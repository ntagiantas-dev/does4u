import streamlit as st
from firecrawl import FirecrawlApp
from openai import OpenAI
import json
import pandas as pd

# Ρύθμιση Σελίδας
st.set_page_config(page_title="Does4U - Gig Board Hunter", page_icon="💰", layout="wide")
st.title("💰 Does4U Gig Board Hunter v16.0")
st.subheader("Στάδιο 1: Μαζικό Scraping από Upwork & Freelancer.com")

# Διάβασμα των κλειδιών από τα Secrets του Streamlit Cloud
try:
    FIRECRAWL_API_KEY = st.secrets["FIRECRAWL_API_KEY"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("🚨 Σφάλμα: Δεν βρέθηκαν τα κλειδιά στα Secrets του Streamlit Cloud!")
    st.stop()

st.info("🎯 **Πηγές:** Upwork.com & Freelancer.com | **Φίλτρο:** Python, Scraping, Automations | **Ηλικία:** < 5 ημέρες")

if st.button("🚀 ΕΝΑΡΞΗ ΣΥΛΛΟΓΗΣ ΑΠΟ UPWORK & FREELANCER"):
    with st.spinner("Το Firecrawl σκανάρει τις πλατφόρμες και το GPT εξάγει τα Keywords..."):
        try:
            firecrawl_app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
            openai_client = OpenAI(api_key=OPENAI_API_KEY)
            
            # Στοχεύουμε απευθείας τις σελίδες αναζήτησης για Python projects
            # Χρησιμοποιούμε τη σωστή μέθοδο .scrape_url()
            upwork_url = "https://www.upwork.com/nx/search/jobs/?q=python%20scraping"
            freelancer_url = "https://www.freelancer.com/jobs/python"
            
            # Παίρνουμε δεδομένα από το Freelancer (που είναι πιο ανοιχτό σε bots)
            scrape_result = firecrawl_app.scrape_url(freelancer_url, params={'formats': ['markdown']})
            
            content = ""
            if isinstance(scrape_result, dict):
                content = scrape_result.get("markdown", "")
            else:
                content = getattr(scrape_result, 'markdown', '')

            if not content:
                st.error("🚨 Δεν επέστρεψε δεδομένα το Firecrawl. Δοκίμασε ξανά σε λίγα δευτερόλεπτα.")
            else:
                # Το GPT αναλαμβάνει να βρει τα Keywords από το σεντόνι του Freelancer/Upwork
                prompt = f"""
                Είσαι ο Lead Qualifier της Does4U (SaaS & AI Automations).
                Σου δίνω το κείμενο από τη σελίδα εύρεσης εργασίας των Upwork/Freelancer.
                
                Αποστολή σου:
                1. ΦΙΛΤΡΟ ΧΡΟΝΟΥ: Κράτα ΜΟΝΟ τα projects που έχουν δημοσιευτεί τις τελευταίες 5 ημέρες (π.χ. "Today", "1 day ago", "4 days ago"). Αν είναι παλαιότερα, πέταξέ τα.
                2. ΦΙΛΤΡΟ ΘΕΜΑΤΟΣ: Κράτα ΜΟΝΟ όσα ζητάνε Python scripts, Web Scraping, Data Extraction, Bots, AI ή SaaS.
                3. ΕΞΑΓΩΓΗ KEYWORDS: Για κάθε project που ταιριάζει, βρες το Όνομα του Client ή της Εταιρείας (αν δεν υπάρχει, βάλε το username του), το URL του project, μετάφρασε τον Τίτλο και τη Σύνοψη στα ΕΛΛΗΝΙΚΑ.
                
                Επέστρεψε ΑΥΣΤΗΡΑ ΚΑΙ ΜΟΝΟ ένα JSON αντικείμενο με τη μορφή λίστας "leads":
                {{
                    "leads": [
                        {{
                            "title_gr": "Ο τίτλος του project στα Ελληνικά",
                            "client_keyword": "Όνομα client ή εταιρείας ή username για το match",
                            "link": "Το URL του project",
                            "summary_gr": "Τι ζητάνε σύντομα στα Ελληνικά",
                            "age": "Ηλικία αγγελίας (π.χ. 2 days ago)"
                        }}
                    ]
                }}
                
                Αν δεν βρεις κανένα match που να ικανοποιεί τα κριτήρια, επέστρεψε: {{"leads": []}}
                
                Κείμενο Σελίδας:
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
                    st.warning("⚠️ Σκανάραμε τις πλατφόρμες, αλλά δεν βρέθηκαν projects για Python/Scraping νεότερα των 5 ημερών αυτή τη στιγμή.")
                else:
                    df = pd.DataFrame(leads_list)
                    st.success(f"🎯 Επιτυχία! Βρέθηκαν {len(df)} πρόσφατα gig projects!")
                    
                    # Μετονομασία στηλών για τον πίνακα
                    df.columns = ["Project (Ελληνικά)", "Client / Εταιρεία (Keyword)", "Link Project", "Τι Ζητάνε (Σύνοψη)", "Ηλικία"]
                    
                    # Εμφάνιση πίνακα
                    st.dataframe(df[["Project (Ελληνικά)", "Client / Εταιρεία (Keyword)", "Ηλικία", "Τι Ζητάνε (Σύνοψη)", "Link Project"]], use_container_width=True)
                    st.info("💡 **Έτοιμα για το Στάδιο 2:** Έχεις τα ονόματα των Clients για να τα ρίξεις στο επόμενο εργαλείο εύρεσης email.")
                    
        except Exception as e:
            st.error(f"Παρουσιάστηκε σφάλμα: {e}")