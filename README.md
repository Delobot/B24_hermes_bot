# B24 Hermes Bot — Плагин Bitrix24 для Hermes Agent

**Русский** | [English](#english-version)

## Описание

Нативный плагин-адаптер **Bitrix24** для AI-ассистента **Hermes Agent**. Позволяет Hermes общаться с пользователями в мессенджере Bitrix24, обрабатывать сообщения и отправлять ответы через AI.

### Возможности

- Автоматическое получение сообщений из Bitrix24 через VibeCode API
- Обработка входящих событий и фильтрация
- Отправка ответов с индикатором набора текста
- Автоматический поллинг каждые 3 секунды
- Поддержка нескольких ботов одновременно
- Интеграция с моделью AI из профиля Hermes
- Авто-создание ботов через API

### Архитектура

```
Пользователь Bitrix24
        ↓ сообщение
   Bitrix24 Adapter (polling)
        ↓
   Hermes Agent (AI)
        ↓ ответ
   Bitrix24 Adapter (send)
        ↓
Пользователь Bitrix24
```

## Установка

### 1. Клонирование

```bash
git clone https://github.com/Delobot/B24_hermes_bot.git
cd B24_hermes_bot
```

### 2. Конфигурация

```bash
cp config/bitrix24_example.yaml config/bitrix24.yaml
```

Отредактируйте `config/bitrix24.yaml`:

```yaml
platforms:
  bitrix24:
    enabled: true
    extra:
      api_key: "vibe_api_ВАШ_КЛЮЧ"
      bot_id: 19
      base_url: "https://vibecode.bitrix24.tech/v1"
      poll_interval: 3
```

### 3. API ключ VibeCode

1. Перейдите на https://vibecode.bitrix24.tech/keys
2. Создайте ключ `vibe_api_...`
3. **Важно:** ключ должен быть создан от имени пользователя, от имени которого будет общаться бот

### 4. Запуск

**Docker:**
```bash
docker compose up -d
```

**Python venv:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python bot_handler.py
```

## Интеграция с Hermes

### Установка плагина

```bash
cp -r plugins/platforms/bitrix24 ~/.hermes/plugins/
```

### Активация

```bash
hermes plugins enable bitrix24
```

### Перезапуск Gateway

```bash
hermes gateway restart
```

## Структура проекта

```
B24_hermes_bot/
├── plugins/platforms/bitrix24/   ← Плагин Hermes
│   ├── __init__.py
│   ├── adapter.py
│   └── plugin.yaml
├── scripts/
├── tests/
├── config/
├── bot_handler.py
├── Dockerfile
└── docker-compose.yml
```

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `VIBE_API_KEY` | API ключ VibeCode | *обязательная* |
| `BOT_ID` | ID бота в Bitrix24 | `19` |
| `BOT_NAME` | Имя бота | `HermesBot` |
| `HERMES_MODEL` | Модель AI | Из профиля Hermes |
| `POLL_INTERVAL` | Интервал опроса (сек) | `3` |

## Тестирование

```bash
pytest tests/ -v
```

## Безопасность

- Не коммитьте `.env` и `config/bitrix24.yaml`
- API ключ хранится в переменных окружения
- Ключ должен быть создан от имени пользователя-бота

## Лицензия

MIT

---

---

# B24 Hermes Bot — Bitrix24 Platform Plugin for Hermes Agent

English | [Русский](#b24-hermes-bot--плагин-bitrix24-для-hermes-agent)

## Description

A native **Bitrix24** platform adapter plugin for the **Hermes Agent** AI assistant. Enables Hermes to communicate with users in Bitrix24 messenger, process messages, and send AI-generated responses.

### Features

- Automatic message retrieval from Bitrix24 via VibeCode API
- Incoming event processing and filtering
- Response delivery with typing indicator
- Automatic polling every 3 seconds
- Support for multiple bots simultaneously
- Integration with AI model from Hermes profile
- Auto bot creation via API

### Architecture

```
Bitrix24 User
      ↓ message
Bitrix24 Adapter (polling)
      ↓
Hermes Agent (AI)
      ↓ response
Bitrix24 Adapter (send)
      ↓
Bitrix24 User
```

## Installation

### 1. Clone

```bash
git clone https://github.com/Delobot/B24_hermes_bot.git
cd B24_hermes_bot
```

### 2. Configuration

```bash
cp config/bitrix24_example.yaml config/bitrix24.yaml
```

Edit `config/bitrix24.yaml`:

```yaml
platforms:
  bitrix24:
    enabled: true
    extra:
      api_key: "vibe_api_YOUR_KEY"
      bot_id: 19
      base_url: "https://vibecode.bitrix24.tech/v1"
      poll_interval: 3
```

### 3. VibeCode API Key

1. Go to https://vibecode.bitrix24.tech/keys
2. Create a key `vibe_api_...`
3. **Important:** key must be created by the user on whose behalf the bot will communicate

### 4. Run

**Docker:**
```bash
docker compose up -d
```

**Python venv:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python bot_handler.py
```

## Hermes Integration

### Install plugin

```bash
cp -r plugins/platforms/bitrix24 ~/.hermes/plugins/
```

### Enable

```bash
hermes plugins enable bitrix24
```

### Restart Gateway

```bash
hermes gateway restart
```

## Project Structure

```
B24_hermes_bot/
├── plugins/platforms/bitrix24/   ← Hermes Plugin
│   ├── __init__.py
│   ├── adapter.py
│   └── plugin.yaml
├── scripts/
├── tests/
├── config/
├── bot_handler.py
├── Dockerfile
└── docker-compose.yml
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VIBE_API_KEY` | VibeCode API key | *required* |
| `BOT_ID` | Bitrix24 bot ID | `19` |
| `BOT_NAME` | Bot name | `HermesBot` |
| `HERMES_MODEL` | AI model | From Hermes profile |
| `POLL_INTERVAL` | Poll interval (seconds) | `3` |

## Testing

```bash
pytest tests/ -v
```

## Security

- Don't commit `.env` and `config/bitrix24.yaml`
- API key stored in environment variables
- Key must be created by the bot user

## License

MIT
