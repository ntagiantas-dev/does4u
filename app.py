import streamlit as st
import requests
from openai import OpenAI
import json
import sqlite3
import pandas as pd

# Ρύθμιση Σελίδας
st.set_page_config(page_title="Does4U - Lead Sniper DB v0.0.8", page_icon="🗄️", layout="wide")
st.title("🗄️ Does4U Lead Sniper με Μόνιμη Βάση Δεδομένων v0.0.8")

# --- ΣΥΝΔΕΣΗ ΚΑΙ ΔΗΜΙΟΥΡΓΙΑ ΒΑΣΗΣ ΔΕΔΟΜΕΝΩΝ (SQLite) ---
def init_db():
    conn = sqlite3.connect("does4u_leads.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            title TEXT,
            summary TEXT,
            link TEXT,
            email_content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_lead(company, title, summary, link, email_content):
    conn = sqlite3.connect("does4u_leads.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM leads WHERE link = ?", (link,))
    exists = cursor.fetchone()
    if not exists:
        cursor.execute("""
            INSERT INTO leads (company, title, summary, link, email_content)
            VALUES (?, ?, ?, ?, ?)
        """, (company, title, summary, link, email_content))
        conn.commit()
    conn.close()

def get_last_50_leads():
    conn = sqlite3.connect("does4u_leads.db")
    df = pd.read_sql_query("SELECT company, title, summary, link, email_content, timestamp FROM leads ORDER BY id DESC LIMIT 50", conn)
    conn.close()
    return df

# Αρχικοποίηση της DB πάντα στην αρχή
init_db()

XING_TARGET_URL = "https://www.xing.com/jobs/search?keywords=python%20freelance"

col_actions, col_history = st.columns([1, 1])

with col_actions:
    st.subheader("🎯 Νέο Σκανάρισμα")
    
    if st.button("🚀 ΕΝΑΡΞΗ & ΑΠΟΘΗΚΕΥΣΗ ΣΤΗ ΒΑΣΗ"):
        # ΔΙΟΡΘΩΣΗ: Ο έλεγχος μεταφέρθηκε ΕΔΩ, αφού πατηθεί το κουμπί!
        try:
            JINA_API_KEY = st.secrets["JINA_API_KEY"]
            OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
            
            st.write("📡 Η Jina AI σκανάρει το Xing...")
            jina_endpoint = f"https://r.jina.ai/{XING_TARGET_URL}"
            headers = {"Authorization": f"Bearer {JINA_API_KEY}", "X-Return-Format": "markdown"}
            response = requests.get(jina_endpoint, headers=headers)
            
            if response.status_code == 200:
                raw_markdown = response.text
                with st.spinner("Το GPT-4o-mini δημιουργεί τα leads..."):
                    openai_client = OpenAI(api_key=OPENAI_API_KEY)
                    prompt = """
                    Ψάξε στο Markdown για projects Python (Freelance, Junior, One-off, fixed price). Αποκλεισέ μόνιμες θέσεις.
                    Γράψε ένα έτοιμο Cold Email στα Αγγλικά για κάθε εταιρεία.
                    Επέστρεψε ΑΥΣΤΗΡΑ JSON:
                    {
                        "leads": [
                            {"title_gr": "Τίτλος", "client_company_keyword": "Εταιρεία", "project_link": "Link", "summary_gr": "Σύνοψη", "ready_email_en": "Email"}
                        ]
                    }
                    """
                    ai_response = openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        response_format={"type": "json_object"},
                        messages=[{"role": "user", "content": f"{prompt}\n\nΚείμενο:\n{raw_markdown}"}],
                        temperature=0.2
                    )
                    ai_data = json.loads(ai_response.choices[0].message.content)
                    leads_list = ai_data.get("leads", [])
                    
                    if len(leads_list) > 0:
                        for lead in leads_list:
                            save_lead(
                                lead['client_company_keyword'],
                                lead['title_gr'],
                                lead['summary_gr'],
                                lead['project_link'],
                                lead['ready_email_en']
                            )
                        st.success(f"🔥 Βρέθηκαν και αποθηκεύτηκαν {len(leads_list)} νέα leads στη βάση!")
                        st.rerun() # Κάνει αυτόματη ανανέωση για να εμφανιστούν αμέσως δεξιά στο ιστορικό!
                    else:
                        st.warning("⚠️ Δεν βρέθηκαν νέα one-off projects.")
            else:
                st.error(f"❌ Σφάλμα Jina API (Status Code: {response.status_code})")
                
        except KeyError:
            st.error("🚨 Σφάλμα: Λείπει το JINA_API_KEY ή το OPENAI_API_KEY από τα Secrets του Streamlit Cloud!")

# --- ΕΜΦΑΝΙΣΗ ΙΣΤΟΡΙΚΟΥ (ΔΕΞΙΑ ΣΤΗΝ ΟΘΟΝΗ) ---
with col_history:
    st.subheader("🗄️ Ιστορικό των Τελευταίων 50 Leads")
    history_df = get_last_50_leads()
    
    if history_df.empty:
        st.info("Η βάση δεδομένων είναι άδεια. Κάνε το πρώτο σκανάρισμα για να μαζέψεις δεδομένα!")
    else:
        csv = history_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Κατέβασε όλη τη Βάση σε CSV (Excel)",
            data=csv,
            file_name="does4u_leads_history.csv",
            mime="text/csv"
        )
        st.markdown("---")
        
        for idx, row in history_df.iterrows():
            with st.expander(f"🏢 {row['company']} - {row['title']}"):
                st.write(f"**Ημερομηνία Καταγραφής:** {row['timestamp']}")
                st.write(f"**Σύνοψη (GR):** {row['summary']}")
                st.markdown(f"[🔗 Link Αγγελίας]({row['link']})")
                st.markdown("**✉️ Έτοιμο Cold Email:**")
                st.text_area("Copy Email:", value=row['email_content'], height=150, key=f"hist_{idx}")