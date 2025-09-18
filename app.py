import streamlit as st
import time, hmac, hashlib, requests
import os

# API কী এবং সিক্রেট Streamlit secrets থেকে নেবে (লাইভে সেট করবেন)
API_KEY = st.secrets.get("DELTA_API_KEY", "4gk9aExJL9nFgNKXZ80CYFMKqKaqNN")
API_SECRET = st.secrets.get("DELTA_API_SECRET", "GNia87uLC5G3D1Zbmy54cHAcedngnRj0A4H3R3X4gA5IMJucbQlx8L1fwpT3")
BASE_URL = "https://cdn-ind.testnet.deltaex.org"

def test_api_connection(path):
    query = ""
    url = BASE_URL + path
    timestamp = str(int(time.time()))
    method = "GET"
    body = ""
    signature_payload = method + timestamp + path + query + body
    signature = hmac.new(
        API_SECRET.encode(),
        signature_payload.encode(),
        hashlib.sha256
    ).hexdigest()
    headers = {
        "api-key": API_KEY,
        "timestamp": timestamp,
        "signature": signature,
        "User-Agent": "python-3.12"
    }
    try:
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        st.write("Server response:", r.text)  # ডিবাগ: সম্পূর্ণ রেসপন্স দেখাবে
        return r.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"⚠️ HTTP Error for {path}: {e}")
        if e.response.status_code == 401:
            st.error("   সম্ভাব্য সমস্যা: অগত্যা API কী, IP whitelisting, বা ৫ মিনিট অপেক্ষা।")
        return None
    except Exception as e:
        st.error(f"⚠️ সাধারণ ত্রুটি for {path}: {str(e)}")
        return None

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
        st.markdown(f"<div style='background: #e0f7fa; border-radius: 8px; padding: 8px; margin-bottom: 6px;'><b>💰 {asset}:</b> {balance}</div>", unsafe_allow_html=True)

st.markdown("""
<h1 style='color:#1976d2; text-align:center; margin-bottom: 0;'>Delta Exchange API Fetcher</h1>
<hr style='margin-top:0; margin-bottom:1.5em;'>
""", unsafe_allow_html=True)

with st.spinner("ডেটা ফেচ করা হচ্ছে..."):
    positions_data = test_api_connection("/v2/positions/margined")
    if positions_data:
        st.subheader("ওপেন পজিশন")
        pretty_print_positions(positions_data)
    balances_data = test_api_connection("/v2/wallet/balances")
    if balances_data:
        st.subheader("ওয়ালেট ব্যালেন্স")
        print_wallet_balances(balances_data)

