import paho.mqtt.client as mqtt
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import json
import time
import random

# --- Configurações ---
MQTT_BROKER_HOST = "mqtt.eclipseprojects.io"
MQTT_BROKER_PORT = 1883
# Tópico para receber os dados do ultrafreezer
MQTT_TOPIC_SUBSCRIBE = "ucpel/basso/ultrafreezer/dados"
CLIENT_ID = f"python_subscriber_{random.randint(0, 1000)}"

INFLUXDB_URL = "http://influxdb:8086"
# !!! ATENÇÃO: SUBSTITUA COM O SEU TOKEN REAL DO INFLUXDB !!!
INFLUXDB_TOKEN = "DICqtzzk5r14Ge5Hf8gL8Hh5XYptz2nqiiOwShigOy7SM5wq9LBzK6eyxGrt7xKw2zTr09VvKllKk19Eh9q9rQ==" 
INFLUXDB_ORG = "minha_org"
INFLUXDB_BUCKET = "iot_bucket"

print("--- Python Subscriber ---")

# Função para criar o cliente do InfluxDB
def get_influx_client():
    if "cole_seu_token_aqui" in INFLUXDB_TOKEN:
        print("ERRO CRÍTICO: O token do InfluxDB não foi definido no script subscriber.py.")
        return None
    try:
        client = influxdb_client.InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        print("Cliente InfluxDB criado com sucesso.")
        return client
    except Exception as e:
        print(f"Falha ao criar o cliente do InfluxDB: {e}")
        return None

# Callback para quando o cliente se conecta ao broker
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(f"Conectado com sucesso ao Broker MQTT. Subscrevendo ao tópico: {MQTT_TOPIC_SUBSCRIBE}")
        client.subscribe(MQTT_TOPIC_SUBSCRIBE)
    else:
        print(f"Falha ao conectar ao MQTT, código de retorno: {reason_code}\n")

# Callback para quando uma mensagem é recebida do broker
def on_message(client, userdata, msg):
    print(f"Mensagem recebida no tópico {msg.topic}: {msg.payload.decode()}")
    try:
        influx_client = get_influx_client()
        if not influx_client:
            print("Não foi possível gravar os dados. Cliente do InfluxDB não está disponível.")
            return

        write_api = influx_client.write_api(write_options=SYNCHRONOUS)
        data = json.loads(msg.payload.decode())

        # Cria o ponto de dados com os novos campos
        point = (
            influxdb_client.Point("dados_sensores")
            .tag("dispositivo_id", data.get("dispositivo_id"))
            .field("temperatura_freezer", float(data.get("temperatura_freezer")))
            .field("temperatura_ambiente", float(data.get("temperatura_ambiente")))
            .field("status_energia", int(data.get("status_energia")))
            .time(int(data.get("timestamp_utc")), "s")
        )

        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
        print(f"Dados do dispositivo '{data.get('dispositivo_id')}' escritos com sucesso no InfluxDB.")

    except Exception as e:
        print(f"Ocorreu um erro ao processar a mensagem: {e}")

def run_subscriber():
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    
    while True:
        try:
            time.sleep(5)
            mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
            mqtt_client.loop_forever()
        except Exception as e:
            print(f"Erro na conexão MQTT: {e}. Tentando novamente em 10s...")
            time.sleep(10)

if __name__ == '__main__':
    run_subscriber()


