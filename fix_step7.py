import json

with open('C:/AlahiMangosteen/COE67_312_Model_Training.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Step 7: Keras 3 compatible TFLite Conversion (from_keras_model directly)
step7_code = [
    "# === Step 7: int8 Quantization (Compatible with Keras 3 / TensorFlow 2.x) ===\n",
    "# Representative Dataset for Full Integer Quantization calibration\n",
    "def representative_data_gen():\n",
    "    for images, _ in train_ds.take(20):\n",
    "        for img in images:\n",
    "            # Input shape (1, 96, 96, 3), float32 range [0, 255]\n",
    "            input_tensor = tf.expand_dims(img, 0)\n",
    "            yield [input_tensor]\n",
    "\n",
    "# Convert directly from in-memory Keras model\n",
    "converter = tf.lite.TFLiteConverter.from_keras_model(model)\n",
    "converter.optimizations = [tf.lite.Optimize.DEFAULT]\n",
    "converter.representative_dataset = representative_data_gen\n",
    "converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]\n",
    "converter.inference_input_type = tf.int8\n",
    "converter.inference_output_type = tf.int8\n",
    "\n",
    "tflite_quant_model = converter.convert()\n",
    "\n",
    "tflite_model_file = 'mangosteen_model_int8.tflite'\n",
    "with open(tflite_model_file, 'wb') as f:\n",
    "    f.write(tflite_quant_model)\n",
    "\n",
    "size_kb = len(tflite_quant_model) / 1024.0\n",
    "print(f\" int8 Quantized Model Saved: {tflite_model_file}\")\n",
    "print(f\" Model Size: {size_kb:.2f} KB (Fits easily inside ESP32-S3 Flash!)\")"
]

for cell in nb['cells']:
    if cell['cell_type'] == 'code' and 'converter = tf.lite.TFLiteConverter' in ''.join(cell['source']):
        cell['source'] = step7_code

with open('C:/AlahiMangosteen/COE67_312_Model_Training.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print('STEP_7_UPDATED_SUCCESSFULLY')
