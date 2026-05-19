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

# RSS Feeds
FEEDS = {
    "ForHire": "https://www.reddit.com/r/forhire/new/.rss",
    "SlaveLabour": "https://www.reddit.com/r/slavelabour/new/.rss",
    "Automation": "https://www.reddit.com/r/automation/new/.rss"
}

# --- Συναρτήσεις ---
def translate_to_greek(text):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Είσαι μεταφραστής αγγελιών. Μετάφρασε τον τίτλο στα Ελληνικά διατηρώντας το νόημα. Δώσε μόνο το αποτέλεσμα."},
                {"role": "user", "content": text}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except:
        return text

def get_google_leads(query):
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query, "num": 10})
    headers = {
        'X-API-KEY': get_secret("SERPER_API_KEY"),
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get('organic', [])

def get_reddit_leads(keywords):
    all_leads = []
    for name, url in FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:
            if not keywords or any(k.lower() in entry.title.lower() for k in keywords):
                all_leads.append({
                    "source": name, 
                    "title": entry.title, 
                    "greek_title": translate_to_greek(entry.title),
                    "link": entry.link
                })
    return all_leads

# --- UI ---
st.set_page_config(page_title="Opportunity Hunter", page_icon="🏹")
st.title("🏹 Opportunity Hunter: Pro Edition")

tab1, tab2 = st.tabs(["Reddit (RSS)", "Google (Search)"])

with tab1:
    keywords_input = st.text_input("Keywords για Reddit", "scraping, automation, script")
    keywords = [k.strip() for k in keywords_input.split(",")] if keywords_input else []
    if st.button("Hunt Reddit"):
        leads = get_reddit_leads(keywords)
        for lead in leads:
            st.markdown(f"### 🇬🇷 {lead['greek_title']}")
            st.caption(f"Πηγή: {lead['source']}")
            st.write(f"[Link]({lead['link']})")
            st.divider()

with tab2:
    search_q = st.text_input("Τι ψάχνουμε στη Google (π.χ. site:linkedin.com 'automation hire')", 'site:linkedin.com "hiring" "automation"')
    if st.button("Hunt Google"):
        if not get_secret("SERPER_API_KEY"):
            st.error("Το SERPER_API_KEY λείπει από τα Secrets!")
        else:
            leads = get_google_leads(search_q)
            for lead in leads:
                st.subheader(lead['title'])
                st.write(lead.get('snippet', ''))
                st.link_button("Δες το Post", lead['link'])
                st.divider()