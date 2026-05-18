import streamlit as st
import requests
from openai import OpenAI
import json
import sqlite3
import pandas as pd

# Ρύθμιση Σελίδας
st.set_page_config(page_title="Does4U - Xing Sniper v0.0.19", page_icon="🎯", layout="wide")
st.title("🎯 Does4U Xing Sniper v0.0.19")
st.subheader("Η επιτυχημένη έκδοση (9/9 Matches) - Μόνο Πίνακας")

# --- ΒΑΣΗ ΔΕΔΟΜΕΝΩΝ (Αποκλειστικά για Xing Matches) ---
DB_FILE = "does4u_xing_success.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            title TEXT,
            summary TEXT,
            link TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_lead(company, title, summary, link):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Έλεγχος για διπλότυπα βάσει link
    cursor.execute("SELECT id FROM leads WHERE link = ?", (link,))
    exists = cursor.fetchone()
    if not exists:
        cursor.execute("""
            INSERT INTO leads (company, title, summary, link)
            VALUES (?, ?, ?, ?)
        """, (company, title, summary, link))
        conn.commit()
        return True
    return False

def get_last_50_leads():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("""
        SELECT company AS 'Εταιρεία', 
               title AS 'Τίτλος Project', 
               summary AS 'Σύνοψη (GR)', 
               link AS 'Link Αγγελίας', 
               timestamp AS 'Ημ/νία Καταγραφής' 
        FROM leads 
        ORDER BY id DESC LIMIT 50
    """, conn)
    conn.close()
    return df

# Αρχικοποίηση της βάσης
init_db()

XING_TARGET_URL = "https://www.xing.com/jobs/search?keywords=python%20freelance"

col_actions, col_history = st.columns([1, 2])

with col_actions:
    st.subheader("🎯 Νέο Σκανάρισμα")
    
    if st.button("🚀 ΕΝΑΡΞΗ ΑΥΣΤΗΡΟΥ MATCH"):
        try:
            JINA_API_KEY = st.secrets["JINA_API_KEY"]
            OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
            
            st.write("📡 Η Jina AI φέρνει τα δεδομένα από το Xing...")
            jina_endpoint = f"https://r.jina.ai/{XING_TARGET_URL}"
            headers = {"Authorization": f"Bearer {JINA_API_KEY}", "X-Return-Format": "markdown"}
            response = requests.get(jina_endpoint, headers=headers)
            
            if response.status_code == 200:
                raw_markdown = response.text
                with st.spinner("Το GPT-4o-mini φιλτράρει με το επιτυχημένο prompt..."):
                    openai_client = OpenAI(api_key=OPENAI_API_KEY)
                    
                    # Εδώ είναι το ακριβές prompt που σου έβγαλε τα 9 matches!
                    prompt = """
                    Ανάλυσε το Markdown του Xing για Python Freelance/One-off projects.
                    
                    ΚΑΝΟΝΑΣ MATCHING:
                    1. Αν βρεις το ακριβές όνομα της εταιρείας ή το όνομα του recruiter, βάλε "has_match": 1.
                    2. Αν το όνομα της εταιρείας είναι κρυφό, ανώνυμο ή γράφει απλώς "Recruiting Agency" χωρίς όνομα, βάλε "has_match": 0.
                    
                    Επέστρεψε ΑΥΣΤΗΡΑ JSON:
                    {
                        "leads": [
                            {
                                "title_gr": "Τίτλος στα Ελληνικά",
                                "client_company_keyword": "Όνομα Εταιρείας",
                                "project_link": "Link αγγελίας",
                                "summary_gr": "Σύνοψη στα Ελληνικά",
                                "has_match": 1
                            }
                        ]
                    }
                    """
                    
                    ai_response = openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        response_format={"type": "json_object"},
                        messages=[{"role": "user", "content": f"{prompt}\n\nΚείμενο:\n{raw_markdown}"}],
                        temperature=0.1
                    )
                    
                    ai_data = json.loads(ai_response.choices[0].message.content)
                    leads_list = ai_data.get("leads", [])
                    
                    saved_count = 0
                    for lead in leads_list:
                        # Κρατάμε ΜΟΝΟ όσα έχουν has_match == 1 (Αυστηρό φιλτράρισμα στην πράξη!)
                        if int(lead.get('has_match', 0)) == 1:
                            was_saved = save_lead(
                                lead['client_company_keyword'],
                                lead['title_gr'],
                                lead['summary_gr'],
                                lead['project_link']
                            )
                            if was_saved:
                                saved_count += 1
                                
                    if saved_count > 0:
                        st.success(f"🔥 Βρέθηκαν και αποθηκεύτηκαν {saved_count} νέα καθαρά Matches!")
                        st.rerun()
                    else:
                        st.warning("⚠️ Δεν βρέθηκαν νέα matches που να μην υπάρχουν ήδη στη βάση.")
            else:
                st.error(f"❌ Σφάλμα Jina API: {response.status_code}")
                
        except Exception as e:
            st.error(f"🚨 Κάτι πήγε στραβά: {e}")

# --- ΕΜΦΑΝΙΣΗ ΚΑΘΑΡΟΥ ΠΙΝΑΚΑ ΙΣΤΟΡΙΚΟΥ (ΔΕΞΙΑ) ---
with col_history:
    st.subheader("🗄️ Πίνακας Ιστορικού (Μόνο Matches)")
    df_history = get_last_50_leads()
    
    if df_history.empty:
        st.info("Η βάση δεδομένων είναι έτοιμη και άδεια. Κάνε ένα σκανάρισμα αριστερά!")
    else:
        csv = df_history.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Download CSV (Excel)", data=csv, file_name="xing_pure_matches.csv", mime="text/csv")
        
        st.dataframe(
            df_history, 
            use_container_width=True,
            column_config={
                "Link Αγγελίας": st.column_config.LinkColumn("Link Αγγελίας")
            }
        )