#ifndef MANGOSTEEN_INFER_H_
#define MANGOSTEEN_INFER_H_

#include <Arduino.h>
#include "esp_camera.h"

struct MangosteenResult {
    float unripe_pct;
    float ripe_pct;
    float overripe_pct;
    const char *label;
    const char *class_code; // "unripe", "ripe", or "overripe"
    float confidence;
    uint32_t latency_ms;
    bool success;
};

// Initialize TensorFlow Lite Micro with model from model_data.h
bool initMangosteenModel();

// Run on-chip AI inference on a camera frame
MangosteenResult classifyMangosteen(camera_fb_t *fb);

// Print formatted ASCII benchmark table to Serial Monitor
void printMangosteenResult(const MangosteenResult &res);

#endif // MANGOSTEEN_INFER_H_
