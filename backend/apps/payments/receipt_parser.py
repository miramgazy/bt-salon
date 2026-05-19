import re
from pdfminer.high_level import extract_text
import logging

logger = logging.getLogger(__name__)

def parse_kaspi_receipt(file_path):
    """
    Parses a Kaspi PDF receipt and extracts:
    - bin_iin (Merchant's 12-digit BIN/IIN)
    - amount (Float representing the paid amount)
    - receipt_number (String representing the receipt/transaction number)

    Returns a dict with the parsed data, or None if extraction fails completely.
    """
    try:
        # Extract text from PDF
        text = extract_text(file_path)
        if not text:
            logger.warning(f"No text extracted from PDF file: {file_path}")
            return None
        
        logger.info(f"Successfully extracted text from receipt PDF ({len(text)} chars)")
        
        # 1. Parse BIN/IIN
        # Extract all 12-digit numbers as potential BINs/IINs
        all_12_digits = re.findall(r'\b\d{12}\b', text)
        
        # Also try direct label matching
        bin_match = re.search(r'(?:БИН|ИИН)\s*(?:продавца|получателя|бенефициара)?\s*:?\s*(\d{12})', text, re.IGNORECASE)
        bin_iin = bin_match.group(1) if bin_match else (all_12_digits[0] if all_12_digits else None)
        
        # 2. Parse Amount
        amount = None
        # Pattern 1: Look for amount followed by Tenge symbol
        amount_match = re.search(r'(?:Сумма|Итого|Всего|Оплачено|Сумма платежа|Сумма к оплате)\s*:?\s*([\d\s\.,]+)\s*(?:₸|KZT|тенге)', text, re.IGNORECASE)
        if amount_match:
            raw_amount = amount_match.group(1)
            # Clean up whitespace and commas
            cleaned = re.sub(r'[\s\s]+', '', raw_amount).replace(' ', '').replace(',', '.')
            if '.' in cleaned:
                # Handle trailing dot or commas
                try:
                    amount = float(cleaned.rstrip('.'))
                except ValueError:
                    pass
            else:
                try:
                    amount = float(cleaned)
                except ValueError:
                    pass
                    
        # Fallback amount parsing if Pattern 1 failed: look for any number before ₸
        if amount is None:
            fallback_match = re.search(r'([\d\s\.,]+)\s*₸', text)
            if fallback_match:
                cleaned = re.sub(r'[\s\s]+', '', fallback_match.group(1)).replace(' ', '').replace(',', '.')
                try:
                    amount = float(cleaned.rstrip('.'))
                except ValueError:
                    pass

        # 3. Parse Receipt Number
        receipt_number = None
        # Pattern 1: № чека / Чек №
        receipt_match = re.search(r'(?:№\s*чека|чек\s*№|номер\s*чека|транзакци\w*\s*№|номер\s*платежа|№\s*квитанции|квитанци\w*\s*№)\s*:?\s*([A-Za-z0-9_\-]+)', text, re.IGNORECASE)
        if receipt_match:
            receipt_number = receipt_match.group(1).strip()
            
        # Fallback 1: Look for standard Kaspi receipt pattern (e.g. 10 or more alphanumeric characters usually near QR code)
        if not receipt_number:
            # Let's search for a token starting with "QR" or any 10-18 character uppercase alphanumeric code
            qr_code_match = re.search(r'\b(QR[A-Z0-9]{8,15}|[A-Z0-9]{10,18})\b', text)
            if qr_code_match:
                receipt_number = qr_code_match.group(1).strip()

        parsed_data = {
            "bin_iin": bin_iin,
            "amount": amount,
            "receipt_number": receipt_number,
            "all_12_digits": all_12_digits
        }
        
        logger.info(f"Parsed receipt data: {parsed_data}")
        return parsed_data

    except Exception as e:
        logger.error(f"Error parsing Kaspi receipt PDF: {e}", exc_info=True)
        return None
