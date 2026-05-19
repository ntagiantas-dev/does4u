import streamlit as st
import feedparser

# Λίστα με RSS feeds από Reddit (π.χ. r/forhire, r/slavelabour, r/automation)
FEEDS = {
    "ForHire": "https://www.reddit.com/r/forhire/new/.rss",
    "SlaveLabour": "https://www.reddit.com/r/slavelabour/new/.rss",
    "Automation": "https://www.reddit.com/r/automation/new/.rss"
}

def get_leads(keywords):
    all_leads = []
    for name, url in FEEDS.items():
        feed = feedparser.parse(url)
        st.write(f"--- Checking {name} ({len(feed.entries)} total posts) ---") # Debugging: Θα δούμε αν παίρνει δεδομένα
        for entry in feed.entries[:10]: # Κοιτάμε τα 10 τελευταία
            # Αν τα keywords είναι κενά, εμφάνισε τα όλα για δοκιμή
            if not keywords or any(k.lower() in entry.title.lower() for k in keywords):
                all_leads.append({"source": name, "title": entry.title, "link": entry.link})
    return all_leads

st.title("🏹 Opportunity Hunter: Reddit Monitor")

# Βάλε εδώ τα keywords που σε ενδιαφέρουν
keywords_input = st.text_input("Keywords (χωρισμένα με κόμμα)", "scraping, automation, script, help")
keywords = [k.strip() for k in keywords_input.split(",")]

if st.button("Find Opportunities"):
    with st.spinner("Hunting..."):
        leads = get_leads(keywords)
        if leads:
            for lead in leads:
                st.markdown(f"**[{lead['source']}]** {lead['title']}")
                st.write(f"[Link]({lead['link']})")
                st.divider()
        else:
            st.write("No fresh leads found. Try different keywords.")