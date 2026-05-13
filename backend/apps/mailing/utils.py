import requests
import logging

logger = logging.getLogger(__name__)


def send_telegram_mailing_message(bot_token, chat_id, text, reply_markup=None):
    """
    Отправляет сообщение через Telegram Bot API с использованием библиотеки requests.
    Возвращает структуру с подробным ответом и HTTP статус-кодом для точной обработки ошибок (403).
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    if reply_markup:
        payload['reply_markup'] = reply_markup

    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
        
        return {
            'success': response.status_code == 200 and data.get('ok', False),
            'status_code': response.status_code,
            'response': data
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"[Mailing] Network error sending message to {chat_id}: {e}")
        return {
            'success': False,
            'status_code': None,
            'response': {'error': str(e)}
        }
