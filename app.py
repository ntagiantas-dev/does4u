import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import threading
import asyncio

# --- CONFIGURATION ---"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1o9GrbNipQV-q1vfTYLdeD3vbs7HtKHftgeq3P11XwcU/edit?usp=sharing"
# Σύνδεση με Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Διαβάζουμε το Token από τα Streamlit Secrets
# Στα Secrets έχεις βάλει: HTTP_API_KEY = "..."
TOKEN = st.secrets["HTTP_API_KEY"]

st.set_page_config(page_title="Does4u Pro", layout="wide")

# --- INITIALIZATION ---
if 'df' not in st.session_state: st.session_state.df = pd.DataFrame()
if 'is_optimized' not in st.session_state: st.session_state.is_optimized = False

# Σύνδεση με το Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- BOT LOGIC ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    # Προσθήκη στο Google Sheet
    df_current = conn.read(spreadsheet=SHEET_URL)
    new_row = pd.DataFrame({
        'address': [text], 
        'city': ['N/A'], 
        'postal code': ['N/A'], 
        'status': ['Pending'], 
        'type': ['Παράδοση']
    })
    updated_df = pd.concat([df_current, new_row], ignore_index=True)
    conn.update(spreadsheet=SHEET_URL, data=updated_df)
    await update.message.reply_text(f"✅ Η στάση '{text}' προστέθηκε!")

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.run_polling()

# Εκκίνηση του Bot σε ξεχωριστό thread
if 'bot_started' not in st.session_state:
    threading.Thread(target=run_bot, daemon=True).start()
    st.session_state.bot_started = True

# --- UI ---
st.title("🚚 Does4u - Professional Driver Portal")

if st.button("🔄 Ανανέωση από Sheets"):
    st.session_state.df = conn.read(spreadsheet=SHEET_URL)
    st.rerun()

if not st.session_state.df.empty:
    st.dataframe(st.session_state.df)
else:
    st.write("Πατήστε ανανέωση για να δείτε τις στάσεις.")

st.info("Το Telegram Bot είναι ενεργό. Στείλε διευθύνσεις στο bot σου για να πάνε στο Sheet!")