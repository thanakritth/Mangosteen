# Update notebook with improved CNN architecture (no BatchNorm distortion, preserving mangosteen color)
import json

with open('C:/AlahiMangosteen/COE67_312_Model_Training.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Update Step 4 (cell index 7)
new_step4_source = [
    "# Data Augmentation: DO NOT alter brightness/contrast because ripeness depends heavily on COLOR!\n",
    "data_augmentation = keras.Sequential([\n",
    "    layers.RandomFlip(\"horizontal_and_vertical\"),\n",
    "    layers.RandomRotation(0.15),\n",
    "    layers.RandomZoom(0.1)\n",
    "], name=\"data_augmentation\")\n",
    "\n",
    "def create_lightweight_cnn():\n",
    "    inputs = keras.Input(shape=(96, 96, 3), name=\"input_image\")\n",
    "    \n",
    "    x = data_augmentation(inputs)\n",
    "    x = layers.Rescaling(1.0 / 255.0)(x)\n",
    "    \n",
    "    # Block 1 (96x96 -> 48x48)\n",
    "    x = layers.Conv2D(16, (3, 3), padding='same', activation='relu')(x)\n",
    "    x = layers.MaxPooling2D((2, 2))(x)\n",
    "    \n",
    "    # Block 2 (48x48 -> 24x24)\n",
    "    x = layers.Conv2D(32, (3, 3), padding='same', activation='relu')(x)\n",
    "    x = layers.MaxPooling2D((2, 2))(x)\n",
    "    \n",
    "    # Block 3 (24x24 -> 12x12)\n",
    "    x = layers.Conv2D(64, (3, 3), padding='same', activation='relu')(x)\n",
    "    x = layers.MaxPooling2D((2, 2))(x)\n",
    "    \n",
    "    # Block 4 (12x12 -> 6x6)\n",
    "    x = layers.Conv2D(96, (3, 3), padding='same', activation='relu')(x)\n",
    "    x = layers.MaxPooling2D((2, 2))(x)\n",
    "    \n",
    "    # Classification Head (Global Pooling eliminates dense params)\n",
    "    x = layers.GlobalAveragePooling2D()(x)\n",
    "    x = layers.Dropout(0.4)(x)\n",
    "    x = layers.Dense(32, activation='relu')(x)\n",
    "    outputs = layers.Dense(3, activation='softmax', name=\"prediction\")(x)\n",
    "    \n",
    "    model = keras.Model(inputs=inputs, outputs=outputs, name=\"Mangosteen_Edge_CNN\")\n",
    "    return model\n",
    "\n",
    "model = create_lightweight_cnn()\n",
    "model.summary()\n",
    "\n",
    "param_count = model.count_params()\n",
    "print(f\"\\nTotal Parameters: {param_count:,}\")\n",
    "if param_count <= 100000:\n",
    "    print(\" PASS: Model parameters <= 100,000 as required!\")\n",
    "else:\n",
    "    raise ValueError(f\"FAIL: Model has {param_count} parameters, exceeds 100,000 limit!\")"
]

# Update Step 5 (cell index 9)
new_step5_source = [
    "optimizer = keras.optimizers.Adam(learning_rate=5e-4)\n",
    "model.compile(\n",
    "    optimizer=optimizer,\n",
    "    loss='categorical_crossentropy',\n",
    "    metrics=['accuracy']\n",
    ")\n",
    "\n",
    "callbacks = [\n",
    "    keras.callbacks.EarlyStopping(monitor='val_accuracy', patience=25, restore_best_weights=True, verbose=1),\n",
    "    keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=6, min_lr=1e-5, verbose=1)\n",
    "]\n",
    "\n",
    "EPOCHS = 80\n",
    "print(\"Starting training with tuned architecture...\")\n",
    "history = model.fit(\n",
    "    train_ds,\n",
    "    validation_data=val_ds,\n",
    "    epochs=EPOCHS,\n",
    "    class_weight=class_weight_dict,\n",
    "    callbacks=callbacks\n",
    ")"
]

# Find cells by searching
for cell in nb['cells']:
    if cell['cell_type'] == 'code' and 'create_lightweight_cnn' in ''.join(cell['source']):
        cell['source'] = new_step4_source
    if cell['cell_type'] == 'code' and 'optimizer = keras.optimizers.Adam' in ''.join(cell['source']):
        cell['source'] = new_step5_source

with open('C:/AlahiMangosteen/COE67_312_Model_Training.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print('UPDATED_NOTEBOOK_SUCCESSFULLY')
