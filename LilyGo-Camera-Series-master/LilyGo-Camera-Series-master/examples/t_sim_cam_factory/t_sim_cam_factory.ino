#include "FS.h"
#include "HTTPClient.h"
#include "SD.h"
#include "WiFi.h"
#include "config.h"
#include "esp_camera.h"
#include <Arduino.h>
#include <WiFiAP.h>
#include <driver/i2s.h>


#include "mangosteen_infer.h"

HardwareSerial SerialAT(1);
HTTPClient http_client;

void mic_init(void);
void check_sound(void);
void sd_test(void);
void wifi_scan_connect(void);
void pcie_test(void);
void camera_test(void);
void startCameraServer();


void setup()
{
    pinMode(PWR_ON_PIN, OUTPUT);
    digitalWrite(PWR_ON_PIN, HIGH);
    delay(100);
    Serial.begin(115200);
    Serial.println("T-SIMCAM self test");

#ifdef CAM_IR_PIN
    //Teset IR Filter
    pinMode(CAM_IR_PIN, OUTPUT);
    Serial.println("Test IR Filter");
    int i = 3;
    while (i--) {
        digitalWrite(CAM_IR_PIN, 1 - digitalRead(CAM_IR_PIN)); delay(1000);
    }
#endif
    sd_test();
    //pcie_test();
    mic_init();
    wifi_scan_connect();
    delay(2000);
    camera_test();
    
    // Initialize AI Model
    initMangosteenModel();
}

void loop()
{
    // Realtime Mangosteen AI Inference every 2.5 seconds
    static uint32_t last_infer = 0;
    if (millis() - last_infer > 2500) {
        last_infer = millis();
        camera_fb_t *fb = esp_camera_fb_get();
        if (fb) {
            MangosteenResult res = classifyMangosteen(fb);
            printMangosteenResult(res);
            esp_camera_fb_return(fb);
        }
    }
    delay(10);
}

void sd_test(void)
{

    SPI.begin(SD_SCLK_PIN, SD_MISO_PIN, SD_MOSI_PIN, SD_CS_PIN);
    if (!SD.begin(SD_CS_PIN, SPI)) {
        Serial.println("Card Mount Failed");
        return;
    }
    uint8_t cardType = SD.cardType();
    if (cardType == CARD_NONE) {
        Serial.println("No SD card attached");
        return;
    }

    Serial.print("SD Card Type: ");

    if (cardType == CARD_MMC)
        Serial.println("MMC");
    else if (cardType == CARD_SD)
        Serial.println("SDSC");
    else if (cardType == CARD_SDHC)
        Serial.println("SDHC");
    else
        Serial.println("UNKNOWN");

    uint64_t cardSize = SD.cardSize() / (1024 * 1024);
    Serial.printf("SD Card Size: %lluMB\n", cardSize);
    SD.end();
    return;
}

void mic_init(void)
{
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = 44100,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 6,
        .dma_buf_len = 160,
        .use_apll = false,
        .tx_desc_auto_clear = true,
        .fixed_mclk = 0,
        .mclk_multiple = I2S_MCLK_MULTIPLE_256,
        .bits_per_chan = I2S_BITS_PER_CHAN_32BIT,
    };

    i2s_pin_config_t pin_config = {-1};
    pin_config.bck_io_num = MIC_IIS_SCK_PIN;
    pin_config.ws_io_num = MIC_IIS_WS_PIN;
    pin_config.data_in_num = MIC_IIS_DATA_PIN;
    i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
    i2s_set_pin(I2S_NUM_0, &pin_config);
    i2s_zero_dma_buffer(I2S_NUM_0);
}

#define BUFFER_SIZE (4 * 1024)
uint8_t buffer[BUFFER_SIZE] = {0};
const int define_max = 600;
const int define_avg = 150;
const int define_zero = 3900;
String timelong_str = "";
float val_avg = 0;
int16_t val_max = 0;
float val_avg_1 = 0;
int16_t val_max_1 = 0;

float all_val_avg = 0;
int32_t all_val_zero1 = 0;
int32_t all_val_zero2 = 0;
int32_t all_val_zero3 = 0;

int16_t val16 = 0;
uint8_t val1, val2;
uint32_t j = 0;
bool aloud = false;

void check_sound(void)
{
    size_t bytes_read;
    j = j + 1;
    i2s_read(I2S_NUM_0, (char *)buffer, BUFFER_SIZE, &bytes_read, portMAX_DELAY);

    for (int i = 0; i < BUFFER_SIZE / 2; i++) {
        val1 = buffer[i * 2];
        val2 = buffer[i * 2 + 1];
        val16 = val1 + val2 * 256;
        if (val16 > 0) {
            val_avg = val_avg + val16;
            val_max = max(val_max, val16);
        }
        if (val16 < 0) {
            val_avg_1 = val_avg_1 + val16;
            val_max_1 = min(val_max_1, val16);
        }

        all_val_avg = all_val_avg + val16;

        if (abs(val16) >= 20)
            all_val_zero1 = all_val_zero1 + 1;
        if (abs(val16) >= 15)
            all_val_zero2 = all_val_zero2 + 1;
        if (abs(val16) > 5)
            all_val_zero3 = all_val_zero3 + 1;
    }

    if (j % 2 == 0 && j > 0) {
        val_avg = val_avg / BUFFER_SIZE;
        val_avg_1 = val_avg_1 / BUFFER_SIZE;
        all_val_avg = all_val_avg / BUFFER_SIZE;

        if (val_max > define_max && val_avg > define_avg && all_val_zero2 > define_zero)
            aloud = true;
        else
            aloud = false;

        timelong_str = " high_max:" + String(val_max) + " high_avg:" + String(val_avg) + " all_val_zero2:" + String(all_val_zero2);

        if (aloud) {
            timelong_str = timelong_str + " ##### ##### ##### ##### ##### #####";
            Serial.println(timelong_str);
        }

        val_avg = 0;
        val_max = 0;

        val_avg_1 = 0;
        val_max_1 = 0;

        all_val_avg = 0;
        all_val_zero1 = 0;
        all_val_zero2 = 0;
        all_val_zero3 = 0;
    }

}

void wifi_scan_connect(void)
{
    Serial.println("\n[WiFi] Initializing Wi-Fi...");
    WiFi.disconnect(true);
    delay(100);

    // Start SoftAP Hotspot immediately so iPad can connect without delay!
    WiFi.mode(WIFI_MODE_APSTA);
    WiFi.softAP(WIFI_AP_SSID, WIFI_AP_PASSWORD);

    Serial.println("\n=========================================");
    Serial.printf("  Hotspot AP Active: %s\n", WIFI_AP_SSID);
    Serial.printf("  Hotspot Password:  %s\n", WIFI_AP_PASSWORD);
    Serial.print("  Connect iPad & open: http://");
    Serial.println(WiFi.softAPIP());
    Serial.println("=========================================\n");

    // Try connecting to station Wi-Fi if configured, with 4-second timeout (non-blocking)
    if (String(WIFI_SSID) != "" && String(WIFI_SSID) != "NETTEE") {
        Serial.printf("[WiFi] Attempting to connect to STA: %s ...\n", WIFI_SSID);
        WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
        int timeout = 40; // 4 seconds max
        while (WiFi.status() != WL_CONNECTED && timeout > 0) {
            Serial.print(".");
            vTaskDelay(100);
            timeout--;
        }
        if (WiFi.status() == WL_CONNECTED) {
            Serial.println("\n[WiFi] Connected to STA! Local IP: ");
            Serial.println(WiFi.localIP());
        } else {
            Serial.println("\n[WiFi] STA connection timeout. Continuing in Standalone Hotspot mode.");
        }
    } else {
        Serial.println("[WiFi] Running in Standalone Hotspot mode.");
    }
}

void pcie_test(void)
{
    SerialAT.begin(115200, SERIAL_8N1, PCIE_RX_PIN, PCIE_TX_PIN);
    delay(100);
    pinMode(PCIE_PWR_PIN, OUTPUT);
    digitalWrite(PCIE_PWR_PIN, 1);
    delay(500);
    digitalWrite(PCIE_PWR_PIN, 0);
    delay(3000);
    Serial.println("Waking up PCI module");
    do {
        SerialAT.println("AT");
        delay(50);
    } while (!SerialAT.find("OK"));
    Serial.println("The PCI module has been awakened");

    Serial.println("Example Query the SIM card status");
    do {
        SerialAT.println("AT+CPIN?");
        delay(50);
    } while (!SerialAT.find("READY"));
    Serial.println("SIM card has been identified");
}

void camera_test()
{
    Serial.println("Camera init");
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = CAM_Y2_PIN;
    config.pin_d1 = CAM_Y3_PIN;
    config.pin_d2 = CAM_Y4_PIN;
    config.pin_d3 = CAM_Y5_PIN;
    config.pin_d4 = CAM_Y6_PIN;
    config.pin_d5 = CAM_Y7_PIN;
    config.pin_d6 = CAM_Y8_PIN;
    config.pin_d7 = CAM_Y9_PIN;
    config.pin_xclk = CAM_XCLK_PIN;
    config.pin_pclk = CAM_PCLK_PIN;
    config.pin_vsync = CAM_VSYNC_PIN;
    config.pin_href = CAM_HREF_PIN;
    config.pin_sccb_sda = CAM_SIOD_PIN;
    config.pin_sccb_scl = CAM_SIOC_PIN;
    config.pin_pwdn = CAM_PWDN_PIN;
    config.pin_reset = CAM_RESET_PIN;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG; // for streaming
    // config.pixel_format = PIXFORMAT_RGB565; // for face detection/recognition

    // if PSRAM IC present, init with UXGA resolution and higher JPEG quality
    //                      for larger pre-allocated frame buffer.
    if (psramFound()) {
        config.frame_size = FRAMESIZE_UXGA;
        config.jpeg_quality = 10;
        config.fb_count = 2;
    } else {
        config.frame_size = FRAMESIZE_SVGA;
        config.jpeg_quality = 12;
        config.fb_count = 1;
        config.fb_location = CAMERA_FB_IN_DRAM;
    }

#if defined(CAMERA_MODEL_ESP_EYE)
    pinMode(13, INPUT_PULLUP);
    pinMode(14, INPUT_PULLUP);
#endif

    // camera init
    Serial.printf("Camera init");
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Camera init failed with error 0x%x", err);
        return;
    }

    sensor_t *s = esp_camera_sensor_get();
    // initial sensors are flipped vertically and colors are a bit saturated
    if (s->id.PID == OV3660_PID) {
        s->set_vflip(s, 1);       // flip it back
        s->set_brightness(s, 1);  // up the brightness just a bit
        s->set_saturation(s, -2); // lower the saturation
    }
    // drop down frame size for higher initial frame rate
    s->set_framesize(s, FRAMESIZE_QVGA);

#if defined(CAMERA_MODEL_M5STACK_WIDE) || defined(CAMERA_MODEL_M5STACK_ESP32CAM)
    s->set_vflip(s, 1);
    s->set_hmirror(s, 1);
#endif

    WiFi.mode(WIFI_MODE_APSTA);
    WiFi.softAP(WIFI_AP_SSID, WIFI_AP_PASSWORD);

    startCameraServer();
    Serial.println("\n=========================================");
    Serial.println("  CAMERA SERVER READY!");
    Serial.printf("  Connect iPad to:  %s\n", WIFI_AP_SSID);
    Serial.printf("  Wi-Fi Password:   %s\n", WIFI_AP_PASSWORD);
    Serial.print("  Open Safari URL:  http://");
    Serial.println(WiFi.softAPIP());
    Serial.println("=========================================\n");
    // while (!WiFi.softAPgetStationNum()) {
    //     delay(10);
    // }
    // delay(5000);
}
