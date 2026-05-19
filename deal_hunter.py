import streamlit as st
import os
from scrapegraphai.graphs import SmartScraperGraph
from openai import OpenAI
import requests
import json

# --- CONFIG ---
def get_key(k): return st.secrets.get(k) or os.getenv(k)

client = OpenAI(api_key=get_key("OPENAI_API_KEY"))

# 1. ScrapeGraph: Διαβάζει το Upwork
def scrape_upwork(url):
    graph_config = {
        "llm": {"api_key": get_key("OPENAI_API_KEY"), "model": "gpt-4o-mini"},
    }
    scraper = SmartScraperGraph(
        prompt="Extract job title, description, budget type, and client history link.",
        source=url,
        config=graph_config
    )
    return scraper.run()

# 2. GPT-4o-mini: Φιλτράρει για Web Scraping, AI, Growth, Python & One-time
def filter_job(job_data):
    prompt = f"Analyze: {job_data}. Return JSON with 'relevant': true/false and 'reason'. Check if one-time project."
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(resp.choices[0].message.content)

# 3. Jina: Συμπληρώνει τα κενά (π.χ. website από το link του client)
def enrich_with_jina(client_link):
    jina_url = f"https://r.jina.ai/{client_link}"
    return requests.get(jina_url).text

# 4. Dropcontact: Match email
def get_email(name, company, website):
    url = "https://api.dropcontact.io/v1/enrich"
    headers = {"X-API-Key": get_key("DROPCONTACT_API_KEY"), "Content-Type": "application/json"}
    payload = {"firstName": name, "company": company, "website": website}
    return requests.post(url, headers=headers, json=payload).json()

# --- UI EXECUTION ---
st.title("🏹 The Hunter: Upwork to Email")
url = st.text_input("Upwork Job URL")

if st.button("Start Hunting"):
    with st.spinner("Scraping..."):
        job = scrape_upwork(url)
        st.write("Found job:", job)
        
        decision = filter_job(job)
        if decision.get("relevant"):
            st.success("Relevant Job!")
            # Εδώ μπαίνει το loop για Jina -> Dropcontact
        else:
            st.error("Not relevant: " + decision.get("reason"))