# Script to upgrade notebook for Maximum Accuracy Competition
import json

with open('C:/AlahiMangosteen/COE67_312_Model_Training.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Step 4: High Accuracy Architecture (< 35k params, 5-stage feature extraction, 1x1 color transform)
step4_code = [
    "# === Competition-Grade High Accuracy Architecture (Under 35k Params) ===\n",
    "# 1. Geometric Augmentation only (Preserve authentic fruit color!)\n",
    "data_augmentation = keras.Sequential([\n",
    "    layers.RandomFlip(\"horizontal_and_vertical\"),\n",
    "    layers.RandomRotation(0.5), # Mangosteen is round, rotation-invariant\n",
    "    layers.RandomZoom(0.1),\n",
    "    layers.RandomTranslation(0.08, 0.08)\n",
    "], name=\"data_augmentation\")\n",
    "\n",
    "def create_competition_cnn():\n",
    "    inputs = keras.Input(shape=(96, 96, 3), name=\"input_image\")\n",
    "    \n",
    "    x = data_augmentation(inputs)\n",
    "    x = layers.Rescaling(1.0 / 255.0)(x)\n",
    "    \n",
    "    # Stage 0: 1x1 Trainable Color Transform (Extracts optimal ripeness color filters from RGB)\n",
    "    x = layers.Conv2D(16, (1, 1), padding='same', activation='relu')(x)\n",
    "    \n",
    "    # Stage 1: 96x96 -> 48x48 (Edge & Texture)\n",
    "    x = layers.Conv2D(24, (3, 3), padding='same', activation='relu')(x)\n",
    "    x = layers.MaxPooling2D((2, 2))(x)\n",
    "    \n",
    "    # Stage 2: 48x48 -> 24x24 (Separable Conv for rich features without parameter explosion)\n",
    "    x = layers.SeparableConv2D(48, (3, 3), padding='same', activation='relu')(x)\n",
    "    x = layers.MaxPooling2D((2, 2))(x)\n",
    "    \n",
    "    # Stage 3: 24x24 -> 12x12\n",
    "    x = layers.SeparableConv2D(64, (3, 3), padding='same', activation='relu')(x)\n",
    "    x = layers.MaxPooling2D((2, 2))(x)\n",
    "    \n",
    "    # Stage 4: 12x12 -> 6x6\n",
    "    x = layers.SeparableConv2D(96, (3, 3), padding='same', activation='relu')(x)\n",
    "    x = layers.MaxPooling2D((2, 2))(x)\n",
    "    \n",
    "    # Stage 5: 6x6 (Deep ripeness pattern extraction)\n",
    "    x = layers.SeparableConv2D(128, (3, 3), padding='same', activation='relu')(x)\n",
    "    \n",
    "    # Head: Global Average Pooling (immune to position shift, zero dense params)\n",
    "    x = layers.GlobalAveragePooling2D()(x)\n",
    "    x = layers.Dropout(0.35)(x)\n",
    "    x = layers.Dense(32, activation='relu')(x)\n",
    "    outputs = layers.Dense(3, activation='softmax', name=\"prediction\")(x)\n",
    "    \n",
    "    model = keras.Model(inputs=inputs, outputs=outputs, name=\"Mangosteen_HighAccuracy_CNN\")\n",
    "    return model\n",
    "\n",
    "model = create_competition_cnn()\n",
    "model.summary()\n",
    "\n",
    "param_count = model.count_params()\n",
    "print(f\"\\n Total Parameters: {param_count:,}\")\n",
    "if param_count <= 100000:\n",
    "    print(\" PASS: Strictly <= 100,000 parameters requirement!\")\n",
    "else:\n",
    "    raise ValueError(f\"FAIL: Exceeds 100,000 limit!\")"
]

# Step 5: Label Smoothing + Cosine Annealing Learning Rate + ModelCheckpoint
step5_code = [
    "# === Competition Training Setup: Cosine Decay + Label Smoothing + Best Weight Checkpoint ===\n",
    "EPOCHS = 90\n",
    "\n",
    "# Cosine Annealing Learning Rate Schedule for optimal smooth convergence\n",
    "lr_schedule = keras.optimizers.schedules.CosineDecay(\n",
    "    initial_learning_rate=1e-3,\n",
    "    decay_steps=EPOCHS * len(train_ds),\n",
    "    alpha=0.01\n",
    ")\n",
    "\n",
    "optimizer = keras.optimizers.Adam(learning_rate=lr_schedule)\n",
    "\n",
    "# Label smoothing = 0.1 prevents overconfidence on the majority class (unripe)\n",
    "loss_fn = keras.losses.CategoricalCrossentropy(label_smoothing=0.1)\n",
    "\n",
    "model.compile(\n",
    "    optimizer=optimizer,\n",
    "    loss=loss_fn,\n",
    "    metrics=['accuracy']\n",
    ")\n",
    "\n",
    "# Checkpoint automatically saves the model weights that gave the HIGHEST val_accuracy\n",
    "checkpoint_cb = keras.callbacks.ModelCheckpoint(\n",
    "    'best_mangosteen_model.keras',\n",
    "    monitor='val_accuracy',\n",
    "    mode='max',\n",
    "    save_best_only=True,\n",
    "    verbose=1\n",
    ")\n",
    "\n",
    "print(\"Starting high-accuracy training...\")\n",
    "history = model.fit(\n",
    "    train_ds,\n",
    "    validation_data=val_ds,\n",
    "    epochs=EPOCHS,\n",
    "    class_weight=class_weight_dict,\n",
    "    callbacks=[checkpoint_cb]\n",
    ")\n",
    "\n",
    "# Load the best weights achieved during the entire training run\n",
    "model.load_weights('best_mangosteen_model.keras')\n",
    "print(\"\\n Loaded best model weights (highest Val Accuracy)!\")"
]

for cell in nb['cells']:
    if cell['cell_type'] == 'code' and 'create_' in ''.join(cell['source']):
        cell['source'] = step4_code
    if cell['cell_type'] == 'code' and 'optimizer = keras.optimizers.Adam' in ''.join(cell['source']):
        cell['source'] = step5_code

with open('C:/AlahiMangosteen/COE67_312_Model_Training.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print('UPGRADE_COMPLETED')
