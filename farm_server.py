from flask import Flask, jsonify, request
import os
from claude_farm import TradingFarm

app = Flask(__name__)
farm = TradingFarm()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "alive"})

@app.route('/analyze', methods=['POST'])
def analyze_market():
    try:
        data = request.get_json()
        market_data = {
            "price": data.get("price"),
            "high": data.get("high"),
            "low": data.get("low"),
            "volume": data.get("volume"),
            "atr": data.get("atr")
        }
        result = farm.process_market_data(market_data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
