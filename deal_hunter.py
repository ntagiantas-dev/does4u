import streamlit as st
import os
import requests
import json
from openai import OpenAI

# --- CONFIG & SETUP ---
def get_key(k): return st.secrets.get(k) or os.getenv(k)
client = OpenAI(api_key=get_key("OPENAI_API_KEY"))

def scrape_target(url):
    jina_url = f"https://r.jina.ai/{url}"
    headers = {"Authorization": f"Bearer {get_key('JINA_API_KEY')}"} if get_key("JINA_API_KEY") else {}
    try:
        response = requests.get(jina_url, headers=headers, timeout=30)
        return response.text if response.status_code == 200 else f"Error: Status {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

def analyze_relevance(text_data):
    # Κόβουμε το κείμενο στους πρώτους 15.000 χαρακτήρες (αρκούν για να βρει το project)
    trimmed_text = text_data[:15000] 
    
    prompt = f"Analyze this job: {trimmed_text}. Return JSON: {{\"relevant\": true/false, \"reason\": \"string\", \"keywords\": [], \"client_entity\": \"string\"}}"
    
    resp = client.chat.completions.create(
        model="gpt-4o-mini", # Χρησιμοποίησε το mini για να γλιτώσεις credits και errors
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(resp.choices[0].message.content)

# --- UI ---
st.title("🏹 The Hunter: Jina On The Rocks")
url = st.text_input("Project URL")

if st.button("Start Hunting"):
    with st.status("Hunting...", expanded=True) as status:
        job_text = scrape_target(url) 
        if "Error" in job_text:
            st.error(job_text)
        else:
            analysis = analyze_relevance(job_text)
            if analysis.get("relevant"):
                st.success(f"🎯 Match! {analysis.get('reason')}")
                st.json(analysis)
            else:
                st.warning(f"⏭️ Ignored: {analysis.get('reason')}")
        status.update(label="Finished!", state="complete")