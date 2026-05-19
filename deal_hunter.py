import os
import requests
import json
import time
import smtplib
from email.message import EmailMessage
import streamlit as st
from openai import OpenAI

# 1. Ασφαλής ανάκτηση όλων των κλειδιών
def get_config(key):
    if hasattr(st, "secrets") and key in st.secrets:
        return st.secrets[key]
    return os.getenv(key)

# Φόρτωση όλων των απαραίτητων κλειδιών
OPENAI_API_KEY = get_config("OPENAI_API_KEY")
DROPCONTACT_API_KEY = get_config("DROPCONTACT_API_KEY")
JINA_API_KEY = get_config("JINA_API_KEY")
EMAIL_USER = get_config("EMAIL_USER")
EMAIL_PASSWORD = get_config("EMAIL_PASSWORD")

client = OpenAI(api_key=OPENAI_API_KEY)

# 2. Scraper (Jina)
def scrape_with_jina(url):
    headers = {"Authorization": f"Bearer {JINA_API_KEY}"} if JINA_API_KEY else {}
    jina_url = f"https://r.jina.ai/{url}"
    try:
        response = requests.get(jina_url, headers=headers, timeout=30)
        return response.text
    except Exception as e:
        return ""

# 3. GPT Brain (Analysis)
def filter_and_extract_gpt(raw_text):
    prompt = f"""Analyze the Upwork job text. 
    1. Check for: Web Scraping, AI Automation, Python, Growth Hacking.
    2. If not relevant, return {{"status": "ignored"}}.
    3. If relevant, extract: company, website, first_name.
    Return ONLY JSON. Text: {raw_text}"""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    content = response.choices[0].message.content.replace("```json", "").replace("```", "").strip()
    return json.loads(content)

# 4. Enrichment (Dropcontact)
def match_with_dropcontact(data):
    url = "https://api.dropcontact.io/v1/enrich"
    headers = {"Content-Type": "application/json", "X-API-Key": DROPCONTACT_API_KEY}
    payload = {"firstName": data.get("first_name"), "company": data.get("company"), "website": data.get("website")}
    return requests.post(url, headers=headers, json=json.dumps(payload)).json()

# 5. SMTP Outreach
def send_email(to_email, name):
    msg = EmailMessage()
    msg.set_content(f"Hi {name}, saw your job post and I can help with automation!")
    msg["Subject"] = "Quick question about your Upwork post"
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASSWORD)
        smtp.send_message(msg)

# 6. Κεντρική Ροή (The Hunter)
def run_deal_hunter(job_links):
    for link in job_links:
        text = scrape_with_jina(link)
        decision = filter_and_extract_gpt(text)
        
        if decision.get("status") != "ignored":
            enrichment = match_with_dropcontact(decision)
            email = enrichment.get("email")
            if email:
                send_email(email, decision.get("first_name"))
        time.sleep(3)

if __name__ == "__main__":
    # Εδώ θα μπαίνουν τα links
    urls = ["URL1", "URL2"] 
    run_deal_hunter(urls)