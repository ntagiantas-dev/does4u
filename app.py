import streamlit as st
import requests
from openai import OpenAI
import json
import sqlite3
import pandas as pd
import urllib.parse

# Ρύθμιση Σελίδας
st.set_page_config(page_title="Does4U - All Matches v0.0.14", page_icon="🎯", layout="wide")
st.title("🎯 Does4U Omni-Source Sniper v0.0.14")
st.subheader("Συνδυασμένα αποτελέσματα από Xing και X (Twitter) στον ίδιο πίνακα")

# --- ΚΟΙΝΗ ΒΑΣΗ ΔΕΔΟΜΕΝΩΝ ---
DB_FILE = "does4u_all_matches.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            company TEXT,
            title TEXT,
            summary TEXT,
            link TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_match(source, company, title, summary, link):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Έλεγχος μοναδικότητας βάσει link για να μην έχουμε ποτέ διπλότυπα
    cursor.execute("SELECT id FROM matches WHERE link = ?", (link,))
    exists = cursor.fetchone()
    if not exists:
        cursor.execute("""
            INSERT INTO matches (source, company, title, summary, link)
            VALUES (?, ?, ?, ?, ?)
        """, (source, company, title, summary, link))
        conn.commit()
        return True
    return False

def get_last_50_matches():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("""
        SELECT source AS 'Πηγή',
               company AS 'Εταιρεία / User', 
               title AS 'Τίτλος / Θέμα', 
               summary AS 'Σύνοψη (GR)', 
               link AS 'Link Αγγελίας', 
               timestamp AS 'Ώρα Καταγραφής' 
        FROM matches 
        ORDER BY id DESC LIMIT 50
    """, conn)
    conn.close()
    return df

# Αρχικοποίηση της κοινής βάσης
init_db()

# URLs Αναζήτησης
XING_URL = "https://www.xing.com/jobs/search?keywords=python%20freelance"
TWITTER_SEARCH_QUERY = 'site:x.com "python freelance" OR "looking for python developer" OR "need a python script"'
X_GOOGLE_URL = f"https://www.google.com/search?q={urllib.parse.quote(TWITTER_SEARCH_QUERY)}&tbs=qdr:w"

col_actions, col_history = st.columns([1, 2])

with col_actions:
    st.subheader("🎯 Επιλογή Σκαναρίσματος")
    st.caption("Πάτα το αντίστοιχο κουμπί για να τρέξει το σκανάρισμα της πηγής που θες.")
    
    # --- ΚΟΥΜΠΙ 1: XING ---
    if st.button("🇩🇪 Σκανάρισμα XING"):
        try:
            JINA_API_KEY = st.secrets["JINA_API_KEY"]
            OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
            
            st.write("📡 Η Jina AI σκανάρει το Xing...")
            response = requests.get(f"https://r.jina.ai/{XING_URL}", headers={"Authorization": f"Bearer {JINA_API_KEY}", "X-Return-Format": "markdown"})
            
            if response.status_code == 200:
                with st.spinner("Το GPT αναλύει τα δεδομένα του Xing..."):
                    openai_client = OpenAI(api_key=OPENAI_API_KEY)
                    prompt = "Analyse the text for Python Freelance projects. We ONLY want matches with a specific company name. Return STRICT JSON: {'matches': [{'title_gr': 'Title', 'client_company_keyword': 'Company', 'project_link': 'Link', 'summary_gr': 'Summary'}]}"
                    ai_response = openai_client.chat.completions.create(
                        model="gpt-4o-mini", response_format={"type": "json_object"},
                        messages=[{"role": "user", "content": f"{prompt}\n\nΚείμενο:\n{response.text}"}], temperature=0.1
                    )
                    matches = json.loads(ai_response.choices[0].message.content).get("matches", [])
                    
                    saved = 0
                    for item in matches:
                        # Αποθήκευση με ένδειξη "XING"
                        if save_match("XING", item['client_company_keyword'], item['title_gr'], item['summary_gr'], item['project_link']): 
                            saved += 1
                    st.success(f"🔥 Xing: Αποθηκεύτηκαν {saved} νέα matches!")
                    st.rerun()
        except Exception as e: st.error(f"🚨 Σφάλμα Xing: {e}")
            
    st.markdown("---")
    
    # --- ΚΟΥΜΠΙ 2: X (TWITTER) ---
    if st.button("🐦 Σκανάρισμα X (TWITTER)"):
        try:
            JINA_API_KEY = st.secrets["JINA_API_KEY"]
            OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
            
            st.write("📡 Η Jina AI σκανάρει τη Google για πρόσφατα Tweets...")
            response = requests.get(f"https://r.jina.ai/{X_GOOGLE_URL}", headers={"Authorization": f"Bearer {JINA_API_KEY}", "X-Return-Format": "markdown"})
            
            if response.status_code == 200:
                with st.spinner("Το GPT απομονώνει valid tweets..."):
                    openai_client = OpenAI(api_key=OPENAI_API_KEY)
                    prompt = """
                    Ανάλυσε το κείμενο. Ψάχνουμε για πραγματικά Tweets στο x.com από άτομα που ζητάνε Python Developers, Scripts, Automation ή Scraping.
                    Θέλουμε μόνο tweets με συγκεκριμένο χρήστη (π.χ. @Username ή το όνομά του).
                    Επέστρεψε ΑΥΣΤΗΡΑ JSON: 
                    {'matches': [{'title_gr': 'Τίτλος', 'client_company_keyword': '@Username', 'project_link': 'Link στο x.com', 'summary_gr': 'Σύνοψη'}]}
                    """
                    ai_response = openai_client.chat.completions.create(
                        model="gpt-4o-mini", response_format={"type": "json_object"},
                        messages=[{"role": "user", "content": f"{prompt}\n\nΚείμενο:\n{response.text}"}], temperature=0.1
                    )
                    matches = json.loads(ai_response.choices[0].message.content).get("matches", [])
                    
                    saved = 0
                    for item in matches:
                        # Αποθήκευση με ένδειξη "X (Twitter)"
                        if save_match("X (Twitter)", item['client_company_keyword'], item['title_gr'], item['summary_gr'], item['project_link']): 
                            saved += 1
                    st.success(f"🔥 X (Twitter): Αποθηκεύτηκαν {saved} νέα matches!")
                    st.rerun()
            else:
                st.error(f"❌ Σφάλμα Jina API: {response.status_code}")
        except Exception as e: st.error(f"🚨 Σφάλμα Twitter: {e}")

# --- ΕΜΦΑΝΙΣΗ ΕΝΙΑΙΟΥ ΠΙΝΑΚΑ ΙΣΤΟΡΙΚΟΥ ---
with col_history:
    st.subheader("🗄️ Συγκεντρωτικός Πίνακας Matches")
    df_history = get_last_50_matches()
    
    if df_history.empty:
        st.info("Η βάση δεδομένων είναι άδεια. Επίλεξε μια πηγή από αριστερά για να ξεκινήσεις!")
    else:
        csv = df_history.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Κατέβασε τη βάση σε CSV (Excel)", data=csv, file_name="all_matches.csv", mime="text/csv")
        st.markdown("---")
        
        # Ο πίνακας δείχνει πλέον στην πρώτη στήλη αν το lead ήρθε από XING ή X (Twitter)
        st.dataframe(
            df_history, 
            use_container_width=True,
            column_config={
                "Link Αγγελίας": st.column_config.LinkColumn("Link Αγγελίας")
            }
        )