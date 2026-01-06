<div align="center">
  <img src="./img/logo.png" width="160" alt="ByteGasto logo" />

  <h1>ByteGasto</h1>

  <p><strong>Controle seus gastos falando no Telegram.</strong><br>
  Do áudio ao relatório em segundos, tudo rodando localmente.</p>

  <p>
    <img src="https://img.shields.io/badge/status-ativo-2ED3C6?style=for-the-badge" />
    <img src="https://img.shields.io/badge/python-3.10+-10012c?style=for-the-badge&logo=python&logoColor=white" />
    <img src="https://img.shields.io/badge/telegram-bot-5B2D8B?style=for-the-badge&logo=telegram" />
  </p>
</div>

---

## 🚀 O que é o ByteGasto?

O **ByteGasto** é um bot de Telegram para **controle financeiro pessoal**, onde você registra gastos simplesmente **falando**.

Ele transcreve o áudio, entende o valor e a categoria usando **IA local**, salva os dados em um banco SQLite e gera:
- relatórios em **PDF**
- gráficos visuais
- respostas em **linguagem natural**

Tudo isso **sem depender de serviços pagos ou cloud externa**.

---

## ✨ Funcionalidades

### 🤖 Bot no Telegram
- Envie **áudios ou textos**
- Registro automático de gastos
- Confirmação antes de salvar

### 🧠 Inteligência Artificial Local
- **Ollama + Qwen2 1.5B**
- Extração estruturada (JSON) de:
  - valor
  - categoria
  - descrição
- Execução 100% local (CPU/GPU)
- Integração via **LangGraph** para orquestração de agentes

### 🎙️ Transcrição de Áudio
- Whisper local
- Conversão automática para WAV
- Normalização de áudio

### 💾 Persistência
- Banco **SQLite**
- Zero configuração
- Dados locais

### 📊 Relatórios e Gráficos
- Relatório em **PDF personalizado**
  - logo
  - cores do projeto
  - totalizador
- Gráfico de gastos por categoria (imagem)

### 🔎 Consultas em PT-BR
- Interpretação via **LangGraph + Qwen2**
- Exemplos:
  - "Quanto gastei com alimentação?"
  - "Total de transporte em janeiro"

---

## 🎨 Identidade Visual

O projeto segue uma identidade visual consistente:

```text
PRIMARY   #10012c
SECONDARY #2ED3C6
ACCENT    #F5B301
TEXT      #1F1F1F
```

Essas cores são usadas em:
- PDF
- gráficos
- identidade do projeto

---

## 🧱 Arquitetura (Visão Geral)

```text
Telegram
   │
   ▼
Bot (python-telegram-bot)
   │
   ├── Áudio → ffmpeg → Whisper
   │
   ├── Texto → LangGraph
   │        └── Ollama (qwen2:1.5b)
   │
   ├── SQLite
   │
   ├── PDF / Gráficos
   │
   ▼
Resposta no Telegram
```


---

## 🐳 Docker & Deploy

O projeto roda totalmente via **Docker Compose**:

- volume persistente para o banco
- variáveis sensíveis via **GitHub Secrets**
- deploy automático via **GitHub Actions + self-hosted runner**

```bash
docker compose up -d
```

---

## 🔧 Dependências do Sistema

### Windows (Chocolatey)

```bash
choco install ffmpeg -y
```

### Linux

```bash
sudo apt install ffmpeg
```

---

## 📦 Principais Dependências Python

- python-telegram-bot
- langgraph
- langchain-ollama
- openai-whisper
- torch
- matplotlib
- reportlab
- python-dotenv

---

## 🔐 Variáveis de Ambiente

Exemplo de `.env`:

```env
TELEGRAM_TOKEN=seu_token_aqui
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL="qwen2:1.5b"
WHISPER_MODEL="small"
WHISPER_MODEL_DIR="./models/whisper"
```

<div align="center">
  <strong>ByteGasto</strong><br>
  Controle financeiro simples, privado e inteligente 💜
</div>

