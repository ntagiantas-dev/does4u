import streamlit as st
from firecrawl import FirecrawlApp
from openai import OpenAI
import json
import pandas as pd

# Ρύθμιση Σελίδας
st.set_page_config(page_title="Does4U - Gig Board Hunter", page_icon="💰", layout="wide")
st.title("💰 Does4U Freelance Platform Hunter v16.0")
st.subheader("Στάδιο 1: Μαζικό Scraping από Freelancer.com (< 5 Ημέρες)")

# Διάβασμα των κλειδιών από τα Secrets του Streamlit Cloud
try:
    FIRECRAWL_API_KEY = st.secrets["FIRECRAWL_API_KEY"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("🚨 Σφάλμα: Δεν βρέθηκαν τα κλειδιά στα Secrets του Streamlit Cloud!")
    st.stop()

st.info("🎯 **Πηγή:** Freelancer.com | **Στόχος:** Python Scripts & Web Scraping | **Φίλτρο:** < 5 ημέρες")

if st.button("🚀 ΕΝΑΡΞΗ ΜΑΖΙΚΗΣ ΣΥΛΛΟΓΗΣ"):
    with st.spinner("Το Firecrawl σκανάρει το Freelancer.com και το GPT εξάγει τα Keywords..."):
        try:
            # Αρχικοποίηση με τα ΣΩΣΤΑ αντικείμενα του SDK
            firecrawl_app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
            openai_client = OpenAI(api_key=OPENAI_API_KEY)
            
            # Σελίδα αναζήτησης του Freelancer για Python projects
            target_url = "https://www.freelancer.com/jobs/python"
            
            # Χρήση της σωστής μεθόδου .scrape_url() πάνω στο FirecrawlApp
            scrape_result = firecrawl_app.scrape_url(target_url, params={'formats': ['markdown']})
            
            content = ""
            if isinstance(scrape_result, dict):
                content = scrape_result.get("markdown", "")
            else:
                content = getattr(scrape_result, 'markdown', '')

            if not content:
                st.error("🚨 Το Firecrawl επέστρεψε άδειο περιεχόμενο. Δοκίμασε ξανά σε λίγα δευτερόλεπτα.")
            else:
                # Το GPT αναλαμβάνει να βρει τα Keywords και να φιλτράρει την ηλικία
                prompt = f"""
                Είσαι ο Lead Qualifier της Does4U (SaaS & AI Automations Studio).
                Σου δίνω το markdown κείμενο από τη live σελίδα αγγελιών του Freelancer.com.
                
                Αποστολή σου:
                1. ΦΙΛΤΡΟ ΧΡΟΝΟΥ: Κράτα ΜΟΝΟ τα projects που έχουν δημοσιευτεί τις τελευταίες 5 ημέρες (π.χ. "Today", "1 day ago", "3 days ago", "just now"). Αν γράφει "6 days ago", "2 weeks ago" ή παλαιότερα, ΠΕΤΑΞΕ ΤΑ.
                2. ΦΙΛΤΡΟ ΘΕΜΑΤΟΣ: Κράτα ΜΟΝΟ όσα projects ζητάνε Python scripts, Web Scraping, Data Extraction, Bots, AI Automations ή SaaS Engineering.
                3. ΕΞΑΓΩΓΗ KEYWORDS: Για κάθε project που ταιριάζει, βρες το Όνομα/Username του Client, τον Τίτλο του project (μεταφρασμένο στα ΕΛΛΗΝΙΚΑ) και μια σύντομη σύνοψη στα ΕΛΛΗΝΙΚΑ.
                
                Επέστρεψε ΑΥΣΤΗΡΑ ΚΑΙ ΜΟΝΟ ένα JSON αντικείμενο με τη μορφή λίστας "leads", ακολουθώντας αυτή τη δομή:
                {{
                    "leads": [
                        {{
                            "title_gr": "Ο τίτλος του project στα Ελληνικά",
                            "client_keyword": "Το όνομα ή το username του client για το επόμενο εργαλείο",
                            "project_link": "Το URL της αγγελίας",
                            "summary_gr": "Τι ακριβώς ζητάει στα Ελληνικά",
                            "age": "Πότε δημοσιεύτηκε"
                        }}
                    ]
                }}
                
                Αν δεν βρεις κανένα project που να είναι κάτω από 5 ημέρες και να αφορά Python/Scraping, επέστρεψε: {{"leads": []}}
                
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
                    st.warning("⚠️ Σκανάραμε τη σελίδα, αλλά δεν βρέθηκαν projects για Python/Scraping νεότερα των 5 ημερών αυτή τη στιγμή.")
                else:
                    df = pd.DataFrame(leads_list)
                    st.success(f"🎯 Επιτυχία! Το AI εντόπισε {len(df)} πρόσφατα projects και εξήγαγε τα Keywords!")
                    
                    # Μετονομασία στηλών για τον πίνακα
                    df.columns = ["Project (Ελληνικά)", "Client / Username (Keyword)", "Link Project", "Τι Ζητάει (Σύνοψη)", "Ηλικία"]
                    
                    # Εμφάνιση πίνακα
                    st.dataframe(df[["Project (Ελληνικά)", "Client / Username (Keyword)", "Ηλικία", "Τι Ζητάει (Σύνοψη)", "Link Project"]], use_container_width=True)
                    st.info("💡 **Έτοιμα για το Στάδιο 2:** Κράτα τη στήλη 'Client / Username' για να τη δώσεις στο εργαλείο εύρεσης email ώστε να γίνει το match.")
                    
        except Exception as e:
            st.error(f"Παρουσιάστηκε σφάλμα κατά την εκτέλεση: {e}")