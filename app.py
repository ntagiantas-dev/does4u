import streamlit as st
import requests
from openai import OpenAI
import sqlite3
import pandas as pd
import urllib.parse

# Ρύθμιση Σελίδας
st.set_page_config(page_title="Does4U - Eco Sniper v0.0.17", page_icon="🎯", layout="wide")
st.title("🎯 Does4U Eco Omni-Sniper v0.0.17")
st.subheader("Οικονομικό σκανάρισμα με GPT-4o-Mini & Text-Parsing")

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
            
            st.write("📡 Η Jina AI μαζεύει το Xing...")
            # ΔΙΟΡΘΩΣΗ: Ζητάμε απλό κείμενο χωρίς τη σαβούρα του HTML/Markdown
            headers = {"Authorization": f"Bearer {JINA_API_KEY}", "X-Respond-With": "text"}
            response = requests.get(f"https://r.jina.ai/{XING_URL}", headers=headers)
            
            if response.status_code == 200:
                with st.spinner("Το GPT-4o-mini αναλύει (Eco Mode)..."):
                    openai_client = OpenAI(api_key=OPENAI_API_KEY)
                    
                    prompt = """
                    Ανάλυσε το κείμενο και βρες Python Freelance projects που έχουν συγκεκριμένο όνομα εταιρείας.
                    Για κάθε project που βρεις, γράψε τα στοιχεία του ΑΥΣΤΗΡΑ στην παρακάτω μορφή (μην βάλεις τίποτα άλλο, ούτε JSON, ούτε bullet points):
                    COMPANY: [Όνομα Εταιρείας]
                    TITLE: [Τίτλος Project]
                    LINK: [Link Αγγελίας]
                    SUMMARY: [Σύνοψη στα Ελληνικά]
                    ---
                    """
                    
                    ai_response = openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": f"{prompt}\n\nΚείμενο:\n{response.text}"}],
                        temperature=0.1
                    )
                    
                    raw_text = ai_response.choices[0].message.content
                    blocks = raw_text.split("---")
                    
                    saved = 0
                    for block in blocks:
                        if "COMPANY:" in block and "LINK:" in block:
                            lines = block.strip().split("\n")
                            data = {}
                            for line in lines:
                                if line.startswith("COMPANY:"): data['company'] = line.replace("COMPANY:", "").strip()
                                elif line.startswith("TITLE:"): data['title'] = line.replace("TITLE:", "").strip()
                                elif line.startswith("LINK:"): data['link'] = line.replace("LINK:", "").strip()
                                elif line.startswith("SUMMARY:"): data['summary'] = line.replace("SUMMARY:", "").strip()
                            
                            if data.get('link'):
                                if save_match("XING", data.get('company', 'N/A'), data.get('title', 'N/A'), data.get('summary', 'N/A'), data['link']):
                                    saved += 1
                                    
                    st.success(f"🔥 Xing: Αποθηκεύτηκαν {saved} νέα matches!")
                    st.rerun()
            else:
                st.error(f"❌ Σφάλμα Jina: {response.status_code}")
        except Exception as e:
            st.error(f"🚨 Σφάλμα: {e}")
            
    st.markdown("---")
    
    # --- ΚΟΥΜΠΙ 2: X (TWITTER) ---
    if st.button("🐦 Σκανάρισμα X (TWITTER)"):
        try:
            JINA_API_KEY = st.secrets["JINA_API_KEY"]
            OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
            
            st.write("📡 Η Jina AI σκανάρει τη Google...")
            headers = {"Authorization": f"Bearer {JINA_API_KEY}", "X-Respond-With": "text"}
            response = requests.get(f"https://r.jina.ai/{X_GOOGLE_URL}", headers=headers)
            
            if response.status_code == 200:
                with st.spinner("Το GPT-4o-mini απομονώνει Tweets (Eco Mode)..."):
                    openai_client = OpenAI(api_key=OPENAI_API_KEY)
                    
                    prompt = """
                    Ανάλυσε το κείμενο της Google. Βρες πραγματικά tweets από χρήστες που ζητάνε Python freelancers/scripts.
                    Για κάθε έγκυρο tweet, γράψε τα στοιχεία ΑΥΣΤΗΡΑ στην παρακάτω μορφή:
                    COMPANY: [Το @Username του χρήστη]
                    TITLE: [Σύντομο θέμα στα Ελληνικά]
                    LINK: [Το link του tweet στο x.com]
                    SUMMARY: [Σύνοψη τι ζητάει στα Ελληνικά]
                    ---
                    """
                    
                    ai_response = openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": f"{prompt}\n\nΚείμενο:\n{response.text}"}],
                        temperature=0.1
                    )
                    
                    raw_text = ai_response.choices[0].message.content
                    blocks = raw_text.split("---")
                    
                    saved = 0
                    for block in blocks:
                        if "COMPANY:" in block and "LINK:" in block:
                            lines = block.strip().split("\n")
                            data = {}
                            for line in lines:
                                if line.startswith("COMPANY:"): data['company'] = line.replace("COMPANY:", "").strip()
                                elif line.startswith("TITLE:"): data['title'] = line.replace("TITLE:", "").strip()
                                elif line.startswith("LINK:"): data['link'] = line.replace("LINK:", "").strip()
                                elif line.startswith("SUMMARY:"): data['summary'] = line.replace("SUMMARY:", "").strip()
                            
                            if data.get('link'):
                                if save_match("X (Twitter)", data.get('company', '@Unknown'), data.get('title', 'N/A'), data.get('summary', 'N/A'), data['link']):
                                    saved += 1
                                    
                    st.success(f"🔥 X (Twitter): Αποθηκεύτηκαν {saved} νέα matches!")
                    st.rerun()
            else:
                st.error(f"❌ Σφάλμα Jina: {response.status_code}")
        except Exception as e:
            st.error(f"🚨 Σφάλμα: {e}")

# --- ΕΜΦΑΝΙΣΗ ΕΝΙΑΙΟΥ ΠΙΝΑΚΑ ΙΣΤΟΡΙΚΟΥ ---
with col_history:
    st.subheader("🗄️ Συγκεντρωτικός Πίνακας Matches")
    try:
        df_history = get_last_50_matches()
        if df_history.empty:
            st.info("Η βάση δεδομένων είναι άδεια. Επίλεξε μια πηγή από αριστερά!")
        else:
            csv = df_history.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 Κατέβασε τη βάση σε CSV", data=csv, file_name="all_matches.csv", mime="text/csv")
            st.markdown("---")
            st.dataframe(df_history, use_container_width=True, column_config={"Link Αγγελίας": st.column_config.LinkColumn("Link Αγγελίας")})
    except Exception as e:
        st.error(f"🚨 Σφάλμα πίνακα: {e}")