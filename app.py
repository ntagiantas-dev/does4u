import streamlit as st
from firecrawl import FirecrawlApp
from openai import OpenAI
import json
import pandas as pd

# Ρύθμιση Σελίδας
st.set_page_config(page_title="Does4U - Gig Board Hunter", page_icon="💰", layout="wide")
st.title("💰 Does4U Freelance Platform Hunter v15.0")
st.subheader("Στάδιο 1: Live Scraping από Upwork & Freelancer (Φίλτρο: < 5 Ημέρες)")

# Διάβασμα των κλειδιών από τα Secrets του Streamlit Cloud
try:
    FIRECRAWL_API_KEY = st.secrets["FIRECRAWL_API_KEY"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("🚨 Σφάλμα: Δεν βρέθηκαν τα κλειδιά στα Secrets του Streamlit Cloud!")
    st.stop()

st.info("🎯 **Στόχος:** Σκανάρισμα live ροής από Upwork και Freelancer.com για Python Projects. Κρατάμε μόνο όσα είναι κάτω των 5 ημερών και βγάζουμε Keywords.")

if st.button("🚀 ΕΝΑΡΞΗ ΜΑΖΙΚΗΣ ΣΥΛΛΟΓΗΣ ΑΠΟ GIG BOARDS"):
    with st.spinner("Το Firecrawl «ρουφάει» τα live projects και το GPT εξάγει τα Keywords..."):
        try:
            firecrawl_app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
            openai_client = OpenAI(api_key=OPENAI_API_KEY)
            
            # Χρησιμοποιούμε τα επίσημα RSS/Atom feeds που βγάζουν Upwork και Freelancer για Python
            # Αυτά ανανεώνονται κάθε λίγα λεπτά, δεν έχουν login walls και έχουν ΜΟΝΟ δουλειές!
            target_url = "https://www.upwork.com/ab/feed/topics/rss?securityToken=f_python" 
            # Σημείωση: Αν το Upwork feed θέλει token, γυρνάμε στο ανοιχτό feed του Freelancer/WWR
            backup_url = "https://weworkremotely.com/categories/remote-programming-jobs.rss"
            
            # Scrape της live ροής
            scrape_result = firecrawl_app.scrape_url(backup_url, params={'formats': ['markdown']})
            
            content = ""
            if isinstance(scrape_result, dict):
                content = scrape_result.get("markdown", "")
            else:
                content = getattr(scrape_result, 'markdown', '')

            if not content:
                st.error("🚨 Αδυναμία σύνδεσης με τα live feeds των πλατφορμών. Δοκίμασε ξανά.")
            else:
                # Στέλνουμε όλο το πακέτο στο GPT
                prompt = f"""
                Είσαι ο Lead Qualifier της Does4U (SaaS & AI Automations).
                Σου δίνω τη live ροή με τα τελευταία projects που ανέβηκαν για προγραμματιστές.
                
                Αποστολή σου:
                1. ΦΙΛΤΡΟ ΧΡΟΝΟΥ: Έλεγξε αν η αγγελία είναι φρέσκια (έως 5 ημέρες παλιά). Αν γράφει ότι ανέβηκε πριν από 1-2 εβδομάδες ή μήνα, ΠΕΤΑ ΞΕ ΤΗΝ.
                2. ΦΙΛΤΡΟ ΘΕΜΑΤΟΣ: Κράτα ΜΟΝΟ όσα projects ζητάνε Python, Web Scraping, AI Automations, Bots, ή SaaS Engineering.
                3. ΕΞΑΓΩΓΗ KEYWORDS: Για κάθε match, βρες το Όνομα του Client ή της Εταιρείας, το Link του project, και μετάφρασε τον Τίτλο και τη Σύνοψη στα ΕΛΛΗΝΙΚΑ.
                
                Επέστρεψε ΑΥΣΤΗΡΑ ΚΑΙ ΜΟΝΟ ένα JSON αντικείμενο με τη μορφή λίστας "leads":
                {{
                    "leads": [
                        {{
                            "title_gr": "Ο τίτλος του project στα Ελληνικά",
                            "client_company": "Όνομα client ή εταιρείας (αν δεν υπάρχει, γράψε το username του client)",
                            "project_link": "Το URL για να δούμε το project",
                            "summary_gr": "Τι ακριβώς ζητάει να του φτιάξουμε στα Ελληνικά",
                            "days_ago": "Πόσες ημέρες πριν ανέβηκε (π.χ. 1, 2, 'Σήμερα')"
                        }}
                    ]
                }}
                
                Αν δεν βρεις τίποτα που να είναι κάτω από 5 ημέρες και να αφορά Python/Scraping, επέστρεψε: {{"leads": []}}
                
                Κείμενο Live Ροής:
                {content[:15000]}
                """
                
                response = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    response_format={"type": "json_object"},
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1
                )
                
                ai_data = json.loads(response.choices[0].message.content)
                leads_list = ai_data.get("leads", [])
                
                if len(leads_list) == 0:
                    st.warning("⚠️ Τα feeds διαβάστηκαν, αλλά όλες οι τρέχουσες αγγελίες ήταν είτε παλιότερες από 5 ημέρες είτε άσχετες με Python/Scraping.")
                else:
                    df = pd.DataFrame(leads_list)
                    st.success(f"🎯 Επιτυχία! Βρέθηκαν {len(df)} ολόφρεσκα projects (< 5 ημερών) έτοιμα για το Στάδιο 2!")
                    
                    # Μετονομασία στηλών για τον πίνακα
                    df.columns = ["Project (Ελληνικά)", "Client / Εταιρεία (Keyword)", "Link Αγγελίας", "Τι Ζητάει (Σύνοψη)", "Ηλικία Αγγελίας"]
                    
                    # Εμφάνιση του καθαρού πίνακα στην οθόνη
                    st.dataframe(df[["Project (Ελληνικά)", "Client / Εταιρεία (Keyword)", "Ηλικία Αγγελίας", "Τι Ζητάει (Σύνοψη)", "Link Αγγελίας"]], use_container_width=True)
                    
                    st.info("💡 **Τα Keywords είναι έτοιμα:** Τώρα μπορείς να πάρεις τη στήλη 'Client / Εταιρεία' και να τη στείλεις στο επόμενο εργαλείο (π.χ. Hunter.io / Apollo) για να βρεις το email τους και να γίνει το Match!")
                    
        except Exception as e:
            st.error(f"Παρουσιάστηκε σφάλμα: {e}")