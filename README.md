# 🚀 S&P 500 TRADING FARM 24/7

Автоматизована система торгівлі S&P 500 з 4 агентами, Prompt Caching і 24/7 моніторингом.

---

## 📋 СТРУКТУРА ПРОЕКТУ

```
sp500_farm/
├── claude_farm.py          # Ферма агентів (4 агенти: Analyzer, Signal, Risk, Logger)
├── farm_server.py          # Flask сервер (вебхуки від TradingView)
├── tradingview.pine        # Pine Script для TradingView
├── requirements.txt        # Python залежності
├── .env.example            # Шаблон для налаштувань
└── README.md               # Цей файл
```

---

## 🔧 ВСТАНОВЛЕННЯ

### Крок 1 — Вимоги

- Python 3.9+
- Claude API Key
- TradingView акаунт
- Telegram Bot Token
- Railway & Supabase (для 24/7)

### Крок 2 — Клонуй репо (або скачай файли)

```bash
git clone <YOUR_REPO>
cd sp500_farm
```

### Крок 3 — Встанови залежності

```bash
pip install -r requirements.txt
```

### Крок 4 — Налаштуй .env

Скопіюй `.env.example` → `.env` і вставь свої значення:

```bash
cp .env.example .env
```

Редагуй `.env`:
```
ANTHROPIC_API_KEY=sk-ant-YOUR_KEY
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN
TELEGRAM_CHAT_ID=YOUR_CHAT_ID
SUPABASE_URL=YOUR_URL
SUPABASE_KEY=YOUR_KEY
```

---

## 🧪 ЛОКАЛЬНЕ ТЕСТУВАННЯ

### Запусти claude_farm.py (агенти)

```bash
python claude_farm.py
```

**Результат:**
- 📊 Agent 1 аналізує дані
- 📈 Agent 2 генерує сигнал
- ⚠️ Agent 3 перевіряє ризик
- 📝 Agent 4 логує все

Виведе JSON з сигналом BUY/SELL/WAIT.

### Запусти farm_server.py (Flask)

```bash
python farm_server.py
```

**Результат:**
- Server running on http://localhost:5000

### Тестовий вебхук

В іншому терміналі:

```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "price": 5500,
    "high": 5510,
    "low": 5480,
    "volume": 1000000,
    "atr": 45
  }'
```

**Результат:**
```json
{
  "status": "success",
  "signal": "BUY",
  "entry": 5505,
  "stop_loss": 5480,
  "take_profit": 5550,
  "risk_approved": true
}
```

Перевір логи: http://localhost:5000/logs

---

## 🌐 ДЕПЛОЙ НА RAILWAY (24/7)

### 1. Зроби репо на GitHub

```bash
git init
git add .
git commit -m "S&P 500 Trading Farm"
git push -u origin main
```

### 2. Деплой на Railway

1. Зайди на railway.app
2. New Project → Connect GitHub
3. Вибери свій репо
4. Railway автоматично знайде `requirements.txt`
5. Set Environment Variables (з `.env`)
6. Deploy!

Railway дасть URL: `https://sp500-farm-xxx.railway.app`

---

## 📊 ІНТЕГРАЦІЯ З TRADINGVIEW

### 1. Скопіюй Pine Script

1. TradingView → Pine Script Editor
2. Create new indicator
3. Вставь код з `tradingview.pine`
4. Add to Chart

### 2. Налаштуй Alert

1. TradingView → Alert
2. Alert name: `SP500 Trading Farm`
3. Webhook URL: `https://YOUR-RAILWAY-URL/webhook`
4. Frequency: **Every 5 minutes**
5. Create Alert

### 3. Перевір що спрацює

1. Закрий/відкрий свічку (або чекай 5 хвилин)
2. TradingView відправить webhook
3. Ферма обробить і відправить сигнал
4. Telegram повідомить

---

## 💰 ЕКОНОМІЯ ТОКЕНІВ

Система використовує:
- ✅ **Prompt Caching** — SYSTEM промпт кешується (-90% на повторах)
- ✅ **Retry Backoff** — при помилці автоматично пробує (-0 втрат)
- ✅ **Batch Processing** — можливо додати для масових аналізів (-50%)

**Вартість:**
- Без оптимізації: ~$0.66/день
- З caching: ~$0.30/день
- **За місяць: ~$9**

---

## 🔍 МОНІТОРИНГ

### Логи локально
```bash
python farm_server.py
# Видиш логи в терміналі real-time
```

### Логи на Railway
```
Railway Dashboard → Logs
```

### Всі трейди
```
GET http://localhost:5000/logs
```

### Статус серверу
```
GET http://localhost:5000/health
```

---

## 🐛 ДЕБАГ

**Вебхук не приходить?**
- Перевір URL в TradingView (без https://, це помилка)
- Перевір Railway URL доступний (curl test)
- Перевір логи на Railway

**Сигнали не приходять в Telegram?**
- Перевір TELEGRAM_BOT_TOKEN в `.env`
- Перевір TELEGRAM_CHAT_ID
- Спочатку напиши боту /start

**Claude API error?**
- Перевір ANTHROPIC_API_KEY
- Перевір що є гроші на акаунті
- Перевір rate limits

---

## 📈 АДАПТАЦІЯ

### Змінити символ (тепер S&P 500, можна будь-який)

`tradingview.pine`:
```pine
indicator("Your Symbol Trading Farm Webhook", overlay=true)
```

`claude_farm.py`:
```python
SYSTEM = """You are an expert YOUR_SYMBOL trading analyst..."""
```

### Змінити таймфрейм

`tradingview.pine`:
```pine
send_interval = input.int(defval=1, title="Send Interval (minutes)")  // Кожну хвилину
```

### Додати більше агентів

`claude_farm.py`:
```python
class CustomAgent:
    @staticmethod
    def custom_analysis(data):
        # Твоя логіка
        pass

# В TradingFarm додай:
self.custom_agent = CustomAgent()
```

---

## 📞 ПІДТРИМКА

Якщо щось не спрацює:
1. Перевір логи
2. Тестуй локально спочатку
3. Потім деплой

---

## ⚠️ DISCLAIMER

Цей код для навчання та експериментів. Торгівля несе ризики. Завжди:
- Тестуй на малих позиціях
- Встанови stop-loss ЗАВЖДИ
- Не ризикуй більше ніж можеш втратити
- Перевіряй сигнали вручну перед виконанням

---

**Happy Trading! 🚀📈**
