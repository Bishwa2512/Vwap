import csv
import os
from datetime import datetime

BASE_PATH = "/data/logs"

def ensure_dir():
    os.makedirs(BASE_PATH, exist_ok=True)

def today_file(name):
    date = datetime.now().strftime("%Y%m%d")
    return f"{BASE_PATH}/{name}_{date}.csv"

def log_trade(symbol, strike, side, qty, entry, exit_price, pnl):
    ensure_dir()
    file = today_file("trades")
    new = not os.path.exists(file)

    with open(file, "a", newline="") as f:
        writer = csv.writer(f)
        if new:
            writer.writerow([
                "time", "symbol", "strike", "side",
                "qty", "entry", "exit", "pnl"
            ])
        writer.writerow([
            datetime.now().strftime("%H:%M:%S"),
            symbol, strike, side, qty, entry, exit_price, pnl
        ])
