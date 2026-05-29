import os
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from claude_farm import TradingFarm
from datetime import datetime
import logging

# Завантаж .env
load_dotenv()

app = Flask(__name__)

# Логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ферма агентів
farm = TradingFarm()

# Зберігання трейдів (локально, потім замінимо на БД)
trades_log = []


@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Webhook від TradingView.
    Очікує JSON:
    {
        "price": 5500,
        "high": 5510,
        "low": 5480,
        "volume": 1000000,
        "atr": 45
    }
    """
    try:
        data = request.get_json()
        logger.info(f"📥 Received webhook: {data}")
        
        # Валідація
        required_fields = ['price', 'high', 'low', 'volume', 'atr']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Обробити через ферму
        result = farm.process_market_data({
            'price': float(data['price']),
            'high': float(data['high']),
            'low': float(data['low']),
            'volume': float(data['volume']),
            'atr': float(data['atr'])
        })
        
        # Логуй результат
        trades_log.append(result['log'])
        
        # Отправь сигнал в Telegram (якщо є)
        if result['signal'].get('signal') != 'WAIT':
            send_telegram_signal(result)
        
        logger.info(f"✅ Signal: {result['signal'].get('signal')}")
        
        return jsonify({
            "status": "success",
            "signal": result['signal'].get('signal'),
            "entry": result['signal'].get('entry_price'),
            "stop_loss": result['signal'].get('stop_loss'),
            "take_profit": result['signal'].get('take_profit'),
            "risk_approved": result['risk_check'].get('approved')
        }), 200
    
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/test', methods=['GET'])
def test():
    """Тестовий endpoint"""
    test_data = {
        "price": 5500,
        "high": 5510,
        "low": 5480,
        "volume": 1000000,
        "atr": 45
    }
    
    result = farm.process_market_data(test_data)
    return jsonify(result), 200


@app.route('/logs', methods=['GET'])
def get_logs():
    """Отримай всі логи торговель"""
    return jsonify({
        "total_trades": len(trades_log),
        "trades": trades_log[-10:]  # Останніх 10
    }), 200


@app.route('/health', methods=['GET'])
def health():
    """Перевір статус сервера"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "total_signals": len(trades_log)
    }), 200


def send_telegram_signal(result):
    """Відправь сигнал в Telegram"""
    try:
        from telegram import Bot
        import asyncio
        
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not token or not chat_id:
            logger.warning("Telegram credentials not configured")
            return
        
        signal = result['signal'].get('signal')
        entry = result['signal'].get('entry_price')
        sl = result['signal'].get('stop_loss')
        tp = result['signal'].get('take_profit')
        confidence = result['signal'].get('confidence')
        
        message = f"""
🚨 S&P 500 Trading Signal

Signal: {signal}
Entry: {entry}
Stop Loss: {sl}
Take Profit: {tp}
Confidence: {confidence}
Risk Approved: {result['risk_check'].get('approved')}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        # Відправь асинхронно
        bot = Bot(token=token)
        asyncio.run(bot.send_message(chat_id=chat_id, text=message))
        logger.info(f"✉️ Telegram message sent")
    
    except Exception as e:
        logger.error(f"Telegram error: {e}")


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
