import streamlit as st
import requests
from openai import OpenAI
import json
import sqlite3
import pandas as pd

# Ρύθμιση Σελίδας
st.set_page_config(page_title="Does4U - Strict Match v0.0.9", page_icon="🎯", layout="wide")
st.title("🎯 Does4U Strict Match & Draft v0.0.9")

# --- ΒΑΣΗ ΔΕΔΟΜΕΝΩΝ (SQLite) ---
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
            has_match INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_lead(company, title, summary, link, email_content, has_match):
    conn = sqlite3.connect("does4u_leads.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM leads WHERE link = ?", (link,))
    exists = cursor.fetchone()
    if not exists:
        cursor.execute("""
            INSERT INTO leads (company, title, summary, link, email_content, has_match)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (company, title, summary, link, email_content, has_match))
        conn.commit()
    conn.close()

def get_last_50_leads():
    conn = sqlite3.connect("does4u_leads.db")
    df = pd.read_sql_query("SELECT company, title, summary, link, email_content, has_match, timestamp FROM leads ORDER BY id DESC LIMIT 50", conn)
    conn.close()
    return df

init_db()

XING_TARGET_URL = "https://www.xing.com/jobs/search?keywords=python%20freelance"

col_actions, col_history = st.columns([1, 1])

with col_actions:
    st.subheader("🎯 Νέο Σκανάρισμα")
    
    if st.button("🚀 ΕΝΑΡΞΗ ΑΥΣΤΗΡΟΥ MATCH v0.0.9"):
        try:
            JINA_API_KEY = st.secrets["JINA_API_KEY"]
            OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
            
            st.write("📡 Η Jina AI φέρνει τα δεδομένα από το Xing...")
            jina_endpoint = f"https://r.jina.ai/{XING_TARGET_URL}"
            headers = {"Authorization": f"Bearer {JINA_API_KEY}", "X-Return-Format": "markdown"}
            response = requests.get(jina_endpoint, headers=headers)
            
            if response.status_code == 200:
                raw_markdown = response.text
                with st.spinner("Το GPT-4o-mini ελέγχει για σίγουρα Matches..."):
                    openai_client = OpenAI(api_key=OPENAI_API_KEY)
                    
                    prompt = """
                    Ανάλυσε το Markdown του Xing για Python Freelance/One-off projects.
                    
                    ΚΑΝΟΝΑΣ MATCHING:
                    1. Αν βρεις το ακριβές όνομα της εταιρείας ή το όνομα του recruiter, βάλε "has_match": 1 και γράψε ένα έτοιμο Cold Email στα Αγγλικά στο πεδίο "ready_email_en".
                    2. Αν το όνομα της εταιρείας είναι κρυφό, ανώνυμο ή γράφει απλώς "Recruiting Agency" χωρίς όνομα, βάλε "has_match": 0 και στο πεδίο "ready_email_en" γράψε ΜΟΝΟ τη λέξη "NO_MATCH".
                    
                    Επέστρεψε ΑΥΣΤΗΡΑ JSON:
                    {
                        "leads": [
                            {
                                "title_gr": "Τίτλος",
                                "client_company_keyword": "Όνομα Εταιρείας ή Ν/Α",
                                "project_link": "Link",
                                "summary_gr": "Σύνοψη στα Ελληνικά",
                                "has_match": 1,
                                "ready_email_en": "Email ή NO_MATCH"
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
                    
                    if len(leads_list) > 0:
                        for lead in leads_list:
                            save_lead(
                                lead['client_company_keyword'],
                                lead['title_gr'],
                                lead['summary_gr'],
                                lead['project_link'],
                                lead['ready_email_en'],
                                lead['has_match']
                            )
                        st.success(f"🔥 Φιλτράρισμα ολοκληρώθηκε! Ανανέωση ιστορικού...")
                        st.rerun()
                    else:
                        st.warning("⚠️ Δεν βρέθηκαν νέα projects.")
            else:
                st.error(f"❌ Σφάλμα Jina API: {response.status_code}")
                
        except KeyError:
            st.error("🚨 Λείπουν τα κλειδιά από τα Secrets!")

# --- ΕΜΦΑΝΙΣΗ ΙΣΤΟΡΙΚΟΥ ΜΕ ΦΙΛΤΡΟ MATCH ---
with col_history:
    st.subheader("🗄️ Ιστορικό Leads & Έτοιμα Drafts")
    history_df = get_last_50_leads()
    
    if history_df.empty:
        st.info("Η βάση είναι άδεια.")
    else:
        csv = history_df.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Download CSV", data=csv, file_name="leads.csv", mime="text/csv")
        st.markdown("---")
        
        for idx, row in history_df.iterrows():
            # Δημιουργούμε σήμανση στον τίτλο για το αν υπάρχει Match
            match_status = "✅ MATCHED" if int(row['has_match']) == 1 else "⚠️ NO CONTACT"
            
            with st.expander(f"[{match_status}] {row['company']} - {row['title']}"):
                st.write(f"**Σύνοψη (GR):** {row['summary']}")
                st.markdown(f"[🔗 Link Αγγελίας]({row['link']})")
                
                # ΚΡΙΣΙΜΟΣ ΕΛΕΓΧΟΣ: Εμφάνιση email ΜΟΝΟ αν υπάρχει Match
                if int(row['has_match']) == 1 and row['email_content'] != "NO_MATCH":
                    st.markdown("### ✉️ Έτοιμο Cold Email:")
                    st.text_area("Copy Email:", value=row['email_content'], height=180, key=f"hist_{idx}")
                else:
                    st.warning("🔒 Το email δεν δημιουργήθηκε επειδή δεν εντοπίστηκε καθαρή εταιρεία/επαφή για Match.")