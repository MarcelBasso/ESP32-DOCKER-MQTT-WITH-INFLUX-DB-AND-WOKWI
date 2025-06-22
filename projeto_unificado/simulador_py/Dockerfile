# Usa uma imagem oficial do Python como base. A versão slim é menor.
FROM python:3.9-slim

# Define o diretório de trabalho dentro do container.
# Todos os comandos a seguir serão executados a partir daqui.
WORKDIR /app

# Copia o arquivo de requisitos para o diretório de trabalho.
COPY requirements.txt .

# Instala as dependências Python listadas no requirements.txt.
# O '--no-cache-dir' é uma boa prática para manter a imagem pequena.
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto dos arquivos da pasta local (o simulador.py) para o container.
COPY . .

# Comando que será executado quando o container iniciar.
CMD ["python", "simulador.py"]
