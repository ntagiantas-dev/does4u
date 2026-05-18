import streamlit as st
import openai
import requests
import sqlite3
import json
import re
from datetime import datetime

# Ρύθμιση της σελίδας Streamlit
st.set_page_config(page_title="Does4U - Strict Match & Draft v0.0.9", page_icon="🎯", layout="wide")

st.title("🎯 Does4U - Strict Match & Draft v0.0.9")
st.subheader("Αυτοματοποιημένη Εύρεση Αγγελιών Xing & Στελεχών μέσω AI & Apollo API")

# 1. Έλεγχος και Φόρτωση των Keys από τα Secrets του Streamlit
if "OPENAI_API_KEY" in st.secrets:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
else:
    st.error("❌ Το OpenAI API Key λείπει από τα Secrets!")
    st.stop()

if "APOLLO_API_KEY" in st.secrets:
    APOLLO_KEY = st.secrets["APOLLO_API_KEY"]
else:
    st.error("❌ Το Apollo API Key λείπει από τα Secrets!")
    st.stop()

JINA_KEY = st.secrets.get("JINA_API_KEY", "")

# 2. ΒΑΣΗ ΔΕΔΟΜΕΝΩΝ (SQLite)
def init_db():
    conn = sqlite3.connect("does4u_leads.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT,
            summary TEXT,
            link TEXT,
            email_content TEXT,
            has_match INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

# 3. Βοηθητική Λειτουργία για το Apollo API (Αναζήτηση Ανθρώπων/Emails)
def search_apollo_contacts(company_domain, target_roles):
    """
    Κάνει αναζήτηση στο Apollo API για την εύρεση στελεχών βάσει domain εταιρείας και ρόλων.
    """
    url = "https://api.apollo.io/v1/contacts/search"
    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "X-Api-Key": APOLLO_KEY
    }
    payload = {
        "q_organization_domains": company_domain,
        "person_titles": target_roles,
        "page": 1,
        "per_page": 4
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

# 4. Κύρια Λειτουργία Jina Reader για Xing
def fetch_xing_data(url):
    headers = {}
    if JINA_KEY:
        headers["Authorization"] = f"Bearer {JINA_KEY}"
    
    jina_url = f"https://r.jina.ai/{url}"
    try:
        response = requests.get(jina_url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            st.error(f"❌ Σφάλμα Jina AI ({response.status_code}): {response.text}")
            return None
    except Exception as e:
        st.error(f"❌ Αποτυχία σύνδεσης με Jina AI: {e}")
        return None

# 5. Κύριο UI της Εφαρμογής
xing_url = st.text_input("🔗 Εισάγετε το URL της αγγελίας ή της αναζήτησης από το Xing:", placeholder="https://www.xing.com/jobs/...")

if st.button("🚀 Έναρξη Στόχευσης & Σύνδεσης"):
    if not xing_url:
        st.warning("⚠️ Παρακαλώ εισάγετε ένα έγκυρο Xing URL πρώτα.")
    else:
        with st.spinner("🕷️ Η Jina AI διαβάζει το Xing και το GPT αναλύει τα δεδομένα..."):
            raw_text = fetch_xing_data(xing_url)
            
            if raw_text:
                # Prompt για το GPT ώστε να αναλύσει την αγγελία και να βγάλει δομημένο JSON
                prompt_analysis = f"""
                Analyze the following text extracted from a Xing job posting. 
                Extract the Company Name, a short Summary of the job requirements, and determine if it matches a high-value target profile (has_match = 1 if it fits, 0 otherwise).
                Also, guess or extract the official company website/domain (e.g., 'google.com', 'siemens.de') which will be used for API lookups.
                
                Output strictly in valid JSON format with these exact keys:
                {{
                    "company_name": "Name of Company",
                    "company_domain": "companywebsite.com",
                    "summary": "Brief summary of requirements",
                    "has_match": 1 or 0
                }}

                Xing Data:
                {raw_text[:4000]}
                """
                
                try:
                    client = openai.OpenAI(api_key=openai.api_key)
                    response_gpt = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt_analysis}],
                        temperature=0.2
                    )
                    
                    gpt_out = response_gpt.choices[0].message.content.strip()
                    if "```json" in gpt_out:
                        gpt_out = gpt_out.split("```json")[1].split("```")[0].strip()
                    elif "```" in gpt_out:
                        gpt_out = gpt_out.split("```")[1].split("```")[0].strip()
                        
                    data = json.loads(gpt_out)
                    
                    # Εμφάνιση Αποτελεσμάτων Ανάλυσης
                    st.success("✅ Η ανάλυση ολοκληρώθηκε επιτυχώς!")
                    st.write(f"🏢 **Εταιρεία:** {data.get('company_name')}")
                    st.write(f"🌐 **Domain:** {data.get('company_domain')}")
                    st.write(f"📝 **Σύνοψη:** {data.get('summary')}")
                    
                    match_status = data.get('has_match', 0)
                    
                    # Αν έχουμε Match, τρέχουμε το Apollo API αυτόματα
                    if match_status == 1:
                        st.balloons()
                        st.info("🎯 **Βρέθηκε Match!** Ξεκινάει η αυτόματη αναζήτηση στελεχών στο Apollo...")
                        
                        # Ρόλοι που μας ενδιαφέρουν για HR/Hiring
                        target_roles = ["Recruiter", "HR Manager", "Talent Acquisition", "Human Resources"]
                        company_domain = data.get('company_domain', '')
                        
                        apollo_results = search_apollo_contacts(company_domain, target_roles)
                        
                        contacts_found = []
                        if apollo_results and "contacts" in apollo_results:
                            st.subheader("👥 Στελέχη που βρέθηκαν από το Apollo API:")
                            for contact in apollo_results["contacts"]:
                                name = contact.get("name", "N/A")
                                title = contact.get("title", "N/A")
                                email = contact.get("email", "🔒 Κρυμμένο/Μη διαθέσιμο")
                                
                                st.write(f"👤 **{name}** - {title} ({email})")
                                contacts_found.append(f"{name} ({title}) -> {email}")
                        else:
                            st.warning("⚠️ Δεν βρέθηκαν άμεσα διαθέσιμα στελέχη με email για αυτό το domain στο Apollo.")
                        
                        # Αποθήκευση στη Βάση Δεδομένων
                        conn = sqlite3.connect("does4u_leads.db")
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO leads (company_name, summary, link, email_content, has_match)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            data.get('company_name'), 
                            data.get('summary'), 
                            xing_url, 
                            " | ".join(contacts_found) if contacts_found else "No contacts found", 
                            1
                        ))
                        conn.commit()
                        conn.close()
                        st.success("💾 Το lead και τα emails αποθηκεύτηκαν στη βάση δεδομένων `does4u_leads.db`!")
                        
                    else:
                        st.warning("😴 Η αγγελία δεν πληροί τα κριτήρια strict match. Προσπεράστηκε.")
                        
                except Exception as e:
                    st.error(f"❌ Σφάλμα επεξεργασίας AI ή JSON: {e}")

# 6. Εμφάνιση του Ιστορικού από τη Βάση Δεδομένων στο κάτω μέρος
st.markdown("---")
st.subheader("🗄️ Ιστορικό Leads στη Βάση Δεδομένων")
try:
    conn = sqlite3.connect("does4u_leads.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, company_name, summary, link, email_content, timestamp FROM leads WHERE has_match=1 ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    
    if rows:
        for row in rows:
            with st.expander(f"🏢 {row[1]} ({row[5]})"):
                st.write(f"🔗 **Link:** {row[3]}")
                st.write(f"📝 **Σύνοψη:** {row[2]}")
                st.write(f"📧 **Στελέχη / Emails:** {row[4]}")
    else:
        st.write("Η βάση δεδομένων είναι προσωρινά άδεια ή δεν υπάρχουν matches ακόμα.")
except Exception as e:
    st.write("Δεν βρέθηκαν προηγούμενα δεδομένα.")