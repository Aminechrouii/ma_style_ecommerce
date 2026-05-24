from flask import Flask, render_template, request, jsonify, session, redirect
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect, generate_csrf
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

from models import Order
from services import SecurityService, WhatsAppService


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ma-style-secret-key-2024-secure-key')
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    WTF_CSRF_SSL_STRICT = True

    TALISMAN_CONFIG = {
        'force_https': False,
        'strict_transport_security': True,
        'strict_transport_security_max_age': 31536000,
        'content_security_policy': {
            'default-src': ["'self'"],
            'script-src': ["'self'", "'unsafe-inline'"],
            'style-src': ["'self'", "'unsafe-inline'", 'https://cdnjs.cloudflare.com', 'https://use.fontawesome.com'],
            'img-src': ["'self'", 'data:'],
            'font-src': ["'self'", 'https://cdnjs.cloudflare.com', 'https://use.fontawesome.com'],
            'connect-src': ["'self'"]
        }
    }

    WHATSAPP_PHONE_NUMBER = os.environ.get('WHATSAPP_PHONE_NUMBER', '+212617934680')

    PRODUCT = {
        'name': 'Morocco Team Shirt',
        'name_ar': 'قميص المنتخب المغربي',
        'name_fr': 'Maillot de l\'équipe du Maroc',
        'price': 199,
        'currency': 'MAD'
    }

    SITE_NAME = 'M&A Elite Kits ✦'
    LANGUAGES = {
        'ar': 'العربية',
        'fr': 'Français',
        'en': 'English'
    }


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_SSL_STRICT = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True


app = Flask(__name__)
config_name = os.environ.get('FLASK_ENV', 'development')
if config_name == 'production':
    app.config.from_object(ProductionConfig)
else:
    app.config.from_object(DevelopmentConfig)

Talisman(app, **app.config['TALISMAN_CONFIG'])
csrf = CSRFProtect(app)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


ORDER_PRICES = {1: 199, 2: 299, 3: 399, 4: 499, 5: 599, 6: 699, 7: 799, 8: 899, 9: 999, 10: 1099}


@app.route('/')
@app.route('/index')
def index():
    return redirect('/en')


@app.route('/ar')
def index_ar():
    session['language'] = 'ar'
    return render_template('ar/index.html', whatsapp_phone=app.config['WHATSAPP_PHONE_NUMBER'])


@app.route('/fr')
def index_fr():
    session['language'] = 'fr'
    return render_template('fr/index.html', whatsapp_phone=app.config['WHATSAPP_PHONE_NUMBER'])


@app.route('/en')
def index_en():
    session['language'] = 'en'
    return render_template('en/index.html', whatsapp_phone=app.config['WHATSAPP_PHONE_NUMBER'])


@app.route('/api/order', methods=['POST'])
def submit_order():
    try:
        data = request.get_json()
        language = session.get('language', 'ar')
        if not data:
            return jsonify({'status': 'error', 'message': 'Invalid data'}), 400

        customer_name = SecurityService.sanitize_input(data.get('customer_name', ''))
        customer_phone = data.get('customer_phone', '')
        customer_email = data.get('customer_email', '')
        shirt_size = data.get('shirt_size', '')
        shirt_quantity = data.get('shirt_quantity', 1)
        notes = SecurityService.sanitize_input(data.get('notes', ''))

        if not customer_name or len(customer_name) < 2:
            return jsonify({'status': 'error', 'message': 'Invalid name'}), 400
        if not SecurityService.validate_phone(customer_phone):
            return jsonify({'status': 'error', 'message': 'Invalid phone'}), 400
        if not SecurityService.validate_email(customer_email):
            return jsonify({'status': 'error', 'message': 'Invalid email'}), 400
        if shirt_size not in ['XS', 'S', 'M', 'L', 'XL', 'XXL']:
            return jsonify({'status': 'error', 'message': 'Invalid size'}), 400
        if not (1 <= int(shirt_quantity) <= 10):
            return jsonify({'status': 'error', 'message': 'Invalid quantity'}), 400

        order = Order(
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            shirt_size=shirt_size,
            shirt_quantity=int(shirt_quantity),
            notes=notes
        )
        order.save_to_file()
        SecurityService.log_order(order.to_dict())

        total_price = ORDER_PRICES.get(int(shirt_quantity), app.config['PRODUCT']['price'])
        whatsapp_link = WhatsAppService.generate_whatsapp_link(
            app.config['WHATSAPP_PHONE_NUMBER'],
            order.get_whatsapp_message(language),
            language
        )

        logger.info(f"Order created: {order.order_id} for {customer_name}")
        return jsonify({
            'status': 'success',
            'order_id': order.order_id,
            'whatsapp_link': whatsapp_link,
            'total_price': total_price,
            'message': f"Order {order.order_id} created successfully!"
        }), 201
    except Exception as e:
        logger.error(f"Error submitting order: {e}")
        return jsonify({'status': 'error', 'message': 'Server error'}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()}), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': 'Not found'}), 404


@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {error}")
    return jsonify({'status': 'error', 'message': 'Server error'}), 500


if __name__ == '__main__':
    Path('orders.log').touch(exist_ok=True)
    debug_mode = app.config.get('DEBUG', False)
    app.run(host='0.0.0.0', port=5000, debug=debug_mode, use_reloader=debug_mode)
