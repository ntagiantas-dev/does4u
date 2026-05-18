import streamlit as st
import requests
from openai import OpenAI
import json
import sqlite3
import pandas as pd
import urllib.parse

# Ρύθμιση Σελίδας
st.set_page_config(page_title="Does4U - All Matches v0.0.15", page_icon="🎯", layout="wide")
st.title("🎯 Does4U Omni-Source Sniper v0.0.15")
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

# Αρχικοποίηση βάσης
init_db()

XING_URL = "https://www.xing.com/jobs/search?keywords=python%20freelance"
TWITTER_SEARCH_QUERY = 'site:x.com "python freelance" OR "looking for python developer" OR "need a python script"'
X_GOOGLE_URL = f"https://www.google.com/search?q={urllib.parse.quote(TWITTER_SEARCH_QUERY)}&tbs=qdr:w"

col_actions, col_history = st.columns([1, 2])

with col_actions:
    st.subheader("🎯 Επιλογή Σκαναρίσματος")
    
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
                    prompt = "Analyse the text for Python Freelance projects. We ONLY want matches with a specific company name. Return STRICT JSON format: {'matches': [{'title_gr': 'Title', 'client_company_keyword': 'Company', 'project_link': 'Link', 'summary_gr': 'Summary'}]}"
                    
                    ai_response = openai_client.chat.completions.create(
                        model="gpt-4o-mini", response_format={"type": "json_object"},
                        messages=[{"role": "user", "content": f"{prompt}\n\nΚείμενο:\n{response.text}"}], temperature=0.1
                    )
                    
                    ai_data = json.loads(ai_response.choices[0].message.content)
                    matches = ai_data.get("matches", [])
                    
                    saved = 0
                    for item in matches:
                        if save_match("XING", item.get('client_company_keyword', 'N/A'), item.get('title_gr', 'N/A'), item.get('summary_gr', 'N/A'), item.get('project_link', '')): 
                            saved += 1
                    st.success(f"🔥 Xing: Αποθηκεύτηκαν {saved} νέα matches!")
                    st.rerun()
            else:
                st.error(f"❌ Σφάλμα Jina (Status Code: {response.status_code})")
        except Exception as e: 
            st.error(f"🚨 Σφάλμα κατά την επεξεργασία του Xing: {e}")
            
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
                    Analyse the Google Search results text. Look for real tweets on x.com from users looking for Python Developers, Freelancers, Scripts, Automation, or Scraping.
                    Return STRICT JSON format:
                    {
                        "matches": [
                            {
                                "title_gr": "Σύντομος τίτλος στα Ελληνικά",
                                "client_company_keyword": "@Username του χρήστη",
                                "project_link": "Full link of the tweet on x.com",
                                "summary_gr": "Σύνοψη στα Ελληνικά"
                            }
                        ]
                    }
                    """
                    ai_response = openai_client.chat.completions.create(
                        model="gpt-4o-mini", response_format={"type": "json_object"},
                        messages=[{"role": "user", "content": f"{prompt}\n\nΚείμενο:\n{response.text}"}], temperature=0.1
                    )
                    
                    ai_data = json.loads(ai_response.choices[0].message.content)
                    matches = ai_data.get("matches", [])
                    
                    saved = 0
                    for item in matches:
                        # ΔΙΟΡΘΩΣΗ: Χρήση .get() για ασφάλεια και σωστά keys
                        company_name = item.get('client_company_keyword', '@Unknown')
                        if save_match("X (Twitter)", company_name, item.get('title_gr', 'N/A'), item.get('summary_gr', 'N/A'), item.get('project_link', '')): 
                            saved += 1
                    st.success(f"🔥 X (Twitter): Αποθηκεύτηκαν {saved} νέα matches!")
                    st.rerun()
            else:
                st.error(f"❌ Σφάλμα Jina (Status Code: {response.status_code})")
        except Exception as e: 
            st.error(f"🚨 Σφάλμα κατά την επεξεργασία του Twitter: {e}")

# --- ΕΜΦΑΝΙΣΗ ΕΝΙΑΙΟΥ ΠΙΝΑΚΑ ΙΣΤΟΡΙΚΟΥ ---
with col_history:
    st.subheader("🗄️ Συγκεντρωτικός Πίνακας Matches")
    try:
        df_history = get_last_50_matches()
        
        if df_history.empty:
            st.info("Η βάση δεδομένων είναι άδεια. Επίλεξε μια πηγή από αριστερά για να ξεκινήσεις!")
        else:
            csv = df_history.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 Κατέβασε τη βάση σε CSV (Excel)", data=csv, file_name="all_matches.csv", mime="text/csv")
            st.markdown("---")
            
            st.dataframe(
                df_history, 
                use_container_width=True,
                column_config={
                    "Link Αγγελίας": st.column_config.LinkColumn("Link Αγγελίας")
                }
            )
    except Exception as e:
        st.error(f"🚨 Σφάλμα εμφάνισης πίνακα: {e}")