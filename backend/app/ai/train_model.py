"""
Training script for the StyleSense clothing classifier.

Uses MobileNetV2 with transfer learning to train a 10-class clothing classifier.

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
         t-shirt/     (10+ images)
         ... etc.

  2. Run:
     python -m app.ai.train_model

  3. The trained model will be saved to app/ai/clothing_model.h5
     The detector will automatically use it on next server start.
"""

import os
import sys
from pathlib import Path

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import ImageDataGenerator

IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 10
MODEL_PATH = Path(__file__).parent / "clothing_model.h5"


def train(train_dir: str = "dataset/train", val_dir: str = "dataset/val"):
    """Train the clothing classification model."""

    if not Path(train_dir).exists():
        print(f"❌ Training directory not found: {train_dir}")
        print("Please organize your images as described at the top of this file.")
        sys.exit(1)

    print("🧠 Building MobileNetV2 transfer learning model...")

    # Base model — frozen pretrained features
    base_model = MobileNetV2(
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
        include_top=False,
        weights="imagenet",
    )
    base_model.trainable = False

    # Classification head
    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.3),
        layers.Dense(128, activation="relu"),
        layers.Dropout(0.2),
        layers.Dense(10, activation="softmax"),
    ])

    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    model.summary()

    # Data generators with augmentation for training
    train_gen = ImageDataGenerator(
        rescale=1.0 / 255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        zoom_range=0.15,
        fill_mode="nearest",
    ).flow_from_directory(
        train_dir,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode="categorical",
    )

    val_gen = None
    if Path(val_dir).exists():
        val_gen = ImageDataGenerator(
            rescale=1.0 / 255,
        ).flow_from_directory(
            val_dir,
            target_size=(IMG_SIZE, IMG_SIZE),
            batch_size=BATCH_SIZE,
            class_mode="categorical",
        )

    print(f"\n📊 Classes found: {train_gen.class_indices}")
    print(f"📁 Training samples: {train_gen.samples}")
    if val_gen:
        print(f"📁 Validation samples: {val_gen.samples}")

    # Train
    print(f"\n🚀 Training for {EPOCHS} epochs...")
    history = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=EPOCHS,
        callbacks=[
            tf.keras.callbacks.EarlyStopping(
                patience=3, restore_best_weights=True
            ),
        ],
    )

    # Save
    model.save(str(MODEL_PATH))
    print(f"\n✅ Model saved to {MODEL_PATH}")
    print(f"📈 Final accuracy: {history.history['accuracy'][-1]:.2%}")
    if val_gen:
        print(f"📈 Final val accuracy: {history.history['val_accuracy'][-1]:.2%}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Train StyleSense clothing classifier")
    parser.add_argument("--train-dir", default="dataset/train", help="Training data directory")
    parser.add_argument("--val-dir", default="dataset/val", help="Validation data directory")
    parser.add_argument("--epochs", type=int, default=EPOCHS, help="Number of epochs")
    args = parser.parse_args()

    EPOCHS = args.epochs
    train(args.train_dir, args.val_dir)
