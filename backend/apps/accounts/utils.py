import re

def slugify_cyrillic(text):
    """
    Transliterates Cyrillic text to Latin and slugifies it.
    """
    if not text:
        return "organization"
        
    # Russian/Kazakh transliteration map
    cyrillic_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '',
        'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        # Kazakh specific
        'ә': 'ae', 'ғ': 'g', 'қ': 'q', 'ң': 'n', 'ө': 'o', 'ұ': 'u', 'ү': 'u', 'һ': 'h', 'і': 'i'
    }
    
    # Convert to lower and transliterate
    text = text.lower()
    transliterated = ""
    for char in text:
        transliterated += cyrillic_map.get(char, char)
        
    # Remove non-alphanumeric chars and replace spaces with hyphens
    text = re.sub(r'[^a-z0-9]+', '-', transliterated)
    
    # Clean up hyphens
    return text.strip('-')

import urllib.request
import json

def send_telegram_message(bot_token, chat_id, text, reply_markup=None):
    """
    Sends a message via Telegram Bot API.
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
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error sending telegram message: {e}")
        return None

def answer_telegram_callback(bot_token, callback_query_id, text=None):
    """
    Answers a callback query via Telegram Bot API.
    """
    url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"
    payload = {
        'callback_query_id': callback_query_id,
    }
    if text:
        payload['text'] = text
        
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error answering telegram callback: {e}")
        return None

def edit_telegram_message(bot_token, chat_id, message_id, text, reply_markup=None):
    """
    Edits an existing message via Telegram Bot API.
    """
    url = f"https://api.telegram.org/bot{bot_token}/editMessageText"
    payload = {
        'chat_id': chat_id,
        'message_id': message_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    if reply_markup:
        payload['reply_markup'] = reply_markup
        
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error editing telegram message: {e}")
        return None

def normalize_phone(phone):
    """
    Normalizes phone numbers to +7XXXXXXXXXX format.
    """
    if not phone:
        return ""
    # Extract only digits
    digits = re.sub(r'\D', '', phone)
    
    if len(digits) == 11:
        if digits.startswith('8'):
            return '+7' + digits[1:]
        if digits.startswith('7'):
            return '+' + digits
    elif len(digits) == 10:
        return '+7' + digits
        
    return '+' + digits if digits else ""

def download_file_from_telegram(bot_token, file_id):
    """
    Downloads a file from Telegram Bot API and returns its local temporary path.
    """
    import urllib.request
    import json
    import tempfile
    
    # 1. Get file path
    url = f"https://api.telegram.org/bot{bot_token}/getFile?file_id={file_id}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            if not res_data.get('ok'):
                return None
            file_path_tg = res_data['result']['file_path']
            
        # 2. Download file
        download_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path_tg}"
        
        # Create temp file
        ext = '.' + file_path_tg.split('.')[-1] if '.' in file_path_tg else ''
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        temp_path = temp_file.name
        
        with urllib.request.urlopen(download_url) as response_dl:
            with open(temp_path, 'wb') as out_file:
                out_file.write(response_dl.read())
                
        return temp_path
    except Exception as e:
        print(f"Error downloading file from Telegram: {e}")
        return None
