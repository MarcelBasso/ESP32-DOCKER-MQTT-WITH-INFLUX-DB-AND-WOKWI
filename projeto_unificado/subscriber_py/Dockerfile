# Usa uma imagem oficial do Python como base.
FROM python:3.9-slim

# Define o diretório de trabalho dentro do container.
WORKDIR /app

# Copia o arquivo de requisitos para o diretório de trabalho.
COPY requirements.txt .

# Instala as dependências Python (paho-mqtt e influxdb-client).
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto dos arquivos da pasta local (o subscriber.py) para o container.
COPY . .

# Comando que será executado quando o container iniciar.
CMD ["python", "subscriber.py"]
