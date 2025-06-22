import paho.mqtt.client as mqtt
import time
import json
import random

# --- Configurações do MQTT ---
MQTT_BROKER_HOST = "mqtt.eclipseprojects.io"
MQTT_BROKER_PORT = 1883
# Tópico para os novos dados do ultrafreezer
MQTT_TOPIC = "ucpel/basso/ultrafreezer/dados"
CLIENT_ID = f"python_ultrafreezer_simulator_{random.randint(0, 1000)}"

print("--- Simulador de Ultrafreezer ---")
print(f"Conectando ao Broker MQTT em {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")

def simulate_ultrafreezer_data():
    """
    Simula os dados de um ultrafreezer, incluindo status de energia,
    temperatura interna e temperatura ambiente.
    """
    # Simula o status da energia: 98% de chance de estar ligado (1)
    status_energia = 1 if random.random() > 0.02 else 0

    temperatura_freezer = 0
    # A temperatura do freezer depende do status da energia
    if status_energia == 1:
        # Se ligado, opera em temperatura ultrabaixa
        temperatura_freezer = round(random.uniform(-82.0, -65.0), 2)
    else:
        # Se desligado, a temperatura sobe gradualmente até a ambiente
        temperatura_freezer = round(random.uniform(-64.0, 30.0), 2)

    # Simula a temperatura ambiente
    temperatura_ambiente = round(random.uniform(18.0, 25.0), 2)

    payload = {
        "dispositivo_id": "ultrafreezer_01",
        "timestamp_utc": int(time.time()),
        "temperatura_freezer": temperatura_freezer,
        "temperatura_ambiente": temperatura_ambiente,
        "status_energia": status_energia  # 1 para Ligado, 0 para Desligado
    }
    return json.dumps(payload)

def connect_mqtt():
    """Conecta ao broker MQTT e retorna o cliente."""
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
    try:
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
        print("Conectado com sucesso ao Broker MQTT!")
        return client
    except Exception as e:
        print(f"Falha ao conectar: {e}")
        return None

def publish_data():
    """Inicia a publicação contínua de dados simulados."""
    time.sleep(5)  # Aguarda a rede do container
    mqtt_client = connect_mqtt()
    if not mqtt_client:
        return

    mqtt_client.loop_start()
    
    while True:
        try:
            payload_json = simulate_ultrafreezer_data()
            result = mqtt_client.publish(MQTT_TOPIC, payload_json)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"Publicado em {MQTT_TOPIC}: {payload_json}")
            else:
                print(f"Falha ao publicar, código: {result.rc}")

            time.sleep(10)
        except KeyboardInterrupt:
            print("Simulador interrompido.")
            break
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
            time.sleep(15)

    mqtt_client.loop_stop()
    mqtt_client.disconnect()

if __name__ == '__main__':
    publish_data()
