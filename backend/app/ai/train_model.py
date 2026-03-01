"""
Training script for StyleSense clothing classifier.

Uses PyTorch MobileNetV2 with transfer learning to train a clothing classifier.
Exports the trained model to ONNX for lightweight deployment.

Setup:
  1. Organize images into folders:
     dataset/
       train/
         shirt/       (50+ images)
         t-shirt/     (50+ images)
         pants/       (50+ images)
         jeans/       (50+ images)
         shoes/       (50+ images)
         jacket/      (50+ images)
         dress/       (50+ images)
         accessories/ (50+ images)
         shorts/      (50+ images)
         skirt/       (50+ images)
       val/
         shirt/       (10+ images)
         ... etc.

  2. Run:
     python -m app.ai.train_model

  3. The trained model will be exported to:
     - app/ai/clothing_custom.pth    (PyTorch weights)
     - app/ai/clothing_custom.onnx   (ONNX for deployment)
"""

import os
import sys
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models

IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 10
NUM_CLASSES = 10

CATEGORIES = [
    "accessories", "dress", "jacket", "jeans", "pants",
    "shirt", "shoes", "shorts", "skirt", "t-shirt",
]

MODEL_DIR = Path(__file__).parent
PTH_PATH = MODEL_DIR / "clothing_custom.pth"
ONNX_PATH = MODEL_DIR / "clothing_custom.onnx"

device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")


def build_model(num_classes: int = NUM_CLASSES):
    """Build MobileNetV2 with custom classification head."""
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)

    # Freeze base features
    for param in model.features.parameters():
        param.requires_grad = False

    # Replace classifier
    model.classifier = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(model.last_channel, 256),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(256, num_classes),
    )

    return model.to(device)


def get_data_loaders(train_dir: str, val_dir: str = None):
    """Create training and validation data loaders with augmentation."""

    train_transform = transforms.Compose([
        transforms.Resize((IMG_SIZE + 32, IMG_SIZE + 32)),
        transforms.RandomCrop(IMG_SIZE),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    val_transform = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    train_dataset = datasets.ImageFolder(train_dir, transform=train_transform)
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=2)

    val_loader = None
    if val_dir and Path(val_dir).exists():
        val_dataset = datasets.ImageFolder(val_dir, transform=val_transform)
        val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=2)

    return train_loader, val_loader, train_dataset.class_to_idx


def train(train_dir: str = "dataset/train", val_dir: str = "dataset/val", epochs: int = EPOCHS):
    """Train the clothing classification model."""

    if not Path(train_dir).exists():
        print(f"❌ Training directory not found: {train_dir}")
        print("Please organize your images as described at the top of this file.")
        sys.exit(1)

    print(f"🧠 Building MobileNetV2 (device: {device})...")
    model = build_model()

    train_loader, val_loader, class_map = get_data_loaders(train_dir, val_dir)

    print(f"\n📊 Classes found: {class_map}")
    print(f"📁 Training samples: {len(train_loader.dataset)}")
    if val_loader:
        print(f"📁 Validation samples: {len(val_loader.dataset)}")

    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.classifier.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)

    best_val_acc = 0.0
    patience_count = 0
    patience = 3

    print(f"\n🚀 Training for {epochs} epochs...")

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

        train_acc = correct / total
        avg_loss = running_loss / len(train_loader)

        # Validation
        val_acc = 0.0
        if val_loader:
            model.eval()
            val_correct = 0
            val_total = 0
            with torch.no_grad():
                for images, labels in val_loader:
                    images, labels = images.to(device), labels.to(device)
                    outputs = model(images)
                    _, predicted = torch.max(outputs, 1)
                    val_total += labels.size(0)
                    val_correct += (predicted == labels).sum().item()
            val_acc = val_correct / val_total

            print(f"  Epoch {epoch + 1}/{epochs} — loss: {avg_loss:.4f}  acc: {train_acc:.2%}  val_acc: {val_acc:.2%}")

            # Early stopping
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                patience_count = 0
                # Save best model
                torch.save(model.state_dict(), str(PTH_PATH))
            else:
                patience_count += 1
                if patience_count >= patience:
                    print(f"  ⚡ Early stopping at epoch {epoch + 1}")
                    break
        else:
            print(f"  Epoch {epoch + 1}/{epochs} — loss: {avg_loss:.4f}  acc: {train_acc:.2%}")

        scheduler.step()

    # Save final model
    if not val_loader or best_val_acc == 0:
        torch.save(model.state_dict(), str(PTH_PATH))

    print(f"\n✅ Model saved to {PTH_PATH}")
    print(f"📈 Final accuracy: {train_acc:.2%}")
    if val_loader:
        print(f"📈 Best val accuracy: {best_val_acc:.2%}")

    # Export to ONNX
    print(f"\n📦 Exporting to ONNX...")
    model.eval()
    model = model.to("cpu")
    dummy = torch.randn(1, 3, IMG_SIZE, IMG_SIZE)
    torch.onnx.export(
        model, dummy, str(ONNX_PATH),
        input_names=["input"], output_names=["output"],
        dynamic_axes={"input": {0: "batch"}, "output": {0: "batch"}},
        opset_version=13,
    )
    size_mb = os.path.getsize(ONNX_PATH) / (1024 * 1024)
    print(f"✅ ONNX exported: {ONNX_PATH} ({size_mb:.1f} MB)")

    # Save class mapping
    mapping_path = MODEL_DIR / "class_mapping.txt"
    idx_to_class = {v: k for k, v in class_map.items()}
    with open(mapping_path, "w") as f:
        for i in range(len(idx_to_class)):
            f.write(f"{i}:{idx_to_class[i]}\n")
    print(f"✅ Class mapping saved to {mapping_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Train StyleSense clothing classifier")
    parser.add_argument("--train-dir", default="dataset/train", help="Training data directory")
    parser.add_argument("--val-dir", default="dataset/val", help="Validation data directory")
    parser.add_argument("--epochs", type=int, default=EPOCHS, help="Number of epochs")
    args = parser.parse_args()

    train(args.train_dir, args.val_dir, args.epochs)
