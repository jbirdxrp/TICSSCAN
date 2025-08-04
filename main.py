from flask import Flask, render_template
import requests
import threading
import time
from config import BOT_TOKEN, CHAT_ID, VALIDATOR_ADDRESS
import telegram

app = Flask(__name__)
status_data = {"status": "Unknown", "tokens": "0", "commission": "0", "jailed": False}

def fetch_status():
    global status_data
    url = f"https://swagger.qubetics.com/cosmos/staking/v1beta1/validators/{VALIDATOR_ADDRESS}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()["validator"]
            status_data = {
                "status": data["status"],
                "tokens": data["tokens"],
                "commission": data["commission"]["commission_rates"]["rate"],
                "jailed": data["jailed"]
            }
    except Exception as e:
        print("Error fetching validator data:", e)

def monitor_validator():
    bot = telegram.Bot(token=BOT_TOKEN)
    last_status = None
    while True:
        fetch_status()
        if status_data["status"] != last_status:
            last_status = status_data["status"]
            msg = f"Validator Status Update:\nStatus: {status_data['status']}\nTokens: {status_data['tokens']}\nCommission: {status_data['commission']}\nJailed: {status_data['jailed']}"
            try:
                bot.send_message(chat_id=CHAT_ID, text=msg)
            except Exception as e:
                print("Telegram send error:", e)
        time.sleep(300)

@app.route("/")
def index():
    return render_template("index.html", status=status_data)

if __name__ == "__main__":
    threading.Thread(target=monitor_validator, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
