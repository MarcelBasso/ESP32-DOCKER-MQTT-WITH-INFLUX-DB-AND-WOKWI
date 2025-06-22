#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "time.h"
#include <Adafruit_Sensor.h>
#include <DHT.h>

// --- Configurações de Rede e Tempo ---
const char* ssid = "Wokwi-GUEST"; // Rede padrão do Wokwi
const char* password = "";     // Senha padrão do Wokwi
const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = -3 * 3600; // Fuso Horário GMT-3
const int daylightOffset_sec = 0;

// --- Configurações do Broker MQTT ---
const char* mqtt_server = "mqtt.eclipseprojects.io";
const int mqtt_port = 1883;
const char* device_id = "ultrafreezer_esp32_01";

// --- Tópicos MQTT ---
const char* data_topic = "ucpel/basso/ultrafreezer/dados";
const char* lwt_topic = "ucpel/basso/ultrafreezer/status";
const int lwt_qos = 1;
const boolean lwt_retain = false;

// --- Mapeamento de Pinos dos Sensores ---
const int POWER_SWITCH_PIN = 12; // Pino do interruptor de energia
const int NTC_PIN = 34;          // Pino do sensor NTC (freezer)
const int DHT_PIN = 15;          // Pino do sensor DHT22 (ambiente)

// --- Configuração dos Sensores ---
#define DHTTYPE DHT22
DHT dht(DHT_PIN, DHTTYPE);

// --- Intervalo de Leitura e Publicação ---
const long interval = 10000; // Publica a cada 10 segundos
unsigned long previousMillis = 0;

// --- Clientes ---
WiFiClient espClient;
PubSubClient client(espClient);

// --- Protótipos das Funções ---
void setup_wifi();
void reconnect_mqtt();
void publishSensorData();
void callback(char* topic, byte* payload, unsigned int length);
long getUnixTimestamp();
float readNtcTemperature();

// =================================================================
// --- SETUP ---
// =================================================================
void setup() {
    Serial.begin(115200);
    pinMode(POWER_SWITCH_PIN, INPUT);
    dht.begin();

    setup_wifi();
    configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);

    client.setServer(mqtt_server, mqtt_port);
    client.setCallback(callback);
}

// =================================================================
// --- LOOP ---
// =================================================================
void loop() {
    if (!client.connected()) {
        reconnect_mqtt();
    }
    client.loop();

    unsigned long currentMillis = millis();
    if (currentMillis - previousMillis >= interval) {
        previousMillis = currentMillis;
        publishSensorData();
    }
}

// =================================================================
// --- FUNÇÕES ---
// =================================================================

void setup_wifi() {
    delay(10);
    Serial.println("\nConectando via Wokwi WiFi...");
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi conectado!");
    Serial.print("Endereço IP: ");
    Serial.println(WiFi.localIP());
}

void reconnect_mqtt() {
    while (!client.connected()) {
        Serial.print("Tentando conexão MQTT...");
        String clientId = "ESP32-Wokwi-Ultrafreezer-";
        clientId += String(random(0xffff), HEX);

        StaticJsonDocument<128> lwtDoc;
        lwtDoc["dispositivo_id"] = device_id;
        lwtDoc["status"] = "offline";
        char lwtBuffer[128];
        serializeJson(lwtDoc, lwtBuffer);

        if (client.connect(clientId.c_str(), lwt_topic, lwt_qos, lwt_retain, lwtBuffer)) {
            Serial.println("Conectado!");
        } else {
            Serial.print(" falhou, rc=");
            Serial.print(client.state());
            Serial.println(" tentando novamente em 5 segundos");
            delay(5000);
        }
    }
}

void publishSensorData() {
    // 1. Leitura dos sensores
    float temperatura_ambiente = dht.readTemperature();
    float temperatura_freezer = readNtcTemperature();
    int status_energia = digitalRead(POWER_SWITCH_PIN); // HIGH = 1 (Ligado), LOW = 0 (Desligado)

    if (isnan(temperatura_ambiente)) {
        Serial.println("Falha ao ler do sensor DHT!");
        return;
    }

    // 2. Criação do payload JSON
    StaticJsonDocument<256> doc;
    doc["dispositivo_id"] = device_id;
    doc["timestamp_utc"] = getUnixTimestamp();
    doc["temperatura_freezer"] = temperatura_freezer;
    doc["temperatura_ambiente"] = temperatura_ambiente;
    doc["status_energia"] = status_energia;

    char buffer[256];
    size_t n = serializeJson(doc, buffer);

    // 3. Publicação dos dados
    Serial.print("Publicando dados: ");
    Serial.println(buffer);
    client.publish(data_topic, buffer, n);
}

float readNtcTemperature() {
    // Lê o valor analógico do pino do NTC
    int adcValue = analogRead(NTC_PIN);
    
    // Converte o valor do ADC para temperatura.
    // Esta fórmula é específica para o sensor NTC do Wokwi.
    float temperatura = 25.0 - (adcValue - 1850) / 45.0;
    
    // No Wokwi, você pode clicar no sensor NTC e ajustar a temperatura diretamente.
    // A fórmula acima é uma aproximação. Para um sensor real, seria necessária
    // a equação Steinhart-Hart com os coeficientes corretos.
    return temperatura;
}

void callback(char* topic, byte* payload, unsigned int length) {
    // Não é necessário para este projeto.
}

long getUnixTimestamp() {
    time_t now;
    time(&now);
    return now;
}
