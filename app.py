import streamlit as st
import openai
import requests
import json
import re

# Ρύθμιση της σελίδας Streamlit
st.set_page_config(page_title="Does4U - Xing Sniper v0.0.20", page_icon="🎯", layout="wide")

st.title("🎯 Does4U - Xing Sniper v0.0.20")
st.subheader("Αυτοματοποιημένη Εύρεση Εταιρειών & Στελεχών μέσω AI & Apollo API")

# 1. Έλεγχος και Φόρτωση των Keys από τα Secrets του Streamlit
if "OPENAI_API_KEY" in st.secrets:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
else:
    st.error("❌ Το OpenAI API Key λείπει από τα Secrets!")
    st.stop()

if "APOLLO_API_KEY" in st.secrets:
    APOLLO_KEY = st.secrets["APOLLO_API_KEY"]
else:
    st.error("❌ Το Apollo API Key λείπει από τα Secrets!")
    st.stop()

JINA_KEY = st.secrets.get("JINA_API_KEY", "")

# 2. Βοηθητική Λειτουργία για το Apollo API (Αναζήτηση Ανθρώπων/Emails)
def search_apollo_contacts(company_name, target_roles):
    """
    Κάνει αναζήτηση στο Apollo API για την εύρεση στελεχών βάσει εταιρείας και ρόλων.
    """
    url = "https://api.apollo.io/v1/contacts/search"
    
    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "X-Api-Key": APOLLO_KEY
    }
    
    payload = {
        "q_organization_domains": company_name, # Ψάχνει με βάση το όνομα/domain της εταιρείας
        "person_titles": target_roles,           # Λίστα με τους τίτλους που θέλουμε (π.χ. ['HR', 'Recruiter'])
        "page": 1,
        "per_page": 5
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            st.warning(f"⚠️ Το Apollo API επέστρεψε σφάλμα {response.status_code}: {response.text}")
            return None
    except Exception as e:
        st.error(f"❌ Σφάλμα κατά την κλήση του Apollo API: {e}")
        return None

# 3. Κύριο UI της Εφαρμογής
target_url = st.text_input("🔗 Εισάγετε το URL της εταιρείας (ή το όνομα της εταιρείας):", placeholder="e.g. google.com ή MyCompany")

if st.button("🚀 Έναρξη Στόχευσης & Σύνδεσης"):
    if not target_url:
        st.warning("⚠️ Παρακαλώ εισάγετε ένα URL ή όνομα εταιρείας πρώτα.")
    else:
        with st.spinner("🧠 Το GPT αναλύει τον στόχο και το Apollo ψάχνει για emails..."):
            
            # Βήμα A: Καθαρισμός του ονόματος της εταιρείας από το URL
            domain_clean = target_url.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
            
            # Βήμα B: Το GPT αποφασίζει ποιους ρόλους πρέπει να ψάξουμε στο Apollo
            prompt_roles = f"Based on the company '{domain_clean}', we want to target people responsible for hiring or business decisions (e.g., HR, Recruiter, Talent Acquisition, CEO, Founder). Output ONLY a valid JSON list of 3-4 keywords/titles in English. Example: [\"Recruiter\", \"HR Manager\", \"Talent Acquisition\"]."
            
            try:
                client = openai.OpenAI(api_key=openai.api_key)
                response_gpt = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt_roles}],
                    temperature=0.3
                )
                
                gpt_out = response_gpt.choices[0].message.content.strip()
                # Καθαρισμός του output σε περίπτωση που το GPT βάλει markdown code blocks
                if "```json" in gpt_out:
                    gpt_out = gpt_out.split("```json")[1].split("```")[0].strip()
                elif "```" in gpt_out:
                    gpt_out = gpt_out.split("```")[1].split("```")[0].strip()
                
                target_roles = json.loads(gpt_out)
                
                st.info(f"🔍 **Το GPT πρότεινε τους εξής ρόλους στόχευσης:** {', '.join(target_roles)}")
                
            except Exception as e:
                st.warning("⚠️ Αποτυχία αυτόματης εξαγωγής ρόλων από το GPT. Θα χρησιμοποιηθούν default")