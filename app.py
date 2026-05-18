import streamlit as st
from firecrawl import FirecrawlApp
from openai import OpenAI
import json
import pandas as pd

# Ρύθμιση Σελίδας
st.set_page_config(page_title="Does4U - Lead Prospector", page_icon="⚡", layout="wide")
st.title("⚡ Does4U Job Prospector & Keyword Extractor v12.0")
st.subheader("Στάδιο 1: Αυστηρό Φιλτράρισμα Αγγελιών & Εξαγωγή Keywords για Email Finder")

# Διάβασμα των κλειδιών από τα Secrets του Streamlit Cloud
try:
    FIRECRAWL_API_KEY = st.secrets["FIRECRAWL_API_KEY"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("🚨 Σφάλμα: Δεν βρέθηκαν τα κλειδιά στα Secrets του Streamlit Cloud!")
    st.stop()

st.info("🎯 **Στόχος:** Το Bot εντοπίζει αγγελίες για Python, Scraping, AI & SaaS. Αν είναι match, εξάγει τα Keywords της εταιρείας για να τα χρησιμοποιήσουμε στο εργαλείο εύρεσης email.")

if st.button("🚀 ΕΝΑΡΞΗ ΑΝΑΖΗΤΗΣΗΣ & ΕΞΑΓΩΓΗΣ KEYWORDS"):
    with st.spinner("Σκανάρω το web και το GPT απομονώνει αγγελίες και εταιρικά Keywords..."):
        try:
            firecrawl_app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
            openai_client = OpenAI(api_key=OPENAI_API_KEY)
            
            # Καθαρό search query για να φέρουμε αγγελίες προγραμματισμού
            search_query = '("web scraping" OR "Python automation" OR "AI automation" OR "SaaS developer") ("hiring" OR "looking for freelancer" OR "job opening") -inurl:blog -inurl:tutorial'
            
            search_result = firecrawl_app.search(search_query, limit=12)
            
            raw_results = []
            if hasattr(search_result, 'data') and search_result.data:
                raw_results = search_result.data
            elif isinstance(search_result, list):
                raw_results = search_result
            elif isinstance(search_result, dict) and "data" in search_result:
                raw_results = search_result["data"]
            else:
                raw_results = getattr(search_result, 'results', [])

            if not raw_results:
                st.warning("Δεν βρέθηκαν αποτελέσματα. Δοκίμασε ξανά σε λίγο.")
            else:
                leads_list = []
                
                for item in raw_results:
                    url = getattr(item, 'url', '')
                    content = getattr(item, 'markdown', '')[:4000] if getattr(item, 'markdown', '') else ''
                    
                    if not content or len(content).strip() < 200:
                        continue
                        
                    # Το GPT εδώ λειτουργεί ως Data Extractor
                    prompt = f"""
                    Είσαι ο Lead Qualifier της Does4U. Εξετάζεις το κείμενο μιας σελίδας για να δεις αν είναι αγγελία που μας ενδιαφέρει.
                    
                    Κριτήριο Match: Πρέπει να είναι πραγματική αγγελία ή ζήτηση για Python, Scraping, SaaS ή Automations.
                    
                    Αποστολή σου:
                    1. Έλεγξε αν είναι match (is_match: true/false).
                    2. Αν είναι match, μετάφρασε τον Τίτλο στα ΕΛΛΗΝΙΚΑ.
                    3. Εντόπισε και εξέδωσε τα KEYWORDS της εταιρείας που χρειάζονται για να βρούμε το email της με άλλα εργαλεία (Όνομα Εταιρείας, Domain/Site αν αναφέρεται, Όνομα Recruiter/Hiring Manager αν υπάρχει).
                    
                    Επέστρεψε ΑΥΣΤΗΡΑ ΜΟΝΟ ένα JSON:
                    {{
                        "is_match": true ή false,
                        "title_gr": "Ο τίτλος στα Ελληνικά",
                        "company_name": "Το όνομα της εταιρείας που προσλαμβάνει",
                        "company_domain": "Το website της εταιρείας (αν υπάρχει, αλλιώς κενό)",
                        "recruiter_name": "Όνομα υπευθύνου (αν αναφέρεται, αλλιώς κενό)",
                        "requirements_summary": "1 πρόταση στα Ελληνικά για το τι ζητάνε"
                    }}
                    """
                    
                    response = openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        response_format={"type": "json_object"},
                        messages=[
                            {"role": "system", "content": "Return only valid JSON."},
                            {"role": "user", "content": f"{prompt}\n\nΚείμενο:\n{content}"}
                        ],
                        temperature=0.1
                    )
                    
                    ai_data = json.loads(response.choices[0].message.content)
                    
                    # Κρατάμε ΜΟΝΟ τις πραγματικές αγγελίες
                    if ai_data.get("is_match") is not True or not ai_data.get("company_name"):
                        continue
                        
                    leads_list.append({
                        "Θέση (Ελληνικά)": ai_data.get("title_gr"),
                        "Εταιρεία (Keyword 1)": ai_data.get("company_name"),
                        "Website (Keyword 2)": ai_data.get("company_domain") if ai_data.get("company_domain") else "Δεν αναφέρεται",
                        "Υπεύθυνος (Keyword 3)": ai_data.get("recruiter_name") if ai_data.get("recruiter_name") else "Δεν αναφέρεται",
                        "Τι Ζητάνε": ai_data.get("requirements_summary"),
                        "Σύνδεσμος Αγγελίας": url
                    })
                
                # Εμφάνιση αποτελεσμάτων
                if len(leads_list) == 0:
                    st.warning("⚠️ Δεν βρέθηκαν καθαρές αγγελίες που να ταιριάζουν στα κριτήρια της Does4U αυτή τη στιγμή.")
                else:
                    df = pd.DataFrame(leads_list)
                    st.success(f"🎯 Βρέθηκαν {len(df)} επιβεβαιωμένες αγγελίες! Τα Keywords εξήχθησαν και είναι έτοιμα:")
                    
                    # Εμφάνιση του πίνακα με τα Keywords
                    st.dataframe(df, use_container_width=True)
                    
                    st.info("💡 **Επόμενο Βήμα (Στάδιο 2):** Παίρνουμε τις τιμές από τις στήλες 'Εταιρεία' και 'Website' και τις περνάμε στο API εύρεσης email για να κάνουμε το Match.")
                            
        except Exception as e:
            st.error(f"Σφάλμα: {e}")
            