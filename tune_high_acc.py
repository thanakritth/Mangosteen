import json

with open('C:/AlahiMangosteen/COE67_312_Model_Training.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Step 2: BATCH_SIZE = 8
for cell in nb['cells']:
    if cell['cell_type'] == 'code' and 'BATCH_SIZE =' in ''.join(cell['source']):
        new_source = []
        for line in cell['source']:
            if 'BATCH_SIZE =' in line:
                new_source.append('BATCH_SIZE = 8\n')
            else:
                new_source.append(line)
        cell['source'] = new_source

# Step 3: Square root class weights
for cell in nb['cells']:
    if cell['cell_type'] == 'code' and 'class_weight_dict =' in ''.join(cell['source']):
        new_source = []
        for line in cell['source']:
            if 'class_weight_dict = {' in line:
                new_source.append("class_weight_dict = {i: float(np.sqrt(class_weights_arr[i])) for i in range(len(CLASSES))}\n")
            else:
                new_source.append(line)
        cell['source'] = new_source

# Step 4: 5x5 Color Conv + Separable CNN (~36k params)
step4_code = [
    "# === Optimized Architecture: 5x5 Color-Patch Conv + Separable Feature Hierarchy ===\n",
    "data_augmentation = keras.Sequential([\n",
    "    layers.RandomFlip(\"horizontal_and_vertical\"),\n",
    "    layers.RandomRotation(0.5),\n",
    "    layers.RandomZoom(0.1),\n",
    "    layers.RandomTranslation(0.08, 0.08)\n",
    "], name=\"data_augmentation\")\n",
    "\n",
    "def create_optimized_cnn():\n",
    "    inputs = keras.Input(shape=(96, 96, 3), name=\"input_image\")\n",
    "    \n",
    "    x = data_augmentation(inputs)\n",
    "    x = layers.Rescaling(1.0 / 255.0)(x)\n",
    "    \n",
    "    # Stage 1: 5x5 filter captures broad color patterns of mangosteen skin\n",
    "    x = layers.Conv2D(32, (5, 5), padding='same', activation='relu')(x)\n",
    "    x = layers.MaxPooling2D((2, 2))(x)  # 48x48\n",
    "    \n",
    "    # Stage 2: 48x48 -> 24x24\n",
    "    x = layers.SeparableConv2D(48, (3, 3), padding='same', activation='relu')(x)\n",
    "    x = layers.MaxPooling2D((2, 2))(x)  # 24x24\n",
    "    \n",
    "    # Stage 3: 24x24 -> 12x12\n",
    "    x = layers.SeparableConv2D(64, (3, 3), padding='same', activation='relu')(x)\n",
    "    x = layers.MaxPooling2D((2, 2))(x)  # 12x12\n",
    "    \n",
    "    # Stage 4: 12x12 -> 6x6\n",
    "    x = layers.SeparableConv2D(96, (3, 3), padding='same', activation='relu')(x)\n",
    "    x = layers.MaxPooling2D((2, 2))(x)  # 6x6\n",
    "    \n",
    "    # Stage 5: Deep features\n",
    "    x = layers.SeparableConv2D(128, (3, 3), padding='same', activation='relu')(x)\n",
    "    \n",
    "    # Head\n",
    "    x = layers.GlobalAveragePooling2D()(x)\n",
    "    x = layers.Dropout(0.25)(x)\n",
    "    x = layers.Dense(64, activation='relu')(x)\n",
    "    outputs = layers.Dense(3, activation='softmax', name=\"prediction\")(x)\n",
    "    \n",
    "    model = keras.Model(inputs=inputs, outputs=outputs, name=\"Mangosteen_Optimized_CNN\")\n",
    "    return model\n",
    "\n",
    "model = create_optimized_cnn()\n",
    "model.summary()\n",
    "\n",
    "param_count = model.count_params()\n",
    "print(f\"\\n Total Parameters: {param_count:,}\")\n",
    "if param_count <= 100000:\n",
    "    print(\" PASS: Parameters strictly <= 100,000!\")\n",
    "else:\n",
    "    raise ValueError(f\"FAIL: Exceeds 100,000 limit!\")"
]

# Step 5: Smooth training, preserving learning rate
step5_code = [
    "optimizer = keras.optimizers.Adam(learning_rate=8e-4)\n",
    "loss_fn = keras.losses.CategoricalCrossentropy(label_smoothing=0.05)\n",
    "\n",
    "model.compile(\n",
    "    optimizer=optimizer,\n",
    "    loss=loss_fn,\n",
    "    metrics=['accuracy']\n",
    ")\n",
    "\n",
    "callbacks = [\n",
    "    # Save the model weights that gave the HIGHEST val_accuracy\n",
    "    keras.callbacks.ModelCheckpoint('best_mangosteen_model.keras', monitor='val_accuracy', mode='max', save_best_only=True, verbose=1),\n",
    "    # Gentle learning rate decay without prematurely choking the network\n",
    "    keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.7, patience=8, min_lr=1e-5, verbose=1),\n",
    "    keras.callbacks.EarlyStopping(monitor='val_accuracy', patience=35, restore_best_weights=True, verbose=1)\n",
    "]\n",
    "\n",
    "EPOCHS = 80\n",
    "print(\"Starting training for high accuracy...\")\n",
    "history = model.fit(\n",
    "    train_ds,\n",
    "    validation_data=val_ds,\n",
    "    epochs=EPOCHS,\n",
    "    class_weight=class_weight_dict,\n",
    "    callbacks=callbacks\n",
    ")\n",
    "\n",
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

print('UPDATED_NOTEBOOK_PERFECTLY')
