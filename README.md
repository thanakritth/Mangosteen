# 🥭 AIoT Mangosteen Ripeness Detection on ESP32-S3

> **COE67-312 · AI in Embedded Systems · Mini-Project**  
> An Edge AI system for classifying mangosteen ripeness into **Unripe**, **Ripe**, and **Overripe** using a lightweight CNN and TensorFlow Lite Micro on the **LilyGo T-SIMCAM (ESP32-S3)** development board.

---

## 📌 Project Overview (ภาพรวมโปรเจกต์)

โปรเจกต์นี้เป็นการนำโมเดล Deep Learning (CNN) ย่อขนาดและ Quantize ให้อยู่ในรูปแบบ **int8** เพื่อนำไปรันบนอุปกรณ์ประมวลผลขนาดเล็ก (Edge Device) โดยใช้กล้อง **OV2640** จับภาพผลมังคุดแบบสดๆ ทำการย่อ/ครอปภาพเป็น $96 \times 96$ พิกเซล และทำการจำแนกความสุกของมังคุดออกมาทาง **Serial Monitor (UART)** และหน้าต่าง **Web Stream Server**

### ✨ จุดเด่นและข้อกำหนดทางเทคนิค:
* **Target Board:** LilyGo T-SIMCAM (ESP32-S3 Dual-Core @ 240MHz, 16MB Flash, 8MB PSRAM)
* **Camera Sensor:** OV2640 (รองรับความละเอียด QVGA 320x240 / VGA 640x480)
* **Model Parameters:** **~36,659 Parameters** (ผ่านเกณฑ์เข้มงวดของวิชา $\le 100,000$ ตัว)
* **Model Size:** **63.2 KB** (แปลงเป็น C Header Array ในไฟล์ `model_data.h`)
* **Quantization:** int8 Full Integer Quantization (Accuracy Drop $< 2\%$)
* **Target Classes (3 คลาส):**
  1. `Unripe` (มังคุดดิบ - เปลือกเขียว/ขาวอมชมพู)
  2. `Ripe` (มังคุดสุกพอดี - เปลือกแดงอมม่วง)
  3. `Overripe` (มังคุดสุกงอม - เปลือกม่วงเข้มเกือบดำ)

---

## 🗂 โครงสร้างโฟลเดอร์ใน Repository (Project Structure)

```text
├── Dataset/
│   └── MiniProject/
│       └── mangosteen_dataset/      # ชุดข้อมูลมังคุดแบ่ง train / val / test เรียบร้อยแล้ว
├── COE67_312_Data_Preparation.ipynb # Notebook ขั้นตอนที่ 1: Crop ภาพมังคุดและแบ่ง Dataset
├── COE67_312_Model_Training.ipynb   # Notebook ขั้นตอนที่ 2: เทรน CNN + ทำ int8 Quantization
├── model_data.h                     # ไฟล์โมเดลภาษา C++ Byte Array (TFLite Micro)
│
└── LilyGo-Camera-Series-master/     # โค้ดเฟิร์มแวร์ PlatformIO สำหรับบอร์ด ESP32-S3
    └── LilyGo-Camera-Series-master/
        └── examples/
            └── t_sim_cam_factory/   # โฟลเดอร์โปรเจกต์หลักของบอร์ดกล้อง
                ├── platformio.ini   # กำหนดการตั้งค่าบอร์ดและไลบรารี TFLite
                ├── config.h         # ตั้งค่าชื่อและรหัสผ่าน Wi-Fi
                ├── model_data.h     # ไฟล์โมเดล AI ที่โหลดเข้า TFLite Micro
                ├── mangosteen_infer.h # โมดูล AI Inference Engine (Center Crop 96x96 + TFLM)
                └── t_sim_cam_factory.ino # โค้ดหลักของบอร์ด (เชื่อมกล้อง + AI + Web Server)
```

---

## 🚀 วิธีการใช้งานและการส่งต่อให้เพื่อนร่วมทีม (Setup & Guide)

### ส่วนที่ 1: การเทรนโมเดล (หากต้องการเทรนใหม่ หรือปรับปรุงโมเดล)
1. เปิดไฟล์ `COE67_312_Model_Training.ipynb` บน **Google Colab** (ตั้ง Runtime เป็น T4 GPU)
2. วางชุดข้อมูลไว้ที่ Google Drive: `/content/drive/MyDrive/MiniProject/mangosteen_dataset`
3. กด **Runtime $\rightarrow$ Run all**
4. ในขั้นตอนสุดท้าย (Step 9) Colab จะสร้างไฟล์ **`model_data.h`** ให้ดาวน์โหลดลงมาใช้งาน

---

### ส่วนที่ 2: การ Flash เฟิร์มแวร์ลงบอร์ดจริง (Hardware Deployment)

#### 1. ข้อกำหนดก่อนเริ่ม:
* ติดตั้ง **VS Code** พร้อมส่วนขยาย (Extension) **PlatformIO IDE**

#### 2. เปิดโปรเจกต์ใน VS Code:
* เปิด VS Code ไปที่ **File** $\rightarrow$ **Open Folder...**
* เลือกเปิดโฟลเดอร์นี้โดยตรง:
  ```text
  LilyGo-Camera-Series-master/LilyGo-Camera-Series-master/examples/t_sim_cam_factory
  ```

#### 3. ตรวจสอบการตั้งค่า Wi-Fi:
* เปิดไฟล์ `config.h`
* แก้ไข `WIFI_SSID` และ `WIFI_PASSWORD` ให้ตรงกับ Wi-Fi 2.4GHz ที่ใช้งาน (หรือ Hotspot มือถือ):
  ```c
  #define WIFI_SSID        "ชื่อไวไฟของคุณ"
  #define WIFI_PASSWORD    "รหัสผ่านไวไฟของคุณ"
  ```

#### 4. เสียบสายบอร์ดและอัปโหลดโปรแกรม:
1. เสียบสาย USB-C ของบอร์ด LilyGo T-SIMCAM เข้ากับคอมพิวเตอร์
2. **หากกด Upload ไม่ผ่าน (ขึ้นจุด `Connecting......`):**
   * กดปุ่ม **`BOOT`** บนบอร์ดค้างไว้
   * กดปุ่ม **`RST` (Reset)** 1 ครั้งแล้วปล่อย
   * ปล่อยปุ่ม **`BOOT`** (บอร์ดจะเข้าสู่ Download Mode)
3. กดปุ่ม **Upload (`➔`)** ที่แถบสถานะสีน้ำเงินด้านล่างของ VS Code
4. รอจนขึ้นข้อความ **`[SUCCESS]`**

---

### ส่วนที่ 3: การเปิดดูผลลัพธ์การจำแนกมังคุด

#### วิธีที่ 1: ดูผล AI ผ่าน Serial Monitor (ใช้สำหรับส่งงานอาจารย์)
1. คลิกที่ปุ่ม **Serial Monitor (รูปปลั๊กไฟ 🔌)** ด้านล่างสุดของ VS Code (ความเร็ว 115200)
2. ทุกๆ 2.5 วินาที กล้องจะจับภาพและวิเคราะห์ผลลัพธ์แสดงทาง Terminal:
   ```text
   ==================================================
            🥭 MANGOSTEEN RIPENESS AI RESULT        
   ==================================================
     [1] Unripe   (ดิบ)    :  26.54 %
     [2] Ripe     (สุก)    :  38.02 %
     [3] Overripe (สุกงอม) :  35.44 %
   --------------------------------------------------
     >> PREDICTION : Ripe (สุก) (38.0%)
     >> LATENCY    : 18286 ms (0.1 FPS)
   ==================================================
   ```

#### วิธีที่ 2: ดูภาพสตรีมสดจากกล้องบนเบราว์เซอร์
1. ดู IP Address ที่หน้าต่าง Serial Monitor (เช่น `http://192.168.0.xxx` หรือ `http://192.168.4.1`)
2. เปิด Google Chrome / Safari บนมือถือหรือคอมพิวเตอร์ แล้วพิมพ์ IP นั้น
3. เลื่อนลงมาล่างสุด กดปุ่ม **"Start Stream"** เพื่อดูภาพวิดีโอสดจากกล้องได้ทันที!

---

## 📊 ข้อมูลสำหรับทำ Benchmark Card (Module 3 Deliverable)

| รายการ (Metric) | ค่าที่ได้ (Measured Value) | หมายเหตุ / คำอธิบาย |
|---|---|---|
| **Model Parameters** | 36,659 params | ผ่านเกณฑ์ $\le 100,000$ ตัว |
| **Model Flash Footprint** | 63.2 KB (`model_data.h`) | กะทัดรัดมาก ประหยัด Flash |
| **Tensor Arena Size** | 512 KB | จัดสรรบน PSRAM ภายนอก |
| **Target Hardware** | ESP32-S3 (240 MHz) | LilyGo T-SIMCAM V1.3 |
| **Camera Model** | OV2640 | Frame size: QVGA (320x240) |
| **Inference Preprocessing** | Center Crop $240 \times 240 \rightarrow 96 \times 96$ RGB | ตรงกับ Data Prep ใน Colab |

---

## 👥 Authors & Credits
* **Course:** COE67-312 AI in Embedded Systems
* **Repository:** [thanakritth/Mangosteen](https://github.com/thanakritth/Mangosteen)
* **Frameworks & Libs:** TensorFlow / Keras, TensorFlow Lite for Microcontrollers (`tanakamasayuki/TensorFlowLite_ESP32`), ESP32 Arduino Core
