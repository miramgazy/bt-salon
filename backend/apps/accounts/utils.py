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
        req = urllib.request.Request(url, data=data, content_type='application/json')
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error sending telegram message: {e}")
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
