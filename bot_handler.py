import os
import time
import json
import urllib.request
import urllib.error


def _load_env_from_file(path):
    """Load .env file into os.environ (won't override existing vars)."""
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip("'\"")
            if key and key not in os.environ:
                os.environ[key] = value


def _load_env():
    """Load .env from multiple locations in priority order."""
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 1. Local .env next to this script (highest priority)
    _load_env_from_file(os.path.join(script_dir, '.env'))

    # 2. Hermes profile .env (if accessible)
    hermes_home = os.environ.get('HERMES_HOME', '')
    if hermes_home:
        for profile_dir in [d for d in os.listdir(os.path.join(hermes_home, 'profiles'))
                            if os.path.isdir(os.path.join(hermes_home, 'profiles', d))]:
            _load_env_from_file(os.path.join(hermes_home, 'profiles', profile_dir, '.env'))

    # 3. Common Docker / venv fallback paths
    fallback_paths = [
        '/app/.env',                                        # Docker working dir
        '/opt/hermes/data/.env',                            # Docker mounted volume
        os.path.join(os.path.expanduser('~'), '.hermes', 'data', '.env'),  # venv default
    ]
    for p in fallback_paths:
        _load_env_from_file(p)


_load_env()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

VIBE_API_KEY = os.environ.get('VIBE_API_KEY', os.environ.get('VIBE_KEY', ''))
BASE = os.environ.get('VIBE_BASE_URL', 'https://vibecode.bitrix24.tech/v1')

BOT_ID = int(os.environ.get('BOT_ID', '0'))
BOT_NAME = os.environ.get('BOT_NAME', 'HermesBot')
POLL_INTERVAL = int(os.environ.get('POLL_INTERVAL', '3'))
HERMES_MODEL = os.environ.get('HERMES_MODEL', 'bitrix/bitrixgpt-5.5')

# Support comma-separated multiple bot IDs
BOT_IDS = [int(x.strip()) for x in os.environ.get('BOT_IDS', str(BOT_ID)).split(',') if x.strip()]

SYSTEM_PROMPT = """Ты — Hermes, AI-ассистент в Bitrix24.
Отвечай на русском языке. Будь полезным, кратким и дружелюбным.
Если не знаешь ответ — скажи об этом честно.
Не придумывай информацию, если не уверен."""

offset = None
chat_history = {}


def api_call(method, path, body=None):
    url = f'{BASE}{path}'
    headers = {'X-Api-Key': VIBE_API_KEY, 'Content-Type': 'application/json'}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f'[{time.strftime("%H:%M:%S")}] API error: {e}')
        return None


def generate_ai_response(dialog_id, user_message):
    history = chat_history.get(dialog_id, [])
    messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
    messages.extend(history[-20:])
    messages.append({'role': 'user', 'content': user_message})
    result = api_call('POST', '/chat/completions', {
        'model': HERMES_MODEL,
        'messages': messages,
        'temperature': 0.7,
        'max_tokens': 2000
    })
    if result and 'choices' in result:
        response = result['choices'][0]['message']['content']
        if dialog_id not in chat_history:
            chat_history[dialog_id] = []
        chat_history[dialog_id].append({'role': 'user', 'content': user_message})
        chat_history[dialog_id].append({'role': 'assistant', 'content': response})
        if len(chat_history[dialog_id]) > 40:
            chat_history[dialog_id] = chat_history[dialog_id][-40:]
        return response
    return 'Извините, произошла ошибка при генерации ответа.'


def handle_event(bot_id, event):
    if event.get('type') != 'ONIMBOTV2MESSAGEADD':
        return
    data = event.get('data', {})
    message = data.get('message', {})
    if message.get('isSystem') or message.get('authorId') == bot_id:
        return
    chat = data.get('chat', {})
    dialog_id = chat.get('dialogId', '')
    text = message.get('text', '')
    user_name = data.get('user', {}).get('firstName', 'друг')
    print(f'[{time.strftime("%H:%M:%S")}] Bot {bot_id} | {user_name}: {text[:80]}')
    api_call('POST', f'/bots/{bot_id}/typing', {
        'dialogId': dialog_id,
        'statusMessageCode': 'IMBOT_AGENT_ACTION_THINKING'
    })
    response = generate_ai_response(dialog_id, text)
    result = api_call('POST', f'/bots/{bot_id}/messages', {
        'dialogId': dialog_id,
        'fields': {'message': response}
    })
    if result and result.get('success'):
        print(f'[{time.strftime("%H:%M:%S")}] Bot {bot_id} | Sent OK')


def poll():
    global offset
    print(f'[{time.strftime("%H:%M:%S")}] Hermes bot started')
    print(f'[{time.strftime("%H:%M:%S")}] Bot IDs: {BOT_IDS}')
    print(f'[{time.strftime("%H:%M:%S")}] Bot Name: {BOT_NAME}')
    print(f'[{time.strftime("%H:%M:%S")}] Model: {HERMES_MODEL}')
    print(f'[{time.strftime("%H:%M:%S")}] Polling every {POLL_INTERVAL}s...')
    while True:
        try:
            for bot_id in BOT_IDS:
                url = f'/bots/{bot_id}/events'
                if offset is not None:
                    url += f'?offset={offset}'
                result = api_call('GET', url)
                events = []
                if result and result.get('success'):
                    data = result.get('data', {})
                    events = data.get('events', [])
                    for event in events:
                        handle_event(bot_id, event)
                    if data.get('nextOffset') is not None:
                        offset = data['nextOffset']
            time.sleep(POLL_INTERVAL if not events else 0.5)
        except KeyboardInterrupt:
            print(f'[{time.strftime("%H:%M:%S")}] Bot stopped')
            break
        except Exception as e:
            print(f'[{time.strftime("%H:%M:%S")}] Poll error: {e}')
            time.sleep(5)


if __name__ == '__main__':
    poll()