# Sistema de Monitoramento de Ultrafreezer com Docker e ESP32

Este projeto implementa uma solução completa de Internet das Coisas (IoT) para o monitoramento em tempo real de um ultrafreezer simulado. Ele utiliza um ESP32 (simulado no Wokwi) para coletar dados de sensores, Docker para orquestrar os serviços de backend, InfluxDB como banco de dados de séries temporais e Grafana para visualização dos dados em dashboards interativos.

---

## Arquitetura do Sistema

A solução é composta pelos seguintes componentes:

1.  **Coleta de Dados (Duas Opções):**
    * **Hardware Real (ESP32):** Um microcontrolador ESP32, simulado no ambiente Wokwi, lê os dados de sensores de temperatura e energia e os envia via MQTT.
    * **Simulador Python (`simulador.py`):** Um script Python que roda em um contêiner Docker e gera dados aleatórios, seguindo o mesmo formato do ESP32. É ideal para testar o backend (subscriber, InfluxDB e Grafana) sem a necessidade do hardware físico. Quando usado, sobrescreve os dados da ESP32, sendo que deve ser parado quando for usado o Wokwi.

2.  **Broker MQTT:** Um broker público (`mqtt.eclipseprojects.io`) atua como intermediário, recebendo os dados do ESP32 ou do simulador e distribuindo-os para os clientes inscritos.

3.  **Backend Dockerizado:** Um ambiente Docker orquestrado pelo `docker-compose.yml` executa os seguintes serviços:
    * **Subscriber (`subscriber.py`):** Um script Python que se inscreve no tópico MQTT, recebe os dados dos sensores e os grava no banco de dados InfluxDB.
    * **InfluxDB:** Um banco de dados de alta performance, otimizado para armazenar dados de séries temporais.
    * **Grafana:** Uma plataforma de visualização que se conecta ao InfluxDB para criar dashboards interativos.

---

## Estrutura dos Arquivos

Para que o projeto funcione corretamente, o cliente deve receber os arquivos organizados na seguinte estrutura:

```
/projeto_unificado/
|
+-- docker-compose.yml
+-- simulador_py/
|   |-- Dockerfile
|   +-- simulador.py
|   +-- requirements.txt
+-- subscriber_py/
    |-- Dockerfile
    +-- subscriber.py
    +-- requirements.txt
```

---

## Guia de Instalação e Execução

Siga este passo a passo para configurar e executar o sistema do zero.

### Passo 1: Instalar o Docker Desktop (Pré-requisito Essencial)

1.  **Baixe o Docker Desktop:** Acesse o site oficial do Docker em [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/) e baixe o instalador para o seu sistema operacional.
2.  **Instale e Inicie o Docker Desktop:** Execute o instalador e, após a conclusão, inicie o aplicativo. É fundamental que o Docker Desktop esteja em execução antes de prosseguir.

### Passo 2: Iniciar os Serviços da Aplicação

1.  Descompacte a pasta do projeto em um local de fácil acesso.
2.  Abra um terminal (PowerShell, CMD, etc.) na pasta do projeto.
3.  Execute o seguinte comando para construir e iniciar todos os serviços:
    ```bash
    docker-compose up -d --build
    ```
    Aguarde alguns minutos. O primeiro download pode demorar um pouco.

### Passo 3: Configuração do InfluxDB e do Token de Acesso

Esta etapa só precisa ser realizada uma única vez.

1.  **Acesse a Interface Web do InfluxDB:** Abra seu navegador e vá para `http://localhost:8086`.
2.  **Execute o Setup Inicial:**
    * Clique em **"Get Started"**.
    * Preencha o formulário com um usuário e senha.
    * Use **obrigatoriamente** `minha_org` como **Initial Organization Name** e `iot_bucket` como **Initial Bucket Name**.
3.  **Obtenha e Configure o Token:**
    * O InfluxDB exibirá seu **API Token**. Copie este token.
    * Abra o arquivo `subscriber_py/subscriber.py` em um editor de texto.
    * Localize a linha `INFLUXDB_TOKEN = "..."` e cole o seu token entre as aspas.
    * Salve o arquivo.
4.  **Reinicie e Reconstrua o Serviço:** Volte ao seu terminal e execute o comando abaixo para aplicar a mudança do token.
    ```bash
    docker-compose up -d --build --force-recreate subscriber
    ```

### Passo 4: Configurar o Grafana

1.  Acesse a interface do Grafana em `http://localhost:3000`.
2.  Faça login com as credenciais padrão (`admin` / `admin`) e defina uma nova senha.
3.  **Adicionar o InfluxDB como Fonte de Dados:**
    * No menu, vá para **Connections > Data sources > Add new data source** e selecione **InfluxDB**.
    * Preencha os campos:
        * **Query Language**: `Flux`
        * **URL**: `http://influxdb:8086`
        * **Organization**: `minha_org`
        * **Token**: Cole o mesmo token do InfluxDB que você usou no Passo 3.
        * **Default Bucket**: `iot_bucket`
    * Clique em **"Save & test"**.

4.  **Criar os Dashboards:**
    * No menu lateral, clique no ícone de quatro quadrados (**Dashboards**), depois em **"New"** e **"New Dashboard"**.
    * Clique em **"+ Add visualization"** para criar cada painel.

    ---
    #### **Painel 1: Temperatura do Freezer**
    1.  **Data Source:** Selecione "InfluxDB".
    2.  **Consulta Flux:**
        ```flux
        from(bucket: "iot_bucket")
          |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
          |> filter(fn: (r) => r["_measurement"] == "dados_sensores")
          |> filter(fn: (r) => r["_field"] == "temperatura_freezer")
          |> yield(name: "Temperatura Freezer")
        ```
    3.  **Opções do Painel:**
        * **Title:** `Temperatura do Freezer`
        * **Unit:** `Temperature > Celsius (°C)`
    4.  Clique em **"Apply"**.

    ---
    #### **Painel 2: Temperatura Ambiente**
    1.  **Data Source:** Selecione "InfluxDB".
    2.  **Consulta Flux:**
        ```flux
        from(bucket: "iot_bucket")
          |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
          |> filter(fn: (r) => r["_measurement"] == "dados_sensores")
          |> filter(fn: (r) => r["_field"] == "temperatura_ambiente")
          |> yield(name: "Temperatura Ambiente")
        ```
    3.  **Opções do Painel:**
        * **Title:** `Temperatura Ambiente`
        * **Unit:** `Temperature > Celsius (°C)`
    4.  Clique em **"Apply"**.

    ---
    #### **Painel 3: Status da Energia**
    1.  **Data Source:** Selecione "InfluxDB".
    2.  **Consulta Flux:**
        ```flux
        from(bucket: "iot_bucket")
          |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
          |> filter(fn: (r) => r["_measurement"] == "dados_sensores")
          |> filter(fn: (r) => r["_field"] == "status_energia")
          |> yield(name: "Status Energia")
        ```
    3.  **Opções do Painel:**
        * **Visualization:** `State timeline`
        * **Title:** `Status da Energia`
    4.  **Value Mappings:**
        * **Regra 1:** `Value`: `1`, `Display text`: `Ligado`, `Color`: `green`.
        * **Regra 2:** `Value`: `0`, `Display text`: `Desligado`, `Color`: `red`.
    5.  Clique em **"Apply"**.

    ---
    * Após criar os três painéis, clique no ícone de disquete (💾) no canto superior direito para **salvar o dashboard**.

### Passo 5: Rodar o Firmware do ESP32

1.  Acesse o [Wokwi](https://wokwi.com/) e configure o projeto com os arquivos `sketch.ino` e `diagram.json` fornecidos.
2.  Inicie a simulação. O ESP32 começará a enviar dados que aparecerão no seu dashboard do Grafana.
3.  **Importante:** Pare o contêiner do simulador (`docker stop python_simulator`) para não sobrepor os dados do ESP32.

---

## Solução de Problemas (Troubleshooting)

**Erro no Windows: `open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.`**

* **Causa:** Este erro significa que o Docker Desktop não está em execução ou não iniciou corretamente.
* **Solução:**
    1.  Abra o aplicativo "Docker Desktop" pelo Menu Iniciar.
    2.  Aguarde o ícone do Docker na bandeja do sistema ficar estável.
    3.  Feche seu terminal e abra um novo.
    4.  Navegue até a pasta do projeto e execute o comando `docker-compose up -d --build` novamente.
