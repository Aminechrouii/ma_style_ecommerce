import json
import uuid
from datetime import datetime
from pathlib import Path


class Order:
    """Order model for M&A Elite Kits"""

    def __init__(self, customer_name, customer_phone, customer_email,
                 shirt_size, shirt_quantity=1, notes=''):
        self.order_id = str(uuid.uuid4())[:8]
        self.customer_name = customer_name
        self.customer_phone = customer_phone
        self.customer_email = customer_email
        self.shirt_size = shirt_size
        self.shirt_quantity = shirt_quantity
        self.notes = notes
        self.created_at = datetime.now().isoformat()
        self.status = 'pending'

    def to_dict(self):
        """Convert order to dictionary"""
        return {
            'order_id': self.order_id,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'customer_email': self.customer_email,
            'shirt_size': self.shirt_size,
            'shirt_quantity': self.shirt_quantity,
            'notes': self.notes,
            'created_at': self.created_at,
            'status': self.status
        }

    def save_to_file(self):
        """Append order data to the global orders.log file"""
        log_file = Path('orders.log')
        if not log_file.exists():
            log_file.touch()

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(self.to_dict(), ensure_ascii=False) + '\n')

        return str(log_file)

    def get_whatsapp_message(self, language='ar'):
        """Generate WhatsApp message text for the order"""
        messages = {
            'ar': f"""
📦 *M&A Elite Kits ✦ - طلب جديد*

👤 الاسم: {self.customer_name}
📞 الهاتف: {self.customer_phone}
📧 البريد: {self.customer_email}
👕 الحجم: {self.shirt_size}
📊 الكمية: {self.shirt_quantity}
📝 الملاحظات: {self.notes or 'لا توجد'}
🔖 رقم الطلب: {self.order_id}
""",
            'fr': f"""
📦 *M&A Elite Kits ✦ - Nouvelle commande*

👤 Nom: {self.customer_name}
📞 Téléphone: {self.customer_phone}
📧 Email: {self.customer_email}
👕 Taille: {self.shirt_size}
📊 Quantité: {self.shirt_quantity}
📝 Notes: {self.notes or 'Aucune'}
🔖 Numéro de commande: {self.order_id}
""",
            'en': f"""
📦 *M&A Elite Kits ✦ - New Order*

👤 Name: {self.customer_name}
📞 Phone: {self.customer_phone}
📧 Email: {self.customer_email}
👕 Size: {self.shirt_size}
📊 Quantity: {self.shirt_quantity}
📝 Notes: {self.notes or 'None'}
🔖 Order ID: {self.order_id}
"""
        }
        return messages.get(language, messages['en'])
