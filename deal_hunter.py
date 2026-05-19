import streamlit as st
import os
import requests
import json
from scrapegraphai.graphs import SmartScraperGraph
from openai import OpenAI

# --- CONFIG & SETUP ---
def get_key(k): return st.secrets.get(k) or os.getenv(k)
client = OpenAI(api_key=get_key("OPENAI_API_KEY"))

# 1. ScrapeGraph: Επιθετική ρύθμιση για το Freelancer
def scrape_target(url, cookies=None):
    # Τα headers βοηθούν να μη σε αναγνωρίζει ως bot
    graph_config = {
        "llm": {"api_key": get_key("OPENAI_API_KEY"), "model_name": "gpt-4o"},
        "headless": True,
        "verbose": True,
        "browser": "chromium",
        "cookies": cookies if cookies else None,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    prompt = """
    Analyze the project page. Extract:
    - job_title: The main project title.
    - project_description: Detailed requirements.
    - budget_range: The provided budget.
    - client_name: If visible in reviews or bio.
    - company_website: If mentioned in the description.
    """
    
    try:
        scraper = SmartScraperGraph(prompt=prompt, source=url, config=graph_config)
        return scraper.run()
    except Exception as e:
        return {"error": str(e)}

# 2. GPT-4o: Ανάλυση & Intent
def analyze_relevance(data):
    prompt = f"""
    Analyze job data: {json.dumps(data)}
    Is this a one-time AI/Scraping/Automation project?
    Return ONLY JSON: {{"relevant": boolean, "reason": "string", "keywords": [".."], "client_entity": "string"}}
    """
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(resp.choices[0].message.content)

# 3. Enrichment Flow
def enrich_data(entity):
    # Εδώ θα γίνει το call στο Dropcontact ή LinkedIn API
    return {"email": "found_email@example.com", "status": "verified"}

# --- UI ---
st.set_page_config(page_title="The Hunter Pro", layout="wide")
st.title("🏹 The Hunter: Freelancer Scraper")

url = st.text_input("Freelancer/Upwork Project URL")
# Προαιρετικά cookies αν το site μας ζορίζει
cookies_input = st.text_area("Cookies (Optional, JSON format):")

if st.button("Start Hunting"):
    cookies = json.loads(cookies_input) if cookies_input else None
    
    with st.status("Hunting...", expanded=True) as status:
        st.write("Scraping...")
        job_data = scrape_target(url, cookies)
        
        if "error" in str(job_data):
            st.error(f"Failed: {job_data}")
        else:
            st.write("Analyzing...")
            analysis = analyze_relevance(job_data)
            
            if analysis["relevant"]:
                st.success(f"🎯 Match! Reason: {analysis['reason']}")
                st.write(f"Keywords: {analysis['keywords']}")
                
                st.write("Enriching...")
                contact = enrich_data(analysis['client_entity'])
                st.json(contact)
                st.balloons()
            else:
                st.warning(f"⏭️ Ignored: {analysis['reason']}")
        
        status.update(label="Hunting finished!", state="complete")