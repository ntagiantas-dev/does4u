import os
import requests
import json
import time
import streamlit as st
from openai import OpenAI

# ΑΠΟΛΥΤΑ ΑΣΦΑΛΗΣ ΜΕΘΟΔΟΣ
def get_config(key):
    # 1. Πρώτα Streamlit Secrets (αν υπάρχουν)
    if hasattr(st, "secrets") and key in st.secrets:
        return st.secrets[key]
    # 2. Μετά Environment Variables
    return os.getenv(key)

OPENAI_API_KEY = get_config("OPENAI_API_KEY")
DROPCONTACT_API_KEY = get_config("DROPCONTACT_API_KEY")

# Αν φτάσουμε εδώ και δεν έχουμε κλειδιά, βγάζουμε ένα φιλικό μήνυμα αντί για crash
if not OPENAI_API_KEY or not DROPCONTACT_API_KEY:
    st.error("Δεν βρέθηκαν τα API Keys. Παρακαλώ έλεγξε τα Secrets στο Streamlit Cloud.")
    st.stop() # Σταματάει την εκτέλεση χωρίς error tracebacks

client = OpenAI(api_key=OPENAI_API_KEY)

def scrape_with_jina(url):
    """Μετατρέπει οποιοδήποτε URL σε καθαρό κείμενο για το LLM."""
    jina_url = f"https://r.jina.ai/{url}"
    try:
        response = requests.get(jina_url, timeout=30)
        return response.text
    except Exception as e:
        print(f"Scrape error: {e}")
        return ""

def filter_and_extract_gpt(raw_text):
    """Το 'μυαλό' που κρίνει και εξάγει δεδομένα."""
    prompt = f"""
    Analyze this Upwork job text and client reviews. 
    1. Check if it's about: Web Scraping, AI Automation, Python Scripts, or Growth Hacking.
    2. If NOT relevant, return {{ "status": "ignored" }}.
    3. If relevant, extract:
       - company: Name of company if found.
       - website: Website domain if found.
       - first_name: Client's first name found in reviews (e.g. 'Thanks David!').
       - last_name: Last name if available.
    
    Return ONLY valid JSON (no markdown). 
    Text: {raw_text}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    
    content = response.choices[0].message.content.replace("```json", "").replace("```", "").strip()
    return json.loads(content)

def match_with_dropcontact(data):
    """Αποστολή στους Γάλλους για το email."""
    url = "https://api.dropcontact.io/v1/enrich"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": DROPCONTACT_API_KEY
    }
    payload = {
        "firstName": data.get("first_name"),
        "company": data.get("company"),
        "website": data.get("website")
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def run_deal_hunter(job_links):
    """Η λούπα που ξεσκονίζει τα πάντα."""
    print(f"🚀 Ξεκίνησε το ξεσκόνισμα για {len(job_links)} αγγελίες...")
    
    for link in job_links:
        print(f"\n🔍 Ελέγχω: {link}")
        
        # 1. Scraping
        text = scrape_with_jina(link)
        
        # 2. Decision & Extraction
        try:
            decision = filter_and_extract_gpt(text)
            
            if decision.get("status") != "ignored":
                print(f"🎯 Match! Εταιρεία: {decision.get('company')}. Στέλνω στο Dropcontact...")
                
                # 3. Enrichment
                result = match_with_dropcontact(decision)
                print(f"📧 ΑΠΟΤΕΛΕΣΜΑ: {result}")
            else:
                print("⏭️ Αδιάφορη αγγελία.")
        except Exception as e:
            print(f"⚠️ Σφάλμα στην ανάλυση: {e}")
            
        time.sleep(3) 

# MAIN EXECUTION
if __name__ == "__main__":
    # Εδώ θα βάζεις τα links που θα σκουπίζεις
    urls_to_scan = [
        "https://www.upwork.com/jobs/Example-Job-Link-1"
    ]
    run_deal_hunter(urls_to_scan)