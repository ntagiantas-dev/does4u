import streamlit as st
import os
import requests
import json
from scrapegraphai.graphs import SmartScraperGraph
from openai import OpenAI

# --- CONFIG ---
def get_key(k): return st.secrets.get(k) or os.getenv(k)
client = OpenAI(api_key=get_key("OPENAI_API_KEY"))

# 1. ScrapeGraph: Επιθετική ρύθμιση για ανθεκτικότητα
def scrape_upwork(url):
    # Εδώ ενεργοποιούμε τον browser με stealth για να αποφύγουμε τα blocks
    graph_config = {
        "llm": {"api_key": get_key("OPENAI_API_KEY"), "model": "gpt-4o"},
        "headless": False, 
        "verbose": True,
        "use_stealth": True,  # Εξαιρετικά σημαντικό για το Upwork
        "browser": "chromium"
    }
    
    prompt = """
    Extract from this Upwork job:
    1. Job Title.
    2. Detailed Description.
    3. Client History/Feedback Link (crucial).
    4. Verify if it is a 'one-time project' (True/False).
    5. Client/Company Name if visible.
    Do not return NA. If page is blocked or empty, return {"error": "BLOCKED"}.
    """
    
    try:
        scraper = SmartScraperGraph(prompt=prompt, source=url, config=graph_config)
        return scraper.run()
    except Exception as e:
        return {"error": str(e)}

# 2. GPT-4o: Ποιοτική Ανάλυση & Keyword Extraction
def filter_and_analyze(job_data):
    if not job_data or "error" in job_data:
        return {"relevant": False, "reason": "Scraping failed or was blocked."}

    prompt = f"""
    Analyze job: {json.dumps(job_data)}
    
    CRITERIA (STRICT):
    - Must be a ONE-TIME project.
    - Must involve: Web Scraping, AI Automation, Lead Gen, Growth Hacking, or SaaS Engineering.
    
    TASKS:
    - Extract ONLY the 'golden' keywords from the job and history.
    - Identify Client/Company name.
    
    Return VALID JSON: {{"relevant": true/false, "reason": "...", "keywords": ["k1", "k2"], "client_name": "...", "company_name": "..."}}
    """
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(resp.choices[0].message.content)

# 3. Jina + GPT: Καθαρισμός Website URL
def get_clean_website(client_name, company_name):
    # Αναζήτηση μέσω Jina
    jina_url = f"https://r.jina.ai/search?q=official+website+for+{client_name}+{company_name}"
    raw_text = requests.get(jina_url).text
    
    # LLM για καθαρισμό του URL
    prompt = f"From this text, extract ONLY the official company website URL. If none, return 'None': {raw_text[:1000]}"
    url_resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
    return url_resp.choices[0].message.content.strip()

# --- UI EXECUTION ---
st.title("🏹 The Hunter: Pro Scraper")
url = st.text_input("Upwork Job URL")

if st.button("Start Hunting"):
    with st.spinner("🕵️‍♂️ Browser running..."):
        job = scrape_upwork(url)
        
        if "error" in str(job):
            st.error("Το Upwork μπλόκαρε το request (Cloudflare). Δοκίμασε να προσθέσεις cookies στο config.")
        else:
            analysis = filter_and_analyze(job)
            
            if analysis.get("relevant"):
                st.success("🎯 Found a perfect match!")
                st.write("Keywords:", analysis.get("keywords"))
                
                # Enrichment
                with st.spinner("Enriching contact info..."):
                    website = get_clean_website(analysis.get("client_name"), analysis.get("company_name"))
                    st.write("Website identified:", website)
                    
                    if website != "None":
                        # Call Dropcontact
                        st.info("Calling Dropcontact API...")
                        # email_data = get_email(...) 
                        st.balloons()
            else:
                st.warning(f"❌ Not relevant: {analysis.get('reason')}")