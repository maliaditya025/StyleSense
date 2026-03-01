import os
import copy
import time
from pathlib import Path
from collections import Counter

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, WeightedRandomSampler
from torchvision import datasets, transforms, models

# ==========================================
# CONFIGURATION
# ==========================================
BATCH_SIZE = 32
EPOCHS_PHASE1 = 10
EPOCHS_PHASE2 = 15
LEARNING_RATE_PHASE1 = 1e-3
LEARNING_RATE_PHASE2 = 1e-4
PATIENCE = 5
NUM_CLASSES = 10

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset"
TRAIN_DIR = DATASET_DIR / "train"
VAL_DIR = DATASET_DIR / "val"
MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / "clothing_custom.pth"

MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Detect device (Apple Silicon MPS, CUDA, or CPU)
if torch.cuda.is_available():
    device = torch.device("cuda")
elif torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")
print(f"🚀 Using device: {device}")


def get_data_loaders():
    """Builds DataLoaders with advanced augmentation and class balancing."""
    
    # Advanced data augmentation for training
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
        transforms.RandomRotation(15),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        transforms.RandomErasing(p=0.2, scale=(0.02, 0.1), ratio=(0.3, 3.3), value=0),
    ])

    val_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    train_dataset = datasets.ImageFolder(str(TRAIN_DIR), transform=train_transform)
    val_dataset = datasets.ImageFolder(str(VAL_DIR), transform=val_transform)

    # Class weighting for imbalanced datasets
    class_counts = list(Counter(train_dataset.targets).values())
    total_samples = sum(class_counts)
    class_weights = [total_samples / c for c in class_counts]
    sample_weights = [class_weights[t] for t in train_dataset.targets]
    
    sampler = WeightedRandomSampler(weights=sample_weights, num_samples=len(sample_weights), replacement=True)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, sampler=sampler, num_workers=4, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=4, pin_memory=True)

    return train_loader, val_loader, train_dataset.class_to_idx


def build_model():
    """Initialize MobileNetV2 with a custom classification head."""
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)
    
    model.classifier = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(model.last_channel, 256),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(256, NUM_CLASSES)
    )
    return model.to(device)


def train_epoch(model, dataloader, criterion, optimizer):
    model.train()
    running_loss, correct, total = 0.0, 0, 0

    for inputs, labels in dataloader:
        inputs, labels = inputs.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * inputs.size(0)
        _, preds = torch.max(outputs, 1)
        correct += torch.sum(preds == labels.data).item()
        total += labels.size(0)

    return running_loss / total, correct / total


def eval_epoch(model, dataloader, criterion):
    model.eval()
    running_loss, correct, total = 0.0, 0, 0

    with torch.no_grad():
        for inputs, labels in dataloader:
            inputs, labels = inputs.to(device), labels.to(device)

            outputs = model(inputs)
            loss = criterion(outputs, labels)

            running_loss += loss.item() * inputs.size(0)
            _, preds = torch.max(outputs, 1)
            correct += torch.sum(preds == labels.data).item()
            total += labels.size(0)

    return running_loss / total, correct / total


def train_routine(model, train_loader, val_loader, criterion, optimizer, scheduler, epochs, phase_name):
    best_model_wts = copy.deepcopy(model.state_dict())
    best_acc = 0.0
    epochs_no_improve = 0

    print(f"\n--- Starting {phase_name} ---")
    for epoch in range(epochs):
        start_time = time.time()
        
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer)
        val_loss, val_acc = eval_epoch(model, val_loader, criterion)

        scheduler.step()

        epoch_time = time.time() - start_time
        print(f"Epoch {epoch+1}/{epochs} [{epoch_time:.0f}s] - "
              f"Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | "
              f"Val Loss: {val_loss:.4f} Acc: {val_acc:.4f}")

        # Early Stopping and Checkpointing
        if val_acc > best_acc:
            best_acc = val_acc
            best_model_wts = copy.deepcopy(model.state_dict())
            epochs_no_improve = 0
            torch.save(model.state_dict(), MODEL_PATH)
            print(f"🌟 New best model saved! (Val Acc: {best_acc:.4f})")
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= PATIENCE:
                print(f"🛑 Early stopping triggered after {PATIENCE} epochs without improvement.")
                break

    model.load_state_dict(best_model_wts)
    return model


def main():
    if not TRAIN_DIR.exists() or not VAL_DIR.exists():
        print("❌ Dataset not found! Please populate 'dataset/train' and 'dataset/val'.")
        return

    train_loader, val_loader, class_idx = get_data_loaders()
    print(f"📂 Found classes: {class_idx}")
    
    model = build_model()
    criterion = nn.CrossEntropyLoss()

    # ==========================================
    # PHASE 1: Train only the classifier head
    # ==========================================
    print("❄️ Freezing backbone...")
    for param in model.features.parameters():
        param.requires_grad = False
        
    optimizer_ft = optim.AdamW(model.classifier.parameters(), lr=LEARNING_RATE_PHASE1, weight_decay=1e-4)
    scheduler_ft = optim.lr_scheduler.CosineAnnealingLR(optimizer_ft, T_max=EPOCHS_PHASE1)

    model = train_routine(model, train_loader, val_loader, criterion, optimizer_ft, scheduler_ft, EPOCHS_PHASE1, "Phase 1: Classifier Training")

    # ==========================================
    # PHASE 2: Unfreeze last 30% of backbone
    # ==========================================
    print("\n🔥 Unfreezing last 30% of layers for fine-tuning...")
    num_layers = len(list(model.features.children()))
    unfreeze_start = int(num_layers * 0.7)

    for i, child in enumerate(model.features.children()):
        if i >= unfreeze_start:
            for param in child.parameters():
                param.requires_grad = True

    optimizer_ft2 = optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=LEARNING_RATE_PHASE2, weight_decay=1e-4)
    scheduler_ft2 = optim.lr_scheduler.CosineAnnealingLR(optimizer_ft2, T_max=EPOCHS_PHASE2)

    model = train_routine(model, train_loader, val_loader, criterion, optimizer_ft2, scheduler_ft2, EPOCHS_PHASE2, "Phase 2: Fine-Tuning")

    print(f"✅ Training complete. Final model saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()
