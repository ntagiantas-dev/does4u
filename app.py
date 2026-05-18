import streamlit as st
from firecrawl import FirecrawlApp
from openai import OpenAI
import json
import pandas as pd

# Ρύθμιση Σελίδας
st.set_page_config(page_title="Does4U - Targeted Lead Hunter", page_icon="⚡", layout="wide")
st.title("⚡ Does4U Targeted Lead Hunter v7.0")
st.subheader("Στοχευμένο Σκανάρισμα Ανοιχτών Job Boards & Subreddits")

# Διάβασμα των κλειδιών από τα Secrets του Streamlit Cloud
try:
    FIRECRAWL_API_KEY = st.secrets["FIRECRAWL_API_KEY"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("🚨 Σφάλμα: Δεν βρέθηκαν τα κλειδιά στα Secrets του Streamlit Cloud!")
    st.stop()

st.info("🎯 **Πηγές Στόχευσης:** Το Bot σκανάρει αποκλειστικά τα RemoteOK, WeWorkRemotely, r/forhire και r/pythonjobs για: *Web Scraping, AI Automations, Python Scripts, SaaS Engineering*.")

if st.button("🚀 ΕΝΑΡΞΗ ΣΤΟΧΕΥΜΕΝΟΥ ΚΥΝΗΓΙΟΥ"):
    with st.spinner("Το Firecrawl σκανάρει τα Job Boards και το GPT-4o-mini αναλύει..."):
        try:
            firecrawl_app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
            openai_client = OpenAI(api_key=OPENAI_API_KEY)
            
            # 🔥 ΕΔΩ ΕΙΝΑΙ ΤΟ ΦΙΛΤΡΟ: Ψάχνει ΜΟΝΟ σε αυτά τα συγκεκριμένα site και πουθενά αλλού!
            targeted_query = '(site:remoteok.com OR site:weworkremotely.com OR site:reddit.com/r/forhire OR site:reddit.com/r/pythonjobs) ("web scraping" OR "AI automation" OR "Python script" OR "SaaS") ("hiring" OR "looking for" OR "freelancer")'
            
            search_result = firecrawl_app.search(targeted_query, limit=8)
            
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
                st.warning("Δεν βρέθηκαν φρέσκα posts αυτή τη στιγμή σε αυτές τις πηγές.")
            else:
                leads_list = []
                
                for item in raw_results:
                    url = getattr(item, 'url', '')
                    content = getattr(item, 'markdown', '')[:4000] if getattr(item, 'markdown', '') else ''
                    
                    if not content or len(content).strip() < 200:
                        continue
                        
                    prompt = f"""
                    Είσαι ο Lead Qualifier και Μεταφραστής της εταιρείας Does4U (SaaS Engineering & AI Automations).
                    Εξετάζεις το κείμενο μιας αγγελίας εργασίας.
                    
                    Αποστολή σου:
                    1. ΕΛΕΓΧΟΣ MATCH: Επιβεβαίωσε αν το κείμενο είναι ΠΡΑΓΜΑΤΙΚΗ αγγελία ή post όπου κάποιος ΨΑΧΝΕΙ να προσλάβει ή να συνεργαστεί με developer για Web Scraping, AI Automations, Python ή SaaS. Αν είναι άσχετο, βάλε "is_match": false.
                    2. ΜΕΤΑΦΡΑΣΗ: Αν είναι match, μετάφρασε τον Τίτλο της θέσης και γράψε μια σύντομη σύνοψη των απαιτήσεων ΑΥΣΤΗΡΑ ΣΤΑ ΕΛΛΗΝΙΚΑ.
                    3. EMAIL ΕΠΙΚΟΙΝΩΝΙΑΣ: Ψάξε εξαντλητικά για email επικοινωνίας στο κείμενο ή για link επικοινωνίας. Αν δεν υπάρχει, γράψε "Δεν βρέθηκε".
                    4. COLD EMAIL: Γράψε ένα επαγγελματικό cold email εκ μέρους της Does4U στα Αγγλικά, προσφέροντας λύση για το πρόβλημά τους.
                    
                    Επέστρεψε ΑΥΣΤΗΡΑ ΜΟΝΟ ένα έγκυρο JSON αντικείμενο με αυτή τη δομή:
                    {{
                        "is_match": true ή false,
                        "translated_title": "Ο τίτλος μεταφρασμένος στα Ελληνικά",
                        "summary_greek": "Σύντομη περιγραφή του τι ζητάνε στα Ελληνικά",
                        "email": "το email που βρήκες ή Δεν βρέθηκε",
                        "generated_email": "Το έτοιμο cold email για τον πελάτη"
                    }}
                    
                    Κείμενο σελίδας:
                    {content}
                    """
                    
                    response = openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        response_format={"type": "json_object"},
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.1
                    )
                    
                    ai_data = json.loads(response.choices[0].message.content)
                    
                    if ai_data.get("is_match") is not True:
                        continue
                        
                    leads_list.append({
                        "Τίτλος (Ελληνικά)": ai_data.get("translated_title"),
                        "Τι Ζητάνε (Σύνοψη)": ai_data.get("summary_greek"),
                        "Email Επικοινωνίας": ai_data.get("email"),
                        "Σύνδεσμος (URL)": url,
                        "Έτοιμο Email Does4U": ai_data.get("generated_email")
                    })
                
                # Εμφάνιση Αποτελεσμάτων
                if len(leads_list) == 0:
                    st.info("⚠️ Το AI ανέλυσε τα πρόσφατα posts αλλά κανένα δεν ήταν 100% match για τις υπηρεσίες της Does4U αυτή τη στιγμή.")
                else:
                    df = pd.DataFrame(leads_list)
                    st.success(f"🎯 Βρέθηκαν {len(df)} πραγματικά leads, φιλτραρισμένα και μεταφρασμένα στα Ελληνικά!")
                    
                    # Πίνακας
                    st.dataframe(df[["Τίτλος (Ελληνικά)", "Τι Ζητάνε (Σύνοψη)", "Email Επικοινωνίας", "Σύνδεσμος (URL)"]], use_container_width=True)
                    
                    # Emails
                    st.markdown("### 📝 Έτοιμα Emails της Does4U προς Αντιγραφή:")
                    for idx, row in df.iterrows():
                        with st.expander(f"✉️ Pitch για: {row['Τίτλος (Ελληνικά)']} ({row['Email Επικοινωνίας']})"):
                            st.text_area("Κείμενο Email:", row['Έτοιμο Email Does4U'], height=250, key=f"txt_{idx}")
                            st.caption(f"Πηγή: {row['Σύνδεσμος (URL)']}")
                            
        except Exception as e:
            st.error(f"Παρουσιάστηκε σφάλμα: {e}")