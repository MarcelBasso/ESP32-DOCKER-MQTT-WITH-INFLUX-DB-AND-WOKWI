# Sistema de Monitoramento de Ultrafreezer com Docker e ESP32

Este projeto implementa uma solução completa de Internet das Coisas (IoT) para o monitoramento em tempo real de um ultrafreezer. Ele utiliza um ESP32 (simulado no Wokwi) para coletar dados de sensores, Docker para orquestrar os serviços de backend, InfluxDB como banco de dados de séries temporais e Grafana para visualização dos dados em dashboards interativos.

---

## Arquitetura do Sistema

A solução é composta pelos seguintes componentes:

1.  **Hardware (ESP32):** Um microcontrolador ESP32, simulado no ambiente Wokwi, lê os dados de três sensores:
    * **Temperatura do Freezer:** Simulada por um termistor NTC.
    * **Temperatura Ambiente:** Simulada por um sensor DHT22.
    * **Status da Energia:** Simulado por um interruptor.
    Os dados são enviados via protocolo MQTT para um broker público.

2.  **Broker MQTT:** Um broker público (`mqtt.eclipseprojects.io`) atua como intermediário, recebendo os dados do ESP32 e distribuindo-os para os clientes inscritos no tópico.

3.  **Backend Dockerizado:** Um ambiente Docker orquestrado pelo `docker-compose.yml` executa os seguintes serviços:
    * **Subscriber (`subscriber.py`):** Um script Python que se inscreve no tópico MQTT, recebe os dados dos sensores e os grava no banco de dados InfluxDB.
    * **InfluxDB:** Um banco de dados de alta performance, otimizado para armazenar dados de séries temporais, como leituras de sensores.
    * **Grafana:** Uma plataforma de visualização que se conecta ao InfluxDB para criar dashboards interativos e em tempo real.

---

## Pré-requisitos

Para executar este projeto, é necessário ter os seguintes softwares instalados na máquina host:

* **Docker:** [Link para Instalação](https://docs.docker.com/engine/install/)
* **Docker Compose:** (geralmente já incluído no Docker Desktop para Windows e Mac) [Link para Instalação](https://docs.docker.com/compose/install/)

---

## Estrutura dos Arquivos

Para que o projeto funcione corretamente, os arquivos devem estar organizados na seguinte estrutura:

seu_projeto/│├── docker-compose.yml        # Arquivo de orquestração do Docker.│├── simulador_py/             # Pasta com o código do simulador Python (opcional).│   ├── Dockerfile│   └── simulador.py│└── subscriber_py/            # Pasta com o código do subscriber Python.├── Dockerfile└── subscriber.py
---

## Guia de Instalação e Execução

Siga este passo a passo para configurar e executar o sistema.

### Passo 1: Iniciar os Serviços Docker

1.  Abra um terminal (ou PowerShell) na pasta raiz do projeto (onde está o arquivo `docker-compose.yml`).
2.  Execute o seguinte comando para construir as imagens e iniciar todos os serviços em segundo plano:

    ```bash
    docker-compose up -d --build
    ```
    Aguarde alguns instantes para que todos os contêineres sejam baixados e iniciados.

### Passo 2: Configuração Inicial do InfluxDB

Esta etapa só precisa ser realizada uma única vez.

1.  Abra seu navegador e acesse a interface do InfluxDB em [http://localhost:8086](http://localhost:8086).
2.  Clique em **"Get Started"**.
3.  Preencha o formulário de configuração com os seguintes dados:
    * **Username**: Crie um nome de usuário (ex: `admin`).
    * **Password**: Crie uma senha segura.
    * **Initial Organization Name**: `minha_org` (Este nome é **obrigatório** para que o sistema funcione).
    * **Initial Bucket Name**: `iot_bucket` (Este nome também é **obrigatório**).
4.  Clique em **"Continue"**.
5.  O InfluxDB exibirá seu **API Token**. **Copie este token** para um local seguro. Ele será usado tanto pelo Grafana quanto pelo nosso script Python.

### Passo 3: Atualizar o Token no Script Subscriber

1.  Abra o arquivo `subscriber.py` na pasta `subscriber_py`.
2.  Localize a linha: `INFLUXDB_TOKEN = "cole_seu_token_aqui"`
3.  Substitua `"cole_seu_token_aqui"` pelo token que você copiou do InfluxDB.
4.  Salve o arquivo.
5.  No terminal, reinicie apenas o serviço do subscriber para que ele utilize o novo token:

    ```bash
    docker-compose restart subscriber
    ```

### Passo 4: Configurar o Grafana

1.  Acesse a interface do Grafana em [http://localhost:3000](http://localhost:3000).
2.  Faça login com as credenciais padrão:
    * **Usuário:** `admin`
    * **Senha:** `admin`
    * O Grafana pedirá que você crie uma nova senha.
3.  **Adicionar o InfluxDB como Fonte de Dados:**
    * No menu lateral, vá para **Connections** > **Data sources**.
    * Clique em **"Add new data source"** e selecione **InfluxDB**.
    * Preencha os campos da seguinte forma:
        * **Query Language**: `Flux`
        * **URL**: `http://influxdb:8086`
        * **Organization**: `minha_org`
        * **Token**: Cole o mesmo token do InfluxDB que você usou no Passo 3.
        * **Default Bucket**: `iot_bucket`
    * Clique em **"Save & test"**. Uma mensagem de sucesso deve aparecer.

4.  **Criar os Dashboards:**
    * Siga as instruções do **Guia - Novos Painéis no Grafana** (fornecido anteriormente) para criar os painéis de visualização para cada sensor.

### Passo 5: Rodar o Firmware do ESP32

1.  Acesse o [Wokwi](https://wokwi.com/).
2.  Crie um novo projeto com um ESP32.
3.  Copie o conteúdo do arquivo `sketch.ino` para a aba de código do Wokwi.
4.  Copie o conteúdo do arquivo `diagram.json` para a aba de diagrama.
5.  Inicie a simulação. O ESP32 irá se conectar à rede e começará a enviar os dados dos sensores virtuais para a plataforma.

Após estes passos, o sistema estará completamente funcional, com os dados do ESP32 sendo exibidos em tempo real nos dashboards do Grafana.
