import hashlib
import logging
import secrets
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

logger = logging.getLogger(__name__)


class SecurityService:
    """Security utilities for M&A Elite Kits"""

    @staticmethod
    def validate_phone(phone_number):
        """Validate phone number format"""
        clean_phone = ''.join(c for c in phone_number if c.isdigit() or c == '+')
        return len(clean_phone) >= 10

    @staticmethod
    def validate_email(email):
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def sanitize_input(user_input):
        """Sanitize user input to reduce injection risk"""
        if not isinstance(user_input, str):
            return str(user_input)

        dangerous_chars = ['<', '>', '"', "'", ';', '&', '|']
        sanitized = user_input
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')

        return sanitized.strip()

    @staticmethod
    def log_order(order_dict):
        """Write a simple order entry to orders.log"""
        log_file = Path('orders.log')
        if not log_file.exists():
            log_file.touch()

        log_entry = f"[{datetime.now().isoformat()}] Order ID: {order_dict.get('order_id', 'N/A')} | Customer: {order_dict.get('customer_name', 'N/A')}\n"
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            logger.error(f"Failed to write to orders.log: {e}")


class WhatsAppService:
    """WhatsApp integration utilities"""

    @staticmethod
    def generate_whatsapp_link(phone_number, message, language='ar'):
        """Create a WhatsApp URL for the message"""
        try:
            clean_phone = ''.join(c for c in phone_number if c.isdigit() or c == '+')
            if not clean_phone.startswith('+'):
                if clean_phone.startswith('212'):
                    clean_phone = '+' + clean_phone
                elif clean_phone.startswith('06') or clean_phone.startswith('07'):
                    clean_phone = '+212' + clean_phone[1:]
                else:
                    clean_phone = '+' + clean_phone

            encoded_message = quote(message)
            return f"https://wa.me/{clean_phone}?text={encoded_message}"
        except Exception as e:
            logger.error(f"Error generating WhatsApp link: {e}")
            return None
