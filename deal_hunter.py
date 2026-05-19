import streamlit as st
import feedparser
from openai import OpenAI
import os

# --- Ρύθμιση API Keys (Υποστηρίζει Streamlit Secrets) ---
def get_secret(key):
    return st.secrets.get(key) or os.getenv(key)

client = OpenAI(api_key=get_secret("OPENAI_API_KEY"))

# Λίστα με RSS feeds
FEEDS = {
    "ForHire": "https://www.reddit.com/r/forhire/new/.rss",
    "SlaveLabour": "https://www.reddit.com/r/slavelabour/new/.rss",
    "Automation": "https://www.reddit.com/r/automation/new/.rss"
}

# Συνάρτηση μετάφρασης
def translate_to_greek(text):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Μετάφρασε τον τίτλο της αγγελίας στα Ελληνικά. Δώσε μόνο το αποτέλεσμα."},
                {"role": "user", "content": text}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return text # Επιστρέφει το αγγλικό αν αποτύχει η μετάφραση

def get_leads(keywords):
    all_leads = []
    for name, url in FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:
            if not keywords or any(k.lower() in entry.title.lower() for k in keywords):
                # Μετάφραση
                greek_title = translate_to_greek(entry.title)
                all_leads.append({
                    "source": name, 
                    "title": entry.title, 
                    "greek_title": greek_title,
                    "link": entry.link
                })
    return all_leads

# --- UI ---
st.set_page_config(page_title="Opportunity Hunter", page_icon="🏹")
st.title("🏹 Opportunity Hunter: Reddit Monitor")

keywords_input = st.text_input("Keywords (χωρισμένα με κόμμα)", "scraping, automation, script, help")
keywords = [k.strip() for k in keywords_input.split(",")] if keywords_input else []

if st.button("Find Opportunities"):
    if not get_secret("OPENAI_API_KEY"):
        st.error("Το OpenAI API Key λείπει από τα Secrets!")
    else:
        with st.spinner("Κυνηγάω και μεταφράζω..."):
            leads = get_leads(keywords)
            if leads:
                for lead in leads:
                    st.markdown(f"### 🇬🇷 {lead['greek_title']}")
                    st.caption(f"Πηγή: {lead['source']} | *Αγγλικός τίτλος: {lead['title']}*")
                    st.write(f"[Link για το post]({lead['link']})")
                    st.divider()
            else:
                st.write("Δεν βρέθηκαν φρέσκα αποτελέσματα. Δοκίμασε άλλα keywords.")