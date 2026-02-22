import yfinance as yf
import pandas as pd
import time
import os
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from telegram import Bot

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

bot = Bot(token=TOKEN)

symbols = {
    "SREBRO": "XAGUSD=X",
    "ZŁOTO": "XAUUSD=X",
    "USOIL": "CL=F",
    "UKOIL": "BZ=F"
}

def analyze(name, code):
    data = yf.download(code, period="15d", interval="1h")

    if data.empty:
        return None

    data["rsi"] = RSIIndicator(close=data["Close"], window=14).rsi()
    data["ema"] = EMAIndicator(close=data["Close"], window=200).ema_indicator()
    macd = MACD(close=data["Close"])
    data["macd"] = macd.macd_diff()

    last = data.iloc[-1]
    price = last["Close"]

    if last["rsi"] < 35 and price > last["ema"] and last["macd"] > 0:
        sl = price * 0.99
        tp = price * 1.02
        return f"🟢 KUP {name}\nCena: {price:.2f}\nSL: {sl:.2f}\nTP: {tp:.2f}"

    if last["rsi"] > 65 and price < last["ema"] and last["macd"] < 0:
        sl = price * 1.01
        tp = price * 0.98
        return f"🔴 SPRZEDAJ {name}\nCena: {price:.2f}\nSL: {sl:.2f}\nTP: {tp:.2f}"

    return None

print("Bot uruchomiony...")

while True:
    for name, code in symbols.items():
        signal = analyze(name, code)
        if signal:
            bot.send_message(chat_id=CHAT_ID, text=signal)

    time.sleep(3600)
