import streamlit as st
import openai
import requests
import sqlite3
import json
import pandas as pd
from datetime import datetime

# ⚙️ Ρύθμιση Σελίδας Streamlit
st.set_page_config(page_title="Does4U - Strict Match & Draft v0.0.9", page_icon="🎯", layout="wide")
st.title("🎯 Does4U - Strict Match & Draft v0.0.9")

# 🔑 Έλεγχος API Keys από τα Secrets
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

# 🗄️ ΒΑΣΗ ΔΕΔΟΜΕΝΩΝ (SQLite)
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

# 1️⃣ Apollo API: Εύρεση Επίσημου Domain βάσει Ονόματος Εταιρείας (Όχι μαντεψιές)
def get_apollo_company_domain(company_name):
    url = "https://api.apollo.io/v1/organizations/search"
    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "X-Api-Key": APOLLO_KEY
    }
    payload = {
        "q_organization_name": company_name,  # Strict αναζήτηση με το ακριβές όνομα
        "page": 1,
        "per_page": 1
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            organizations = data.get("organizations", [])
            if organizations:
                # Επιστρέφει το πραγματικό domain της συγκεκριμένης εταιρείας
                actual_domain = organizations[0].get("primary_domain") or organizations[0].get("domain")
                return actual_domain
        return None
    except:
        return None

# 2️⃣ Apollo API: Αναζήτηση Στελεχών βάσει του Έγκυρου Domain
def search_apollo_contacts(company_domain):
    url = "https://api.apollo.io/v1/mixed_people/search"
    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "X-Api-Key": APOLLO_KEY
    }
    payload = {
        "q_organization_domains": company_domain,
        "person_titles": [
            "CTO", "Chief Technology Officer", "Engineering Manager", 
            "Tech Lead", "Product Manager", "Recruiter", "HR Manager", 
            "Talent Acquisition", "Human Resources"
        ],
        "page": 1,
        "per_page": 3
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# 🚀 Κύριο Κουμπί Αυτοματοποίησης
if st.button("🔍 Έναρξη Αυτόματου Scraping & Φιλτραρίσματος Xing"):
    with st.spinner("🕷️ Η Jina AI ξεσκονίζει το Xing για αγγελίες..."):
        
        search_query = "SaaS engineering AI Automation web scraping python scripts freelance contract project"
        xing_search_url = f"https://www.xing.com/jobs/search?keywords={requests.utils.quote(search_query)}"
        jina_url = f"https://r.jina.ai/{xing_search_url}"
        
        headers = {"Authorization": f"Bearer {JINA_KEY}"} if JINA_KEY else {}
        
        try:
            response = requests.get(jina_url, headers=headers)
            if response.status_code != 200:
                st.error(f"❌ Σφάλμα Jina AI: {response.status_code}")
                st.stop()
            raw_text = response.text
        except Exception as e:
            st.error(f"❌ Αποτυχία σύνδεσης με Jina: {e}")
            st.stop()
            
    with st.spinner("🧠 Το GPT-4o-mini απομονώνει One-Off Projects..."):
        prompt = f"""
        You are an elite data miner specializing in B2B lead generation. Analyze the following scraped text from a Xing search page.
        Identify individual job postings or project listings that STRICTLY match two conditions:
        1. Core Domains: SaaS engineering, AI Automation, web scraping, or Python scripting.
        2. Job Type: Must be a One-time project, Freelance gig, Contract-based, Temporary assignment, or Outsourcing request (NOT permanent full-time roles). Look for keywords like 'Freelance', 'Contract', 'Project', 'Temporary', 'Freier Mitarbeiter'.

        For ANY strictly matching job/project, extract the Company Name, a brief requirements summary highlighting the project nature, and the link to the job (if visible, else leave blank). Do NOT try to guess the company domain.
        
        Output strictly as a valid JSON list of objects with this exact format:
        [
            {{
                "company_name": "Example GmbH",
                "summary": "[Freelance Project] Need a Python script to automate data sync between SaaS platforms.",
                "link": "https://xing.com/jobs/...",
                "has_match": 1
            }}
        ]
        If no strict freelance/project matches exist, return an empty list [].

        Scraped Content:
        {raw_text[:6000]}
        """
        
        try:
            client = openai.OpenAI(api_key=openai.api_key)
            response_gpt = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            gpt_out = response_gpt.choices[0].message.content
            
            if "```json" in gpt_out:
                gpt_out = gpt_out.split("```json")[1].split("```")[0].strip()
            elif "```" in gpt_out:
                gpt_out = gpt_out.split("```")[1].split("```")[0].strip()
                
            jobs = json.loads(gpt_out)
            
            if not jobs:
                st.info("😴 Δεν βρέθηκαν αγγελίες για One-Off Projects με strict match σε αυτή τη ροή.")
            else:
                st.success(f"🎯 Βρέθηκαν {len(jobs)} projects που ταιριάζουν απόλυτα!")
                
                for job in jobs:
                    company_name_clean = job.get("company_name", "").strip()
                    st.markdown(f"### 🏢 Εταιρεία: {company_name_clean}")
                    st.write(f"📝 **Σύνοψη Έργου:** {job['summary']}")
                    
                    contacts_list = []
                    
                    if company_name_clean:
                        with st.spinner(f"🔍 Αναζήτηση επίσημου Domain στο Apollo για την '{company_name_clean}'..."):
                            actual_domain = get_apollo_company_domain(company_name_clean)
                            
                        if actual_domain:
                            st.write(f"🌐 **Επαληθευμένο Domain:** {actual_domain}")
                            with st.spinner(f"📞 Άντληση Decision Makers από το Apollo..."):
                                apollo_data = search_apollo_contacts(actual_domain)
                                
                                people_data = []
                                if apollo_data:
                                    if "people" in apollo_data:
                                        people_data = apollo_data["people"]
                                    elif "contacts" in apollo_data:
                                        people_data = apollo_data["contacts"]
                                
                                if people_data:
                                    for person in people_data:
                                        name = person.get("name", "N/A")
                                        title = person.get("title", "N/A")
                                        email = person.get("email", "🔒 Μη διαθέσιμο")
                                        contacts_list.append(f"{name} ({title}) -> {email}")
                                        st.write(f"👤 **{name}** - {title} | 📧 {email}")
                                else:
                                    st.write("⚠️ Δεν βρέθηκαν κατάλληλα στελέχη στο Apollo για αυτό το domain.")
                        else:
                            st.write("❌ Η εταιρεία δεν εντοπίστηκε στη βάση του Apollo.")
                    
                    # 💾 Αποθήκευση στην SQLite (Κρατάμε μόνο όσα βρήκαν πραγματικά contacts)
                    final_contacts = " | ".join(contacts_list) if contacts_list else "No contacts"
                    
                    conn = sqlite3.connect("does4u_leads.db")
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO leads (company_name, summary, link, email_content, has_match)
                        VALUES (?, ?, ?, ?, 1)
                    """, (company_name_clean, job['summary'], job['link'], final_contacts))
                    conn.commit()
                    conn.close()
                    st.caption("💾 Αποθηκεύτηκε στο ιστορικό.")
                    st.markdown("---")
                    
        except Exception as e:
            st.error(f"❌ Σφάλμα κατά την επεξεργασία: {e}")

# 🗄️ Προβολή Ιστορικού Βάσης Δεδομένων (Μόνο Επιτυχείς Επαφές)
st.subheader("🗄️ Αποθηκευμένα Match Leads με Contacts (SQLite)")
try:
    conn = sqlite3.connect("does4u_leads.db")
    # ✅ Φίλτρο ώστε να επιστρέφει ΜΟΝΟ τα πραγματικά matches που έχουν βρει email/contacts
    query = """
        SELECT company_name, summary, email_content, timestamp 
        FROM leads 
        WHERE has_match = 1 AND email_content != 'No contacts' 
        ORDER BY id DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.write("Δεν υπάρχουν ακόμα αποθηκευμένα matches με διαθέσιμα στοιχεία επικοινωνίας.")
except:
    st.write("Δεν βρέθηκε η βάση δεδομένων ή είναι άδεια.")