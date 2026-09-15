#ifndef MANGOSTEEN_INFER_H_
#define MANGOSTEEN_INFER_H_

#include <Arduino.h>
#include "esp_camera.h"
#include "img_converters.h"
#include "model_data.h"

#include <TensorFlowLite_ESP32.h>
#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_error_reporter.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/schema/schema_generated.h"

// 512 KB Tensor Arena (Allocated in PSRAM, requested ~368 KB)
constexpr int kTensorArenaSize = 512 * 1024;
static uint8_t *tensor_arena = nullptr;

static const tflite::Model *model = nullptr;
static tflite::MicroInterpreter *interpreter = nullptr;
static TfLiteTensor *input_tensor = nullptr;
static TfLiteTensor *output_tensor = nullptr;
static tflite::MicroErrorReporter micro_error_reporter;
static tflite::AllOpsResolver resolver;

struct MangosteenResult {
    float unripe_pct;
    float ripe_pct;
    float overripe_pct;
    const char *label;
    float confidence;
    uint32_t latency_ms;
    bool success;
};

// Initialize TensorFlow Lite Micro with the model from model_data.h
bool initMangosteenModel() {
    Serial.println("[AI] Initializing TensorFlow Lite Micro...");

    model = tflite::GetModel(g_mangosteen_model);
    if (model->version() != TFLITE_SCHEMA_VERSION) {
        Serial.printf("[AI ERROR] Model schema mismatch! Expected %d, got %d\n",
                      TFLITE_SCHEMA_VERSION, model->version());
        return false;
    }

    if (!tensor_arena) {
        if (psramFound()) {
            tensor_arena = (uint8_t *)ps_malloc(kTensorArenaSize);
            Serial.println("[AI] Allocated Tensor Arena in PSRAM.");
        } else {
            tensor_arena = (uint8_t *)malloc(kTensorArenaSize);
            Serial.println("[AI] Allocated Tensor Arena in internal RAM.");
        }
    }
    if (!tensor_arena) {
        Serial.println("[AI ERROR] Failed to allocate Tensor Arena memory!");
        return false;
    }

    static tflite::MicroInterpreter static_interpreter(
        model, resolver, tensor_arena, kTensorArenaSize, &micro_error_reporter);
    interpreter = &static_interpreter;

    TfLiteStatus allocate_status = interpreter->AllocateTensors();
    if (allocate_status != kTfLiteOk) {
        Serial.println("[AI ERROR] AllocateTensors() failed!");
        return false;
    }

    input_tensor = interpreter->input(0);
    output_tensor = interpreter->output(0);

    Serial.printf("[AI] Model ready! Arena used: %d bytes\n", interpreter->arena_used_bytes());
    Serial.printf("[AI] Input tensor: %d x %d x %d\n",
                  input_tensor->dims->data[1],
                  input_tensor->dims->data[2],
                  input_tensor->dims->data[3]);
    return true;
}

// Preprocess camera frame (Center Crop & Resize to 96x96) and run Inference
MangosteenResult classifyMangosteen(camera_fb_t *fb) {
    MangosteenResult res = {0.0f, 0.0f, 0.0f, "Unknown", 0.0f, 0, false};

    if (!interpreter || !input_tensor || !fb) {
        Serial.println("[AI ERROR] Interpreter or frame buffer not ready!");
        return res;
    }

    // Step 1: Decode Frame into RGB888 buffer
    size_t rgb_size = fb->width * fb->height * 3;
    uint8_t *rgb888_buf = (uint8_t *)(psramFound() ? ps_malloc(rgb_size) : malloc(rgb_size));
    if (!rgb888_buf) {
        Serial.println("[AI ERROR] Out of memory for RGB888 conversion!");
        return res;
    }

    bool converted = fmt2rgb888(fb->buf, fb->len, fb->format, rgb888_buf);
    if (!converted) {
        Serial.println("[AI ERROR] fmt2rgb888 failed!");
        free(rgb888_buf);
        return res;
    }

    // Step 2: Center-Crop (240x240 from 320x240) and Downsample to 96x96
    int crop_size = (fb->width < fb->height) ? fb->width : fb->height;
    int offset_x = (fb->width - crop_size) / 2;
    int offset_y = (fb->height - crop_size) / 2;

    float in_scale = input_tensor->params.scale;
    int in_zero = input_tensor->params.zero_point;

    // Default int8 quantization for [0, 255] if scale not populated
    if (in_scale == 0.0f) in_scale = 1.0f;

    for (int y = 0; y < 96; y++) {
        int src_y = offset_y + (y * crop_size) / 96;
        for (int x = 0; x < 96; x++) {
            int src_x = offset_x + (x * crop_size) / 96;
            int src_idx = (src_y * fb->width + src_x) * 3;
            int dst_idx = (y * 96 + x) * 3;

            uint8_t r = rgb888_buf[src_idx];
            uint8_t g = rgb888_buf[src_idx + 1];
            uint8_t b = rgb888_buf[src_idx + 2];

            // Quantize to int8: (pixel / scale) + zero_point
            input_tensor->data.int8[dst_idx]     = (int8_t)((float)r / in_scale + in_zero);
            input_tensor->data.int8[dst_idx + 1] = (int8_t)((float)g / in_scale + in_zero);
            input_tensor->data.int8[dst_idx + 2] = (int8_t)((float)b / in_scale + in_zero);
        }
    }

    free(rgb888_buf);

    // Step 3: Run Model Inference & Benchmark Latency
    uint32_t start_time = millis();
    TfLiteStatus invoke_status = interpreter->Invoke();
    res.latency_ms = millis() - start_time;

    if (invoke_status != kTfLiteOk) {
        Serial.println("[AI ERROR] Invoke() failed!");
        return res;
    }

    // Step 4: Dequantize Outputs and Calculate Percentages
    float out_scale = output_tensor->params.scale;
    int out_zero = output_tensor->params.zero_point;
    if (out_scale == 0.0f) out_scale = 1.0f;

    float raw_scores[3];
    for (int i = 0; i < 3; i++) {
        raw_scores[i] = (output_tensor->data.int8[i] - out_zero) * out_scale;
    }

    // Softmax normalization
    float exp_sum = exp(raw_scores[0]) + exp(raw_scores[1]) + exp(raw_scores[2]);
    res.unripe_pct   = (exp(raw_scores[0]) / exp_sum) * 100.0f;
    res.ripe_pct     = (exp(raw_scores[1]) / exp_sum) * 100.0f;
    res.overripe_pct = (exp(raw_scores[2]) / exp_sum) * 100.0f;

    // Pick top class
    if (res.unripe_pct >= res.ripe_pct && res.unripe_pct >= res.overripe_pct) {
        res.label = "Unripe (ดิบ)";
        res.confidence = res.unripe_pct;
    } else if (res.ripe_pct >= res.unripe_pct && res.ripe_pct >= res.overripe_pct) {
        res.label = "Ripe (สุก)";
        res.confidence = res.ripe_pct;
    } else {
        res.label = "Overripe (สุกงอม)";
        res.confidence = res.overripe_pct;
    }

    res.success = true;
    return res;
}

// Pretty printer for Serial Monitor (Matches Mini-Project Benchmark Card)
void printMangosteenResult(const MangosteenResult &res) {
    if (!res.success) return;
    Serial.println("\n==================================================");
    Serial.println("         🥭 MANGOSTEEN RIPENESS AI RESULT        ");
    Serial.println("==================================================");
    Serial.printf("  [1] Unripe    : %6.2f %%\n", res.unripe_pct);
    Serial.printf("  [2] Ripe    : %6.2f %%\n", res.ripe_pct);
    Serial.printf("  [3] Overripe : %6.2f %%\n", res.overripe_pct);
    Serial.println("--------------------------------------------------");
    Serial.printf("  >> PREDICTION : %s (%.1f%%)\n", res.label, res.confidence);
    Serial.printf("  >> LATENCY    : %d ms (%.1f FPS)\n", res.latency_ms, 1000.0f / max((uint32_t)1, res.latency_ms));
    Serial.println("==================================================\n");
}

#endif // MANGOSTEEN_INFER_H_
