import streamlit as st
import feedparser
from openai import OpenAI
import os
import requests
import json

# --- Ρύθμιση ---
def get_secret(key):
    return st.secrets.get(key) or os.getenv(key)

client = OpenAI(api_key=get_secret("OPENAI_API_KEY"))

# --- Συναρτήσεις ---
def load_leads():
    if os.path.exists('leads_db.json'):
        with open('leads_db.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def get_contact_email(website):
    try:
        response = requests.post("https://api.dropcontact.io/v1/email", 
            headers={"X-API-KEY": get_secret("DROPCONTACT_API_KEY"), "Content-Type": "application/json"},
            json={"website": website})
        return response.json().get('email', 'N/A')
    except: return 'N/A'

def analyze_and_enrich(leads_list):
    processed = []
    for l in leads_list:
        website = l.get('link', '')
        email = get_contact_email(website)
        
        # Ανάλυση με GPT
        prompt = f"Ανάλυσε: {l['title']}. Δώσε σκορ 1-5 και ελληνική περιγραφή."
        res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
        score = 5 if "5" in res.choices[0].message.content else 4
        
        if score >= 4:
            processed.append({
                "source": l['title'], "score": score, "link": l['link'], "email": email,
                "proposal": f"Πρόταση για: {l['title']}"
            })
    return processed

def get_google_leads(query):
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query, "num": 10})
    headers = {'X-API-KEY': get_secret("SERPER_API_KEY"), 'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get('organic', [])

# --- UI ---
st.set_page_config(page_title="Hunter Pro", layout="wide")
st.title("🏹 Opportunity Hunter: Fallback System")

tab1, tab2 = st.tabs(["Hunt Leads", "Action Pipeline"])

with tab1:
    search_q = st.text_input("Query", 'site:linkedin.com "hiring" "automation"')
    if st.button("Hunt & Enrich"):
        raw = get_google_leads(search_q)
        enriched = analyze_and_enrich(raw)
        
        all_leads = load_leads() + enriched
        with open('leads_db.json', 'w', encoding='utf-8') as f:
            json.dump(all_leads[:50], f, ensure_ascii=False, indent=4)
        st.success("Ενημερώθηκε η βάση!")

with tab2:
    leads = load_leads()
    for l in leads:
        with st.expander(f"🎯 {l['source']}"):
            if l['email'] != 'N/A':
                st.success(f"Email βρέθηκε: {l['email']}")
                st.text_area("Email Pitch:", value=l['proposal'])
            else:
                st.warning("Δεν βρέθηκε email. Χρήση Plan B:")
                st.link_button("Άνοιγμα Link για χειροκίνητο outreach", l['link'])
                st.write("Συμβουλή: Βρες τον υπεύθυνο στο LinkedIn και στείλε Connection Request.")