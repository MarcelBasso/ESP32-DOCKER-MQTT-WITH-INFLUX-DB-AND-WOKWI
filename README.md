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

seu_projeto/
├── docker-compose.yml
├── simulador_py/
   │   
   ├── Dockerfile│   
   └── simulador.py
│     
└── subscriber_py/
   ├── Dockerfile
   └── subscriber.py
---

## Guia de Instalação e Execução

Siga este passo a passo para configurar e executar o sistema do zero.

### Passo 1: Instalar o Docker Desktop (Pré-requisito Essencial)

O Docker é a tecnologia que permite que todos os serviços (banco de dados, dashboards, etc.) rodem de forma isolada e padronizada.

1.  **Baixe o Docker Desktop:**
    * Acesse o site oficial do Docker: [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
    * Baixe o instalador apropriado para o seu sistema operacional (Windows ou macOS).

2.  **Instale o Docker Desktop:**
    * Execute o instalador baixado e siga as instruções na tela. A instalação pode exigir que você reinicie o computador.

3.  **Inicie o Docker Desktop:**
    * Após a instalação, procure por "Docker Desktop" no seu Menu Iniciar e abra o aplicativo.
    * **É fundamental que o Docker Desktop esteja em execução** antes de prosseguir para o próximo passo. Aguarde até que o ícone do Docker na bandeja do sistema fique estável (geralmente verde).

### Passo 2: Iniciar os Serviços da Aplicação

Com o Docker em execução, agora vamos iniciar a nossa aplicação.

1.  **Descompacte** e coloque a pasta do projeto (que contém o `docker-compose.yml`) em um local de fácil acesso (ex: `C:\Users\SeuUsuario\Desktop\projeto_ultrafreezer`).
2.  **Abra um terminal** (PowerShell ou Prompt de Comando no Windows) nessa pasta usando `cd C:\Users\SeuUsuario\Desktop\projeto_ultrafreezer`.
3.  Execute o seguinte comando no terminal para construir e iniciar todos os serviços:
    ```bash
    docker-compose up -d --build
    ```
    * **O que este comando faz?** Ele lê o `docker-compose.yml`, baixa as imagens do InfluxDB e Grafana, constrói as imagens para os nossos scripts Python e inicia todos os contêineres em segundo plano.
    * Aguarde alguns minutos. O primeiro download pode demorar um pouco.

### Passo 3: Configuração do InfluxDB e do Token de Acesso

Esta etapa só precisa ser realizada uma única vez.

1.  **Acesse a Interface Web do InfluxDB:**
    * Abra seu navegador e vá para [http://localhost:8086](http://localhost:8086).
2.  **Execute o Setup Inicial:**
    * Clique em **"Get Started"**.
    * Preencha o formulário:
        * **Username**: Crie um nome de usuário (ex: `admin`).
        * **Password**: Crie uma senha segura.
        * **Initial Organization Name**: `minha_org` (Este nome é **obrigatório**).
        * **Initial Bucket Name**: `iot_bucket` (Este nome é **obrigatório**).
    * Clique em **"Continue"**.
3.  **Obtenha e Configure o Token:**
    * O InfluxDB exibirá seu **API Token**. **Copie este token** imediatamente.
    * Abra o arquivo `subscriber.py` (dentro da pasta `subscriber_py`) com um editor de texto.
    * Localize a linha: `INFLUXDB_TOKEN = "..."`
    * Substitua o conteúdo entre as aspas pelo token que você acabou de copiar.
    * Salve o arquivo `subscriber.py`.
4.  **Reinicie o Serviço:**
    * Volte ao seu terminal e execute o comando abaixo para que o `subscriber` use o novo token:
        ```bash
        docker-compose restart subscriber
        ```

### Passo 4: Configurar o Grafana

1.  Acesse a interface do Grafana em [http://localhost:3000](http://localhost:3000).
2.  Faça login com as credenciais padrão (`admin` / `admin`) e defina uma nova senha.
3.  **Adicionar o InfluxDB como Fonte de Dados:**
    * No menu, vá para **Connections** > **Data sources** > **Add new data source** e selecione **InfluxDB**.
    * Preencha os campos:
        * **Query Language**: `Flux`
        * **URL**: `http://influxdb:8086`
        * **Organization**: `minha_org`
        * **Token**: Cole o mesmo token do InfluxDB que você usou no Passo 3.
        * **Default Bucket**: `iot_bucket`
    * Clique em **"Save & test"**. Uma mensagem de sucesso deve aparecer.

4.  **Criar os Dashboards:**
    * No menu lateral, clique no ícone de quatro quadrados (**Dashboards**).
    * Na página de Dashboards, clique em **"New"** e depois em **"New Dashboard"**.
    * Dentro do novo dashboard, clique em **"+ Add visualization"**. Siga as instruções abaixo para cada painel.

    <details>
    <summary><strong>Painel 1: Temperatura do Freezer</strong></summary>

    1.  Na tela de criação, selecione **"InfluxDB"** como a fonte de dados (Data Source).
    2.  Cole a seguinte consulta **Flux** no editor:
        ```flux
        from(bucket: "iot_bucket")
          |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
          |> filter(fn: (r) => r["_measurement"] == "dados_sensores")
          |> filter(fn: (r) => r["_field"] == "temperatura_freezer")
          |> yield(name: "Temperatura Freezer")
        ```
    3.  No painel direito, em "Panel options", defina o **Title** como `Temperatura do Freezer`.
    4.  Em "Standard options", defina a **Unit** como `Temperature > Celsius (°C)`.
    5.  Clique em **"Apply"** para adicionar o painel.
    </details>

    <details>
    <summary><strong>Painel 2: Temperatura Ambiente</strong></summary>

    1.  Clique em "+ Add visualization" novamente.
    2.  Selecione **"InfluxDB"** como a fonte de dados.
    3.  Cole a seguinte consulta **Flux** no editor:
        ```flux
        from(bucket: "iot_bucket")
          |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
          |> filter(fn: (r) => r["_measurement"] == "dados_sensores")
          |> filter(fn: (r) => r["_field"] == "temperatura_ambiente")
          |> yield(name: "Temperatura Ambiente")
        ```
    4.  No painel direito, defina o **Title** como `Temperatura Ambiente` e a **Unit** como `Temperature > Celsius (°C)`.
    5.  Clique em **"Apply"**.
    </details>

    <details>
    <summary><strong>Painel 3: Status da Energia</strong></summary>

    1.  Clique em "+ Add visualization".
    2.  Selecione **"InfluxDB"** como a fonte de dados.
    3.  Cole a seguinte consulta **Flux**:
        ```flux
        from(bucket: "iot_bucket")
          |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
          |> filter(fn: (r) => r["_measurement"] == "dados_sensores")
          |> filter(fn: (r) => r["_field"] == "status_energia")
          |> yield(name: "Status Energia")
        ```
    4.  No painel direito, mude a **Visualization** para **"State timeline"**.
    5.  Em **Value mappings**, configure duas regras:
        * **Regra 1:** `Value`: `1`, `Display text`: `Ligado`, `Color`: `green`.
        * **Regra 2:** `Value`: `0`, `Display text`: `Desligado`, `Color`: `red`.
    6.  Defina o **Title** como `Status da Energia`.
    7.  Clique em **"Apply"**.
    </details>

    * Após criar os três painéis, clique no ícone de disquete (💾) no canto superior direito para **salvar o dashboard**.

### Passo 5: Rodar o Firmware do ESP32

1.  Acesse o [Wokwi](https://wokwi.com/) e configure o projeto com os arquivos `sketch.ino` e `diagram.json` fornecidos.
2.  Inicie a simulação. O ESP32 começará a enviar dados que aparecerão no seu dashboard do Grafana.

---

## Solução de Problemas (Troubleshooting)

**Erro no Windows: `open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.`**

* **Causa:** Este erro significa que o Docker Desktop não está em execução ou não iniciou corretamente.
* **Solução:**
    1.  Abra o aplicativo "Docker Desktop" pelo Menu Iniciar.
    2.  Aguarde o ícone do Docker na bandeja do sistema ficar estável.
    3.  Feche seu terminal e abra um novo.
    4.  Navegue até a pasta do projeto e execute o comando `docker-compose up -d --build` novamente.
