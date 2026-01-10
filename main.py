from logger import log_trade
import time
import datetime
import math
import os
import requests
import pandas as pd

# =====================
# CONFIG
# =====================
INDEX = "NIFTY"
LOT_SIZE = 2
LOT_MULTIPLIER = 65
QTY = LOT_SIZE * LOT_MULTIPLIER

TARGET_SELL_DELTA = 0.6
TARGET_HEDGE_DELTA = 0.05

# =====================
# TELEGRAM
# =====================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})

def log(msg):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

# =====================
# STATE
# =====================
ce_done = False
pe_done = False

# =====================
# MARKET DATA (PAPER)
# Replace later with real feed
# =====================
def get_nifty_spot():
    return 22500  # mock spot

def get_vwap():
    return 22480  # mock vwap

def get_option_chain(spot):
    strikes = range(spot - 1000, spot + 1000, 50)
    data = []

    for strike in strikes:
        distance = abs(strike - spot)
        delta = math.exp(-distance / 250)  # delta approximation

        data.append({
            "strike": strike,
            "delta": round(delta, 2)
        })

    return pd.DataFrame(data)

def pick_strike(df, target_delta):
    df["diff"] = abs(df["delta"] - target_delta)
    return df.sort_values("diff").iloc[0]

# =====================
# STRATEGY LOOP
# =====================
def run_strategy():
    global ce_done, pe_done

    log("VWAP BOT STARTED (PAPER MODE)")
    send_telegram("🚀 VWAP BOT STARTED (PAPER MODE)")

    while True:
        now = datetime.datetime.now().time()

        if now < datetime.time(9, 18) or now > datetime.time(15, 25):
            time.sleep(30)
            continue

        spot = get_nifty_spot()
        vwap = get_vwap()

        log(f"NIFTY={spot} | VWAP={vwap}")

        chain = get_option_chain(spot)
        sell_opt = pick_strike(chain, TARGET_SELL_DELTA)
        hedge_opt = pick_strike(chain, TARGET_HEDGE_DELTA)

        # =====================
        # CE SIDE
        # =====================
        if spot > vwap and not ce_done:
            ce_done = True

            msg = (
                f"📈 VWAP BREAK UP\n"
                f"SELL CE {sell_opt['strike']} (Δ {sell_opt['delta']})\n"
                f"BUY HEDGE CE {hedge_opt['strike']} (Δ {hedge_opt['delta']})\n"
                f"QTY: {QTY}"
            )

            log("CE TRADE SELECTED")
            send_telegram(msg)

        # =====================
        # PE SIDE
        # =====================
        if spot < vwap and not pe_done:
            pe_done = True

            msg = (
                f"📉 VWAP BREAK DOWN\n"
                f"SELL PE {sell_opt['strike']} (Δ {sell_opt['delta']})\n"
                f"BUY HEDGE PE {hedge_opt['strike']} (Δ {hedge_opt['delta']})\n"
                f"QTY: {QTY}"
            )

            log("PE TRADE SELECTED")
            send_telegram(msg)

        time.sleep(180)

if __name__ == "__main__":
    run_strategy()
