import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_gsheets import GSheetsConnection
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import threading
import asyncio

# --- CONFIGURATION ---
SHEET_URL = "ΒΑΛΕ_ΕΔΩ_ΤΟ_URL_ΤΟΥ_GOOGLE_SHEET_ΣΟΥ"
TOKEN = "8379012114:AAGWdCPzrdO31VOlTe-BUXH0eOI2kPCCvm4"

st.set_page_config(page_title="Does4u Pro", layout="wide")

# --- INITIALIZATION ---
if 'df' not in st.session_state: st.session_state.df = pd.DataFrame()
if 'is_optimized' not in st.session_state: st.session_state.is_optimized = False
if 'depot_info' not in st.session_state: st.session_state.depot_info = None
if 'route_info' not in st.session_state: st.session_state.route_info = {'total_time': 0, 'eta': None}

conn = st.connection("gsheets", type=GSheetsConnection)

# --- BOT LOGIC ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    # Προσθήκη στο Google Sheet
    df_current = conn.read(spreadsheet=SHEET_URL)
    new_row = pd.DataFrame({'address': [text], 'city': ['N/A'], 'postal code': ['N/A'], 'status': ['Pending'], 'type': ['Παράδοση']})
    updated_df = pd.concat([df_current, new_row], ignore_index=True)
    conn.update(spreadsheet=SHEET_URL, data=updated_df)
    await update.message.reply_text(f"✅ Η στάση '{text}' προστέθηκε!")

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.run_polling()

if 'bot_started' not in st.session_state:
    threading.Thread(target=run_bot, daemon=True).start()
    st.session_state.bot_started = True

# --- FUNCTIONS (OLD LOGIC KEPT) ---
def validate_and_process(df):
    required = ['address', 'city', 'postal code']
    if not all(col in df.columns for col in required): return False, "Λείπουν στήλες"
    df['status'] = 'Pending'; df['type'] = 'Παράδοση'
    return True, df

def optimize_route_logic(depot_addr, depot_city, depot_zip):
    df_data = conn.read(spreadsheet=SHEET_URL)
    pending = df_data[df_data['status'] == 'Pending']
    optimized_pending = pending.sort_values(by='address')
    st.session_state.df = optimized_pending
    st.session_state.is_optimized = True

# --- UI (OLD LOGIC KEPT) ---
st.title("🚚 Does4u - Professional Driver Portal")
# Εδώ διαβάζουμε είτε από Sheet είτε από File
if st.button("🔄 Ανανέωση από Sheets"):
    st.session_state.df = conn.read(spreadsheet=SHEET_URL)

st.dataframe(st.session_state.df)

with st.sidebar:
    st.write("### 🛠️ Εργαλεία")
    if st.session_state.is_optimized:
        st.metric("⏳ Κατάσταση", "Βελτιστοποιημένη")
    
    with st.expander("📍 Ορισμός Αφετηρίας"):
        with st.form("depot_form"):
            d_a = st.text_input("Διεύθυνση")
            if st.form_submit_button("🚀 Εκτέλεση"):
                optimize_route_logic(d_a, "Πόλη", "ΤΚ")
                st.rerun()

st.info("Το Telegram Bot είναι ενεργό. Στείλε διευθύνσεις στο bot σου για να πάνε στο Sheet!")