#include "mangosteen_infer.h"
#include "img_converters.h"
#include "model_data.h"

#include <TensorFlowLite_ESP32.h>
#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_error_reporter.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/schema/schema_generated.h"
#include <freertos/semphr.h>

// 512 KB Tensor Arena (Allocated in PSRAM)
constexpr int kTensorArenaSize = 512 * 1024;
static uint8_t *tensor_arena = nullptr;

static const tflite::Model *model = nullptr;
static tflite::MicroInterpreter *interpreter = nullptr;
static TfLiteTensor *input_tensor = nullptr;
static TfLiteTensor *output_tensor = nullptr;
static tflite::MicroErrorReporter micro_error_reporter;
static tflite::AllOpsResolver resolver;
static SemaphoreHandle_t ai_mutex = nullptr;

bool initMangosteenModel() {
    Serial.println("[AI] Initializing TensorFlow Lite Micro...");

    if (!ai_mutex) {
        ai_mutex = xSemaphoreCreateMutex();
    }

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
    Serial.printf("[AI] Input tensor: %d x %d x %d (scale=%f, zp=%d)\n",
                  input_tensor->dims->data[1],
                  input_tensor->dims->data[2],
                  input_tensor->dims->data[3],
                  input_tensor->params.scale,
                  input_tensor->params.zero_point);
    Serial.printf("[AI] Output tensor: %d classes (scale=%f, zp=%d)\n",
                  output_tensor->dims->data[1],
                  output_tensor->params.scale,
                  output_tensor->params.zero_point);
    return true;
}

MangosteenResult classifyMangosteen(camera_fb_t *fb) {
    MangosteenResult res = {0.0f, 0.0f, 0.0f, "Unknown", "unripe", 0.0f, 0, false};

    if (!interpreter || !input_tensor || !fb) {
        Serial.println("[AI ERROR] Interpreter or frame buffer not ready!");
        return res;
    }

    if (ai_mutex && xSemaphoreTake(ai_mutex, pdMS_TO_TICKS(3000)) != pdTRUE) {
        Serial.println("[AI ERROR] Semaphore timeout waiting for inference!");
        return res;
    }

    // Step 1: Decode Frame into RGB888 buffer
    size_t rgb_size = fb->width * fb->height * 3;
    uint8_t *rgb888_buf = (uint8_t *)(psramFound() ? ps_malloc(rgb_size) : malloc(rgb_size));
    if (!rgb888_buf) {
        Serial.println("[AI ERROR] Out of memory for RGB888 conversion!");
        if (ai_mutex) xSemaphoreGive(ai_mutex);
        return res;
    }

    bool converted = fmt2rgb888(fb->buf, fb->len, fb->format, rgb888_buf);
    if (!converted) {
        Serial.println("[AI ERROR] fmt2rgb888 failed!");
        free(rgb888_buf);
        if (ai_mutex) xSemaphoreGive(ai_mutex);
        return res;
    }

    // Step 2: Center-Crop and Downsample to 96x96
    int crop_size = (fb->width < fb->height) ? fb->width : fb->height;
    int offset_x = (fb->width - crop_size) / 2;
    int offset_y = (fb->height - crop_size) / 2;

    float in_scale = input_tensor->params.scale;
    int in_zero = input_tensor->params.zero_point;
    if (in_scale == 0.0f) in_scale = 1.0f;

    for (int y = 0; y < 96; y++) {
        int src_y = offset_y + (y * crop_size) / 96;
        for (int x = 0; x < 96; x++) {
            int src_x = offset_x + (x * crop_size) / 96;
            int src_idx = (src_y * fb->width + src_x) * 3;
            int dst_idx = (y * 96 + x) * 3;

            // Note: fmt2rgb888 on ESP32 outputs BGR byte order (buf[0]=B, buf[1]=G, buf[2]=R).
            // Neural network expects standard RGB byte order (R, G, B).
            uint8_t r = rgb888_buf[src_idx + 2]; // Red is at byte 2
            uint8_t g = rgb888_buf[src_idx + 1]; // Green is at byte 1
            uint8_t b = rgb888_buf[src_idx];     // Blue is at byte 0

            // Quantize to int8: (pixel / scale) + zero_point with bounds check
            int q_r = (int)roundf((float)r / in_scale) + in_zero;
            int q_g = (int)roundf((float)g / in_scale) + in_zero;
            int q_b = (int)roundf((float)b / in_scale) + in_zero;

            input_tensor->data.int8[dst_idx]     = (int8_t)constrain(q_r, -128, 127);
            input_tensor->data.int8[dst_idx + 1] = (int8_t)constrain(q_g, -128, 127);
            input_tensor->data.int8[dst_idx + 2] = (int8_t)constrain(q_b, -128, 127);
        }
    }

    free(rgb888_buf);

    // Diagnostic RGB averages
    uint32_t sum_r = 0, sum_g = 0, sum_b = 0;
    for (int i = 0; i < 96 * 96; i++) {
        sum_r += (uint8_t)(input_tensor->data.int8[i * 3] - in_zero);
        sum_g += (uint8_t)(input_tensor->data.int8[i * 3 + 1] - in_zero);
        sum_b += (uint8_t)(input_tensor->data.int8[i * 3 + 2] - in_zero);
    }

    // Step 3: Run Model Inference & Benchmark Latency
    uint32_t start_time = millis();
    TfLiteStatus invoke_status = interpreter->Invoke();
    res.latency_ms = millis() - start_time;

    Serial.printf("[AI DIAG] Center Crop RGB: R=%u, G=%u, B=%u | Raw int8: [%d, %d, %d]\n",
                  sum_r / (96 * 96), sum_g / (96 * 96), sum_b / (96 * 96),
                  output_tensor->data.int8[0],
                  output_tensor->data.int8[1],
                  output_tensor->data.int8[2]);

    if (invoke_status != kTfLiteOk) {
        Serial.println("[AI ERROR] Invoke() failed!");
        if (ai_mutex) xSemaphoreGive(ai_mutex);
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

    // Model in notebook has softmax activation: outputs are probabilities [0, 1]
    float sum_raw = raw_scores[0] + raw_scores[1] + raw_scores[2];
    if (sum_raw > 0.5f && sum_raw < 1.5f && raw_scores[0] >= -0.05f && raw_scores[1] >= -0.05f && raw_scores[2] >= -0.05f) {
        float c0 = max(0.0f, raw_scores[0]);
        float c1 = max(0.0f, raw_scores[1]);
        float c2 = max(0.0f, raw_scores[2]);
        float s = c0 + c1 + c2;
        if (s <= 0.0f) s = 1.0f;
        res.unripe_pct   = (c0 / s) * 100.0f;
        res.ripe_pct     = (c1 / s) * 100.0f;
        res.overripe_pct = (c2 / s) * 100.0f;
    } else {
        // Logits fallback
        float max_val = max(raw_scores[0], max(raw_scores[1], raw_scores[2]));
        float e0 = exp(raw_scores[0] - max_val);
        float e1 = exp(raw_scores[1] - max_val);
        float e2 = exp(raw_scores[2] - max_val);
        float exp_sum = e0 + e1 + e2;
        res.unripe_pct   = (e0 / exp_sum) * 100.0f;
        res.ripe_pct     = (e1 / exp_sum) * 100.0f;
        res.overripe_pct = (e2 / exp_sum) * 100.0f;
    }

    // Pick top class: 0=unripe, 1=ripe, 2=overripe
    if (res.unripe_pct >= res.ripe_pct && res.unripe_pct >= res.overripe_pct) {
        res.label = "Unripe (ดิบ)";
        res.class_code = "unripe";
        res.confidence = res.unripe_pct;
    } else if (res.ripe_pct >= res.unripe_pct && res.ripe_pct >= res.overripe_pct) {
        res.label = "Ripe (สุก)";
        res.class_code = "ripe";
        res.confidence = res.ripe_pct;
    } else {
        res.label = "Overripe (สุกงอม)";
        res.class_code = "overripe";
        res.confidence = res.overripe_pct;
    }

    res.success = true;

    if (ai_mutex) xSemaphoreGive(ai_mutex);
    return res;
}

void printMangosteenResult(const MangosteenResult &res) {
    if (!res.success) return;
    Serial.println("\n==================================================");
    Serial.println("         🥭 MANGOSTEEN RIPENESS AI RESULT        ");
    Serial.println("==================================================");
    Serial.printf("  [1] Unripe    : %6.2f %%\n", res.unripe_pct);
    Serial.printf("  [2] Ripe      : %6.2f %%\n", res.ripe_pct);
    Serial.printf("  [3] Overripe  : %6.2f %%\n", res.overripe_pct);
    Serial.println("--------------------------------------------------");
    Serial.printf("  >> PREDICTION : %s (%.1f%%)\n", res.label, res.confidence);
    Serial.printf("  >> LATENCY    : %d ms (%.1f FPS)\n", res.latency_ms, 1000.0f / max((uint32_t)1, res.latency_ms));
    Serial.println("==================================================\n");
}
