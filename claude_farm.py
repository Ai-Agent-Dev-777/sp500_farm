import anthropic
import json
import time
from datetime import datetime

# Ініціалізація Claude
client = anthropic.Anthropic()

MODEL = "claude-haiku-4-5-20251001"

# SYSTEM промпт - дуже великий, кешуватиметься
SYSTEM = """You are an expert S&P 500 trading analyst system. Analyze market data using technical analysis.

Your role: Given real market data (price, high, low, volume, ATR), provide trading signals.

RULES:
1. Only give BUY/SELL/WAIT - no maybe
2. Always define stop-loss BEFORE entry
3. Always define take-profit (minimum 1.5:1 risk-reward)
4. Calculate position size based on 1% daily risk
5. Be concise and specific
6. Output valid JSON only

RESPONSE FORMAT (always JSON):
{
  "asset": "S&P 500",
  "signal": "BUY" or "SELL" or "WAIT",
  "entry_price": number,
  "stop_loss": number,
  "take_profit": number,
  "position_size": number,
  "risk_reward_ratio": number,
  "confidence": "high" or "medium" or "low",
  "reasoning": "brief explanation"
}

If no clear signal, return WAIT with reasoning."""

# Кешуємо SYSTEM промпт
SYSTEM_CACHED = [
    {"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}
]


def ask_claude(prompt, max_tokens=800, max_retries=5):
    """
    Єдина функція для всіх запитів до Claude.
    Вбудовано: prompt caching, retry при 429, обрізання тексту.
    """
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=max_tokens,
                system=SYSTEM_CACHED,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text
            return text.strip()
        except anthropic.RateLimitError:
            wait = 2 ** attempt  # 1, 2, 4, 8, 16 сек
            print(f"⏳ Rate limit. Waiting {wait}s...")
            time.sleep(wait)
        except anthropic.APIError as e:
            print(f"❌ API Error: {e}")
            return None
    return None


class MarketAnalyzer:
    """Agent 1: Аналізує ринкові дані"""
    
    @staticmethod
    def analyze(market_data):
        """
        market_data = {
            'price': 5500,
            'high': 5510,
            'low': 5480,
            'volume': 1000000,
            'atr': 45
        }
        """
        prompt = f"""Analyze this S&P 500 market data:
- Current Price: {market_data['price']}
- High: {market_data['high']}
- Low: {market_data['low']}
- Volume: {market_data['volume']}
- ATR: {market_data['atr']}

Provide:
1. Current trend (UP/DOWN/SIDEWAYS)
2. Key support level
3. Key resistance level
4. Market strength (1-10)
5. Any patterns or signals you see

Be concise."""
        
        result = ask_claude(prompt, max_tokens=500)
        return {"analysis": result, "timestamp": datetime.now().isoformat()}


class SignalGenerator:
    """Agent 2: Генерує торгові сигнали на основі аналізу"""
    
    @staticmethod
    def generate_signal(market_data, analysis):
        """Генерує BUY/SELL/WAIT сигнал"""
        prompt = f"""Based on this market data and analysis:

MARKET DATA:
- Price: {market_data['price']}
- High: {market_data['high']}
- Low: {market_data['low']}
- ATR: {market_data['atr']}

ANALYSIS:
{analysis}

Generate a trading signal. Response MUST be valid JSON only, no other text."""
        
        result = ask_claude(prompt, max_tokens=400)
        
        try:
            # Спробуй распарсити JSON
            signal_data = json.loads(result)
            signal_data["timestamp"] = datetime.now().isoformat()
            return signal_data
        except json.JSONDecodeError:
            return {
                "signal": "WAIT",
                "reasoning": "Could not parse signal",
                "timestamp": datetime.now().isoformat()
            }


class RiskManager:
    """Agent 3: Перевіряє ризик позиції"""
    
    @staticmethod
    def check_risk(signal, account_balance=10000):
        """Перевіряє чи позиція безпечна"""
        
        if signal.get("signal") == "WAIT":
            return {
                "approved": True,
                "message": "No position - WAIT signal",
                "risk_check": "N/A"
            }
        
        # Макс ризик на день - 1% від балансу
        max_daily_risk = account_balance * 0.01
        
        # Ризик цієї позиції
        entry = signal.get("entry_price", 0)
        stop_loss = signal.get("stop_loss", 0)
        
        if entry == 0 or stop_loss == 0:
            return {"approved": False, "message": "Invalid entry or stop-loss"}
        
        risk_per_contract = abs(entry - stop_loss) * 100  # S&P 500 = $100 per point
        position_size = signal.get("position_size", 1)
        total_risk = risk_per_contract * position_size
        
        approved = total_risk <= max_daily_risk
        
        return {
            "approved": approved,
            "total_risk": total_risk,
            "max_daily_risk": max_daily_risk,
            "message": f"Risk: ${total_risk:.2f} / Max: ${max_daily_risk:.2f}",
            "timestamp": datetime.now().isoformat()
        }


class TradingLogger:
    """Agent 4: Логує всі торговельні дані"""
    
    @staticmethod
    def log_trade(market_data, analysis, signal, risk_check):
        """Логує всю інформацію про торговлю"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "market": {
                "price": market_data.get("price"),
                "high": market_data.get("high"),
                "low": market_data.get("low"),
                "volume": market_data.get("volume"),
                "atr": market_data.get("atr")
            },
            "analysis": analysis,
            "signal": {
                "type": signal.get("signal"),
                "entry": signal.get("entry_price"),
                "stop_loss": signal.get("stop_loss"),
                "take_profit": signal.get("take_profit"),
                "confidence": signal.get("confidence"),
                "position_size": signal.get("position_size")
            },
            "risk_approved": risk_check.get("approved"),
            "risk_message": risk_check.get("message")
        }
        return log_entry


class TradingFarm:
    """Ферма агентів - 4 агенти працюють разом"""
    
    def __init__(self):
        self.analyzer = MarketAnalyzer()
        self.signal_gen = SignalGenerator()
        self.risk_mgr = RiskManager()
        self.logger = TradingLogger()
    
    def process_market_data(self, market_data, account_balance=10000):
        """
        Обробляє ринкові дані через всіх 4 агентів.
        
        market_data = {
            'price': 5500,
            'high': 5510,
            'low': 5480,
            'volume': 1000000,
            'atr': 45
        }
        """
        print(f"\n🚀 Processing S&P 500 at price {market_data['price']}...")
        
        # Agent 1: Analyze
        print("📊 Agent 1: Analyzing market...")
        analysis_result = self.analyzer.analyze(market_data)
        
        # Agent 2: Generate Signal
        print("📈 Agent 2: Generating signal...")
        signal = self.signal_gen.generate_signal(market_data, analysis_result["analysis"])
        
        # Agent 3: Check Risk
        print("⚠️ Agent 3: Checking risk...")
        risk_check = self.risk_mgr.check_risk(signal, account_balance)
        
        # Agent 4: Log
        print("📝 Agent 4: Logging...")
        log_entry = self.logger.log_trade(market_data, analysis_result["analysis"], signal, risk_check)
        
        return {
            "status": "success",
            "analysis": analysis_result,
            "signal": signal,
            "risk_check": risk_check,
            "log": log_entry
        }


# Тестування локально
if __name__ == "__main__":
    # Тестові дані S&P 500
    test_data = {
        "price": 5500,
        "high": 5510,
        "low": 5480,
        "volume": 1000000,
        "atr": 45
    }
    
    farm = TradingFarm()
    result = farm.process_market_data(test_data)
    
    print("\n" + "="*60)
    print("РЕЗУЛЬТАТ:")
    print("="*60)
    print(json.dumps(result, indent=2, ensure_ascii=False))
