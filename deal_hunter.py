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

FEEDS = {
    "ForHire": "https://www.reddit.com/r/forhire/new/.rss",
    "SlaveLabour": "https://www.reddit.com/r/slavelabour/new/.rss",
    "Automation": "https://www.reddit.com/r/automation/new/.rss"
}

# --- Συναρτήσεις ---
def analyze_leads_with_gpt(leads_list):
    """Στέλνει τα αποτελέσματα στο GPT για ταξινόμηση και αξιολόγηση."""
    formatted_data = "\n".join([f"- Title: {l['title']}\n  Snippet: {l.get('snippet', '')}\n  Link: {l['link']}" for l in leads_list])
    
    prompt = f"""
    Είσαι ένας έμπειρος Business Analyst. Ανάλυσε τα παρακάτω leads από τη Google.
    Δημιούργησε έναν πίνακα με τις εξής στήλες:
    1. Πηγή (Εταιρεία/Site)
    2. Ελληνική Περιγραφή (Σύνοψη του τι ζητάνε)
    3. Βαθμολογία (1-5, όπου 5 είναι άμεση επαγγελματική ευκαιρία)
    4. Link (Το link που σου έδωσα)

    Αν είναι αγγελία για μόνιμη εργασία (job salary), δώσε χαμηλή βαθμολογία. 
    Αν είναι project ή ανάγκη για consultant, δώσε υψηλή βαθμολογία.
    
    Δεδομένα:
    {formatted_data}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "Δώσε μόνο τον πίνακα σε μορφή Markdown."}, {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def get_google_leads(query):
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query, "num": 10})
    headers = {'X-API-KEY': get_secret("SERPER_API_KEY"), 'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get('organic', [])

def get_reddit_leads(keywords):
    all_leads = []
    for name, url in FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:
            if not keywords or any(k.lower() in entry.title.lower() for k in keywords):
                all_leads.append({"source": name, "title": entry.title, "link": entry.link})
    return all_leads

# --- UI ---
st.set_page_config(page_title="Opportunity Hunter", page_icon="🏹", layout="wide")
st.title("🏹 Opportunity Hunter: Pro Analysis")

tab1, tab2 = st.tabs(["Reddit (RSS)", "Google (Search & Analyze)"])

with tab1:
    keywords_input = st.text_input("Keywords", "scraping, automation, script")
    if st.button("Hunt Reddit"):
        leads = get_reddit_leads([k.strip() for k in keywords_input.split(",")])
        for lead in leads:
            st.markdown(f"**[{lead['source']}]** {lead['title']}")
            st.write(f"[Link]({lead['link']})")
            st.divider()

with tab2:
    search_q = st.text_input("Query", 'site:linkedin.com "hiring" "automation" -jobs')
    if st.button("Hunt & Analyze Google"):
        if not get_secret("SERPER_API_KEY"):
            st.error("Το SERPER_API_KEY λείπει!")
        else:
            with st.spinner("Αναλύω και βαθμολογώ τα leads..."):
                leads = get_google_leads(search_q)
                table = analyze_leads_with_gpt(leads)
                st.markdown(table)