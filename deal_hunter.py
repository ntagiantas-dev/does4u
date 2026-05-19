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
    file_path = 'leads_db.json'
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def get_contact_email(website):
    try:
        key = get_secret("DROPCONTACT_API_KEY")
        if not key or not website: return "N/A"
        response = requests.post("https://api.dropcontact.io/v1/email", 
            headers={"X-API-KEY": key, "Content-Type": "application/json"},
            json={"website": website}, timeout=10)
        return response.json().get('email', 'N/A')
    except: return 'N/A'

def analyze_and_enrich(leads_list):
    processed = []
    for l in leads_list:
        website = l.get('link', '')
        if not website: continue
        
        # Εμπλουτισμός με Email
        email = get_contact_email(website)
        
        # Αναβαθμισμένο Prompt για το GPT
        prompt = f"""
        Είσαι ένας κορυφαίος Lead Qualifier. Ανάλυσε το παρακάτω link/title για ευκαιρίες εργασίας.
        Title: {l.get('title', '')}
        Snippet: {l.get('snippet', '')}
        
        Κριτήρια:
        - Βαθμολόγησε με 5 αν είναι Project, Consulting, ή Freelance ευκαιρία.
        - Βαθμολόγησε με 1-2 αν είναι μόνιμη θέση εργασίας (Full-time job).
        - Απάντησε ΑΠΟΚΛΕΙΣΤΙΚΑ με ένα JSON object: {{"score": int, "description": "str"}}
        """
        
        try:
            res = client.chat.completions.create(
                model="gpt-4o-mini", 
                messages=[{"role": "system", "content": "You are a helpful assistant that outputs only JSON."},
                          {"role": "user", "content": prompt}]
            )
            data = json.loads(res.choices[0].message.content)
            score = data.get("score", 0)
            desc = data.get("description", "Δεν βρέθηκε περιγραφή.")
            
            if score >= 4:
                processed.append({
                    "source": l.get('title', 'Unknown'), 
                    "score": score, 
                    "link": website, 
                    "email": email, 
                    "proposal": f"Γεια σας, είδα το project σας: {desc}. Ειδικεύομαι σε τέτοια θέματα και θα ήθελα να συζητήσουμε."
                })
        except:
            continue
            
    return processed

def get_google_leads(query):
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query, "num": 10})
    headers = {'X-API-KEY': get_secret("SERPER_API_KEY"), 'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get('organic', [])

# --- UI ---
st.set_page_config(page_title="Hunter Pro", layout="wide")
st.title("🏹 Opportunity Hunter: Pro Engine")

tab1, tab2 = st.tabs(["Hunt Leads", "Action Pipeline"])

with tab1:
    search_q = st.text_input("Query", 'site:linkedin.com "hiring" "automation" "freelance"')
    if st.button("Hunt & Enrich"):
        with st.spinner("Κυνηγάω leads..."):
            raw = get_google_leads(search_q)
            if not raw:
                st.warning("Δεν βρέθηκαν αποτελέσματα από την Google.")
            else:
                enriched = analyze_and_enrich(raw)
                if not enriched:
                    st.info("Δεν βρέθηκαν leads με υψηλό σκορ (4-5). Δοκίμασε άλλο query.")
                else:
                    current = load_leads()
                    all_leads = enriched + current
                    with open('leads_db.json', 'w', encoding='utf-8') as f:
                        json.dump(all_leads[:50], f, ensure_ascii=False, indent=4)
                    st.success(f"Βρέθηκαν {len(enriched)} νέα leads και αποθηκεύτηκαν!")

with tab2:
    leads = load_leads()
    if not leads:
        st.info("Δεν υπάρχουν αποθηκευμένα leads.")
    else:
        for l in leads:
            with st.expander(f"🎯 {l['source']} (Score: {l['score']})"):
                st.write(f"Email: {l['email']}")
                st.text_area("Προσχέδιο:", value=l['proposal'], key=l['link'])
                st.link_button("Δες το Link", l['link'])