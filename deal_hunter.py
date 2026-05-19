import streamlit as st
import os
import requests
import json
from scrapegraphai.graphs import SmartScraperGraph
from openai import OpenAI

# --- CONFIG ---
def get_key(k): return st.secrets.get(k) or os.getenv(k)
client = OpenAI(api_key=get_key("OPENAI_API_KEY"))

# 1. ScrapeGraph: Αυστηρή συλλογή δεδομένων
def scrape_upwork(url):
    graph_config = {
        "llm": {"api_key": get_key("OPENAI_API_KEY"), "model": "gpt-4o-mini"},
    }
    # Εξειδικευμένο prompt για one-time projects και client details
    prompt = """Extract:
    1. Job title and exact description.
    2. Is this a 'one-time project'? (True/False)
    3. Category/Skills (must relate to Web Scraping, AI Automation, Lead Gen, Growth Hacking, or SaaS Engineering).
    4. Client history link and client reputation/recent feedback details.
    """
    
    scraper = SmartScraperGraph(prompt=prompt, source=url, config=graph_config)
    return scraper.run()

# 2. GPT-4o-mini: Ανάλυση & Keyword Matching (ΟΧΙ Δημιουργία)
def filter_and_analyze(job_data):
    prompt = f"""
    Analyze the following job data: {job_data}.
    
    TASKS:
    1. Determine if it is a 'one-time project' AND fits strictly into: Web Scraping, AI Automations, Lead Generation, Growth Hacking, or SaaS Engineering.
    2. Extract 'golden' keywords from the job description and client history/feedback.
    3. Return JSON ONLY: {{"relevant": true/false, "reason": "...", "keywords": ["k1", "k2"], "client_name": "...", "company_name": "..."}}
    
    Return ONLY valid JSON.
    """
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(resp.choices[0].message.content)

# 3. Jina: Εμπλουτισμός (αναζήτηση website από τα δεδομένα του client)
def enrich_with_jina(client_name, company_name):
    # Αναζήτηση στο Jina χρησιμοποιώντας τα στοιχεία που βρήκαμε
    search_query = f"{client_name} {company_name} website official"
    jina_url = f"https://r.jina.ai/{search_query}"
    response = requests.get(jina_url)
    return response.text # Εδώ θα μπορούσες να βάλεις ένα call στο GPT για να εξάγει το URL από το κείμενο

# 4. Dropcontact
def get_email(name, company, website):
    url = "https://api.dropcontact.io/v1/enrich"
    headers = {"X-API-Key": get_key("DROPCONTACT_API_KEY"), "Content-Type": "application/json"}
    payload = {"firstName": name, "company": company, "website": website}
    return requests.post(url, headers=headers, json=payload).json()

# --- UI ---
st.title("🏹 The Hunter: Pro Edition")
url = st.text_input("Upwork Job URL")

if st.button("Start Hunting"):
    with st.spinner("Scraping & Analyzing..."):
        # Scrape
        job = scrape_upwork(url)
        
        # Filter & Keywords
        analysis = filter_and_analyze(job)
        
        if analysis.get("relevant"):
            st.success("Target Identified!")
            st.write("Keywords Found:", analysis.get("keywords"))
            
            # Enrich
            st.info("Searching for client contact info...")
            enrichment_data = enrich_with_jina(analysis.get("client_name"), analysis.get("company_name"))
            
            # Εδώ προσθέτεις τη λογική για να περάσεις το website στο dropcontact
            st.write("Enrichment complete. Ready for Outreach.")
        else:
            st.error(f"Filtered out: {analysis.get('reason')}")