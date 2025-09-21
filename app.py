import streamlit as st
import time, hmac, hashlib, requests
import os
import time
import websocket
import json
from datetime import datetime, timezone, timedelta
import threading
from collections import defaultdict

# API কী এবং সিক্রেট Streamlit secrets থেকে নেবে (লাইভে সেট করবেন)
API_KEY = st.secrets.get("DELTA_API_KEY", "4gk9aExJL9nFgNKXZ80CYFMKqKaqNN")
API_SECRET = st.secrets.get("DELTA_API_SECRET", "GNia87uLC5G3D1Zbmy54cHAcedngnRj0A4H3R3X4gA5IMJucbQlx8L1fwpT3")
BASE_URL = "https://cdn-ind.testnet.deltaex.org"
BASE_URL2 = "https://testnet-api.delta.exchange"
# Testnet WebSocket URL
WS_URL = "wss://socket-ind.testnet.deltaex.org"

def test_api_connection(path, query=""):
    query = ""
    url = BASE_URL + path
    timestamp = str(int(time.time()))
    method = "GET"
    body = ""
    signature_payload = method + timestamp + path + query + body
    signature = hmac.new(API_SECRET.encode(), signature_payload.encode(), hashlib.sha256).hexdigest()

    headers = {
        "api-key": API_KEY,
        "timestamp": timestamp,
        "signature": signature,
        "Accept": "application/json",
        "User-Agent": "python-3.11"
    }
    
    try:
        r = requests.get(url, params={}, headers=headers, timeout=30)
        r.raise_for_status()  # HTTP এরর চেক
    
        # st.write("Server response:", r.json())

        data = r.json()
   
        if(path == "/v2/products"):
            st.success("✅ প্রোডাক্ট ডেটা সফলভাবে ফেচ হয়েছে!")
            st.write("Data fetched successfully")  # ডিবাগ: সফল ডেটা ফেচ মেসেজ
            return data
        else:
            return data    
    
    except requests.exceptions.HTTPError as e:
        st.error(f"⚠️ HTTP Error for {path}: {e}")
        if e.response.status_code == 401:
            st.error("   সম্ভাব্য সমস্যা: অগত্যা API কী, IP whitelisting, বা ৫ মিনিট অপেক্ষা।")
        return None
    except Exception as e:
        st.error(f"⚠️ সাধারণ ত্রুটি for {path}: {str(e)}")
        return None
    


def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json")
        ip = response.json()["ip"]
        return ip
    except Exception as e:
        return f"Error: {e}"
    
st.write("My public IP:", get_public_ip())


def pretty_print_positions(data):
    if not data or not data.get("success", False):
        st.error("❌ কোনো ওপেন পজিশন পাওয়া যায়নি।")
        return
    positions = data.get("result", [])
    if not positions:
        st.error("❌ কোনো ওপেন পজিশন পাওয়া যায়নি।")
        return
    for p in positions:
        symbol = p.get("product", {}).get("symbol") or p.get("product_symbol") or "UNKNOWN"
        size = p.get("size") or "N/A"
        entry_price = p.get("entry_price") or "N/A"
        mark_price = p.get("mark_price") or "N/A"
        unrealized_pnl = p.get("unrealized_pnl") or "0"
        st.write(f"🔹 **Symbol:** {symbol} | **Size:** {size} | **Entry:** {entry_price} | **Mark:** {mark_price} | **P/L:** {unrealized_pnl}")

def print_wallet_balances(data):
    if not data or not data.get("success", False):
        st.error("❌ ওয়ালেট ডেটা লোড করতে ব্যর্থ।")
        return
    balances = data.get("result", [])
    if not balances:
        st.info("   কোনো ব্যালেন্স পাওয়া যায়নি (নতুন টেস্টনেট অ্যাকাউন্টে স্বাভাবিক)।")
        return
    for bal in balances[:3]:
        asset = bal.get("asset_symbol", "UNKNOWN")
        balance = bal.get("balance", "0")
        balance_inr = bal.get("balance_inr", "0")
        st.markdown(f"<div style='background: #e0f7fa; border-radius: 8px; padding: 8px; margin-bottom: 6px;'><b>💰 {asset}:</b> {balance}<br> <b>💰 INR:</b> {balance_inr} </br></div>", unsafe_allow_html=True)





st.markdown("""
<h1 style='color:#1976d2; text-align:center; margin-bottom: 0;'>Delta Exchange API Fetcher</h1>
<hr style='margin-top:0; margin-bottom:1.5em;'>
""", unsafe_allow_html=True)


with st.spinner("ডেটা ফেচ করা হচ্ছে..."):
    balances_data = test_api_connection("/v2/wallet/balances")
    if balances_data:
        st.subheader("ওয়ালেট ব্যালেন্স")
        print_wallet_balances(balances_data)


        # funding_data = test_api_connection2("/v2/products")
        # st.write("Funding Data:", data["result"])
    # if data:
    #     funding_rates = [item.get("funding_rate", 0) for item in data["result"]]  # ধরে নিচ্ছি funding_rate আছে
        # st.line_chart({"Funding Rate": funding_rates})    

    positions_data = test_api_connection("/v2/positions/margined")
    if positions_data:
        st.subheader("ওপেন পজিশন")
        pretty_print_positions(positions_data)    










# if "funding_history" not in st.session_state:
#     st.session_state["funding_history"] = []

# def on_message(ws, message):
#     data = json.loads(message)
#     if data.get("type") == "funding_rate":
#         st.session_state["funding_history"].append(data)

# def start_ws():
#     ws = websocket.WebSocketApp(
#         WS_URL,
#         on_message=on_message,
#         on_error=lambda ws, err: st.error(err),
#         on_close=lambda ws, code, msg: st.write("🔴 WebSocket Closed"),
#         on_open=lambda ws: ws.send(json.dumps({
#             "type": "subscribe",
#             "payload": {"channels": [{"name": "funding_rate", "symbols": ["BTCUSD"]}]}
#         }))
#     )
#     ws.run_forever()

# # WebSocket start (once)
# if "ws_started" not in st.session_state:
#     threading.Thread(target=start_ws, daemon=True).start()
#     st.session_state["ws_started"] = True

# st.subheader("📡 Latest Funding Rate")

# # placeholder
# placeholder = st.empty()

# # Auto-refresh every 2 sec
# st_autorefresh = st.experimental_data_editor if hasattr(st, "experimental_data_editor") else None
# while True:
#     if st.session_state["funding_history"]:
#         latest = st.session_state["funding_history"][-1]
#         placeholder.json(latest)
#     else:
#         placeholder.write("⏳ Awaiting funding rate update...")
#     time.sleep(2)




# Initialize empty SYMBOLS list
if "SYMBOLS" not in st.session_state:
    st.session_state["SYMBOLS"] = []  # খালি list


# Function to add a new symbol
    def add_symbol(new_symbol):
        if new_symbol not in st.session_state["SYMBOLS"]:  # Prevent duplicates
            st.session_state["SYMBOLS"].append(new_symbol)








    data_products =test_api_connection("/v2/products")

    if data_products.get("success", False):
        # perpetual_futures = [item for item in data_products.get("result", []) if item.get("contract_type") == "perpetual_futures"]
        # if perpetual_futures:

        perpetual_futures = [item for item in data_products.get("result", []) if item.get("contract_type") == "perpetual_futures"]

    if perpetual_futures:
            st.write("Total Perpetual Futures:", len(perpetual_futures))
 
            data_tickers = test_api_connection("/v2/tickers")

            for contract in perpetual_futures: #[:5]: প্রথম ৫ কন্ট্রাক্টের জন্য
                symbol = contract.get("symbol")
                # leverage = contract.get("default_leverage", "N/A")

                add_symbol(symbol)  # SYMBOLS লিস্টে নতুন সিম্বল যোগ করুন

                # # Get price from tickers data
                ticker_data = next((item for item in data_tickers.get("result", []) if item.get("symbol") == symbol), None)
                price = ticker_data.get("mark_price", "N/A") if ticker_data else "N/A"
                # st.write(f"Raw Ticker Data for {symbol}: {ticker_data}")  # Debug individual data

                # Get funding rate from tickers data
                funding_rate = ticker_data.get("funding_rate", "N/A") if ticker_data else "N/A"

                st.write(f"Symbol: {symbol},  Price: {price}, Funding Rate: {funding_rate}")






def format_time_remaining(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}h:{minutes:02d}m:{secs:02d}s"

SYMBOLS = st.session_state["SYMBOLS"]

if SYMBOLS:
    st.success(f"✅ মোট {len(SYMBOLS)} সিম্বল ওয়াচলিস্টে যোগ হয়েছে।")


# SYMBOLS = ["BTCUSD", "ETHUSD"]

# THREAD-SAFE DICT
funding_latest_threadsafe = defaultdict(lambda: None)

# SESSION STATE INIT
if "ws_started" not in st.session_state:
    st.session_state["ws_started"] = False

# PLACEHOLDER
placeholder = st.empty()

# WEBSOCKET CALLBACKS
def on_message(ws, message):
    data = json.loads(message)
    if data.get("type") == "funding_rate":
        symbol = data.get("symbol")
        funding_latest_threadsafe[symbol] = data  # Only update dict

def on_open(ws):
    subscribe_msg = {
        "type": "subscribe",
        "payload": {"channels": [{"name": "funding_rate", "symbols": SYMBOLS}]}
    }
    ws.send(json.dumps(subscribe_msg))

def start_ws():
    ws = websocket.WebSocketApp(
        WS_URL,
        on_message=on_message,
        on_open=on_open
    )
    ws.run_forever()

if not st.session_state["ws_started"]:
    threading.Thread(target=start_ws, daemon=True).start()
    st.session_state["ws_started"] = True


# STREAMLIT UI
# st.title("📊 Latest Funding Rates")
while True:
    html_content = "<h2>📊 Latest Funding Rates</h2>"
    # html_content = ""
    for symbol in SYMBOLS:
        latest = funding_latest_threadsafe.get(symbol)
        html_content += f"<h3>🔹 {symbol}</h3>"
        if latest:

            


            # st.json(latest)  # ডিবাগ: কাঁচা ডেটা দেখাও
            # STREAMLIT UI


             # Convert timestamp
            # ts_seconds = latest['timestamp'] / 1000000  # মাইক্রোসেকেন্ড থেকে সেকেন্ডে
            # formatted_time = datetime.fromtimestamp(ts_seconds).strftime("%Hh:%Mm:%Ss")

            # next_funding_time = latest['timestamp'] / 10000  # মিলিসেকেন্ড থেকে সেকেন্ডে

            next_funding = latest.get('next_funding_realization', 0)
            next_funding_ts = next_funding / 1_000_000  # microseconds to seconds
            now_ts = datetime.now().timestamp()
            seconds_remaining = int(next_funding_ts - now_ts)
            formatted_time = format_time_remaining(seconds_remaining)
            # print(formatted_time)


            # Timestamp in microseconds
            timestamp_micro = latest.get('timestamp', 0)
            # Convert to seconds
            timestamp_sec = timestamp_micro / 1_000_000
            # Convert to datetime (UTC)
            update_time = datetime.fromtimestamp(timestamp_sec, tz=timezone.utc)
            # Convert to local timezone (IST: UTC+5:30)
            update_time_local = update_time + timedelta(hours=5, minutes=30)

            # print("Funding Update Time (UTC):", update_time.strftime("%Y-%m-%d %H:%M:%S"))
            # print("Funding Update Time (Local, IST):", update_time_local.strftime("%Y-%m-%d %H:%M:%S"))
            

            html_content += f"""
            <div style="background-color:#f0f8ff; padding:15px; border-radius:10px; margin-bottom:10px;">
                <b>Funding Rate:</b> {latest['funding_rate']} <br>
                <b>Funding Rate (8h):</b> {latest['funding_rate_8h']} <br>
                <b>Next Funding:</b>  {formatted_time} <br>
                <b>Predicted Funding Rate:</b> {latest['predicted_funding_rate']} <br>
                <b> Product ID:</b> {latest['product_id']} <br>
                <b> Product Funding Rate (8h):</b> {latest['predicted_funding_rate_8h']} <br>
                <b>Symbol:</b> {latest['symbol']} <br>
                <a><b>Timestamp: UTC :</b>{update_time.strftime("%Y-%m-%d %H:%M:%S")}<b> / Local, IST : </b>{update_time_local.strftime("%Y-%m-%d %H:%M:%S")}</a>
            </div>
            """
        else:
            html_content += "<p>⏳ Waiting for data...</p>"

    # REPLACE placeholder content every iteration
    placeholder.markdown(html_content, unsafe_allow_html=True)
    time.sleep(1) # আপডেট প্রতি 0.5 সেকেন্ডে
