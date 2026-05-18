import streamlit as st
from firecrawl import FirecrawlApp
from openai import OpenAI
import json
import pandas as pd

# Ρύθμιση Σελίδας
st.set_page_config(page_title="Does4U - Lead Hunter", page_icon="⚡", layout="wide")
st.title("⚡ Does4U High-Yield Lead Hunter v8.0")
st.subheader("Σύστημα Ευρείας Αναζήτησης & Deep AI Φιλτραρίσματος")

# Διάβασμα των κλειδιών από τα Secrets του Streamlit Cloud
try:
    FIRECRAWL_API_KEY = st.secrets["FIRECRAWL_API_KEY"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("🚨 Σφάλμα: Δεν βρέθηκαν τα κλειδιά στα Secrets του Streamlit Cloud!")
    st.stop()

st.info("🎯 **Στόχος:** Το Bot σκανάρει το web για: *Web Scraping, AI Automations, Python Scripts, SaaS Engineering*.")

if st.button("🚀 ΕΝΑΡΞΗ ΑΥΤΟΜΑΤΟΥ ΚΥΝΗΓΙΟΥ"):
    with st.spinner("Το Firecrawl συλλέγει δεδομένα και το GPT-4o-mini φιλτράρει αυστηρά..."):
        try:
            firecrawl_app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
            openai_client = OpenAI(api_key=OPENAI_API_KEY)
            
            # Απλό και καθαρό query για να μην κολλάει η μηχανή αναζήτησης
            # Ψάχνει άμεση ζήτηση για τις υπηρεσίες σας
            clean_query = '"looking for python developer" OR "hiring web scraping" OR "need AI automation"'
            
            # Ζητάμε 15 αποτελέσματα για να έχουμε μεγάλο δείγμα
            search_result = firecrawl_app.search(clean_query, limit=15)
            
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
                st.warning("Το Firecrawl δεν επέστρεψε δεδομένα. Δοκίμασε να ξαναπατήσεις το κουμπί.")
            else:
                leads_list = []
                
                for item in raw_results:
                    url = getattr(item, 'url', '')
                    content = getattr(item, 'markdown', '')[:3500] if getattr(item, 'markdown', '') else ''
                    
                    if not content or len(content).strip() < 150:
                        continue
                        
                    # Το GPT αναλαμβάνει όλο το φιλτράρισμα και τη μετάφραση
                    prompt = f"""
                    Είσαι ο αυστηρός Lead Qualifier της Does4U (SaaS & AI Automation Studio).
                    Εξέτασε το παρακάτω κείμενο από το internet.
                    
                    Αποστολή σου:
                    1. ΕΛΕΓΧΟΣ MATCH: Είναι αυτό το κείμενο ΠΡΑΓΜΑΤΙΚΗ αγγελία, project ή post όπου κάποιος ψάχνει developer/freelancer για Python, Scraping, AI ή SaaS; Αν είναι άρθρο, οδηγός, tutorial ή άσχετο, βάλε "is_match": false.
                    2. ΜΕΤΑΦΡΑΣΗ: Αν είναι match, μετάφρασε τον Τίτλο και γράψε μια σύντομη σύνοψη στα ΕΛΛΗΝΙΚΑ.
                    3. EMAIL: Ψάξε για email επικοινωνίας. Αν δεν υπάρχει, γράψε "Δεν βρέθηκε".
                    4. COLD EMAIL: Γράψε ένα επαγγελματικό email εκ μέρους της Does4U στα Αγγλικά.
                    
                    Επέστρεψε ΑΥΣΤΗΡΑ ΜΟΝΟ ένα έγκυρο JSON αντικείμενο:
                    {{
                        "is_match": true ή false,
                        "translated_title": "Ο τίτλος στα Ελληνικά",
                        "summary_greek": "Σύνοψη στα Ελληνικά",
                        "email": "το email ή Δεν βρέθηκε",
                        "generated_email": "Το cold email"
                    }}
                    
                    Κείμενο:
                    {content}
                    """
                    
                    response = openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        response_format={"type": "json_object"},
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.1
                    )
                    
                    ai_data = json.loads(response.choices[0].message.content)
                    
                    # Αν το AI πει ότι είναι σκουπίδι/άρθρο, το πετάμε
                    if ai_data.get("is_match") is not True:
                        continue
                        
                    leads_list.append({
                        "Τίτλος (Ελληνικά)": ai_data.get("translated_title"),
                        "Τι Ζητάνε (Σύνοψη)": ai_data.get("summary_greek"),
                        "Email Επικοινωνίας": ai_data.get("email"),
                        "Σύνδεσμος (URL)": url,
                        "Έτοιμο Email Does4U": ai_data.get("generated_email")
                    })
                
                # Εμφάνιση
                if len(leads_list) == 0:
                    st.info("⚠️ Το Firecrawl βρήκε σελίδες, αλλά το AI τις απέρριψε όλες ως 'μη-αγγελίες' (blogs/tutorials). Ο πίνακας έμεινε καθαρός!")
                else:
                    df = pd.DataFrame(leads_list)
                    st.success(f"🎯 Βρέθηκαν {len(df)} πραγματικά leads!")
                    st.dataframe(df[["Τίτλος (Ελληνικά)", "Τι Ζητάνε (Σύνοψη)", "Email Επικοινωνίας", "Σύνδεσμος (URL)"]], use_container_width=True)
                    
                    st.markdown("### 📝 Έτοιμα Emails προς Αντιγραφή:")
                    for idx, row in df.iterrows():
                        with st.expander(f"✉️ Pitch για: {row['Τίτλος (Ελληνικά)']} ({row['Email Επικοινωνίας']})"):
                            st.text_area("Κείμενο Email:", row['Έτοιμο Email Does4U'], height=250, key=f"txt_{idx}")
                            st.caption(f"Πηγή: {row['Σύνδεσμος (URL)']}")
                            
        except Exception as e:
            st.error(f"Παρουσιάστηκε σφάλμα: {e}")