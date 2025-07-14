import os
import ccxt
import time
import requests
from datetime import datetime, timedelta

API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")
TRADE_AMOUNT = float(os.getenv("TRADE_AMOUNT", 25))
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

exchange = ccxt.mexc({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True
})

def send_telegram(message):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})

def get_top_100_tickers():
    tickers = exchange.fetch_tickers()
    sorted_by_volume = sorted(
        [(symbol, data['quoteVolume']) for symbol, data in tickers.items() if symbol.endswith("/USDT")],
        key=lambda x: x[1], reverse=True
    )
    return [symbol for symbol, _ in sorted_by_volume[:100]]

def detect_pump(symbol):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=5)
    if not ohlcv or len(ohlcv) < 5:
        return False
    start_price = ohlcv[0][1]
    end_price = ohlcv[-1][4]
    percent_change = ((end_price - start_price) / start_price) * 100
    return percent_change >= 3

def place_spot_trade(symbol):
    ticker = exchange.fetch_ticker(symbol)
    last_price = ticker['last']
    quantity = round(TRADE_AMOUNT / last_price, 6)
    order = exchange.create_market_buy_order(symbol, quantity)
    return order

def main():
    send_telegram("🚀 Spot trading bot started...")
    open_trades = []
    last_report_time = datetime.now()

    while True:
        symbols = get_top_100_tickers()
        for symbol in symbols:
            try:
                if detect_pump(symbol):
                    order = place_spot_trade(symbol)
                    open_trades.append({"symbol": symbol, "buy_price": order['average'], "quantity": order['filled']})
                    send_telegram(f"📈 Bought {symbol} at {order['average']} (qty: {order['filled']})")
            except Exception as e:
                print(f"[ERROR] {symbol}: {str(e)}")

        if datetime.now() - last_report_time > timedelta(hours=1):
            report = f"📊 Hourly Report ({datetime.now().strftime('%H:%M')}):\n"
            for trade in open_trades:
                report += f"{trade['symbol']} bought at {trade['buy_price']}\n"
            send_telegram(report)
            last_report_time = datetime.now()

        time.sleep(60)

if __name__ == "__main__":
    main()
