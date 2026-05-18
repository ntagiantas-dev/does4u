import streamlit as st
# 🔥 ΕΙΣΑΓΩΓΗ ΤΗΣ ΣΩΣΤΗΣ ΒΙΒΛΙΟΘΗΚΗΣ ΣΥΜΦΩΝΑ ΜΕ ΤΟ OFFICIAL DOCS
from firecrawl import Firecrawl
from openai import OpenAI
import json
import pandas as pd

# Ρύθμιση Σελίδας
st.set_page_config(page_title="Does4U - Full Lead Prospector", page_icon="💰", layout="wide")
st.title("💰 Does4U Full-Scale Lead Prospector v19.0")
st.subheader("Στάδιο 1: Καθαρό Scraping & Keywords Extraction από Upwork & Freelancer")

# Διάβασμα των κλειδιών από τα Secrets του Streamlit Cloud
try:
    FIRECRAWL_API_KEY = st.secrets["FIRECRAWL_API_KEY"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("🚨 Σφάλμα: Δεν βρέθηκαν τα κλειδιά στα Secrets του Streamlit Cloud!")
    st.stop()

st.markdown("""
### 📊 Προδιαγραφές Συστήματος:
* **Πηγές:** Freelancer.com & Upwork (Search Pages)
* **Tech Stack Φίλτρου:** Python, Web Scraping, Data Extraction, AI Automations, Bots, SaaS Engineering
* **Ηλικία Αγγελίας:** Αυστηρά λιγότερο από 5 ημέρες
""")

if st.button("🚀 ΕΝΑΡΞΗ ΠΛΗΡΟΥΣ ΜΑΖΙΚΗΣ ΣΥΛΛΟΓΗΣ"):
    with st.spinner("Το Firecrawl σκανάρει παράλληλα τις πλατφόρμες..."):
        
        try:
            # 🔥 ΑΡΧΙΚΟΠΟΙΗΣΗ ΜΕ ΤΟ ΣΩΣΤΟ ΑΝΤΙΚΕΙΜΕΝΟ ΤΟΥ SDK
            firecrawl_app = Firecrawl(api_key=FIRECRAWL_API_KEY)
            openai_client = OpenAI(api_key=OPENAI_API_KEY)
            
            # Λίστα με τα URLs
            targets = [
                {"platform": "Freelancer", "url": "https://www.freelancer.com/jobs/python"},
                {"platform": "Upwork", "url": "https://www.upwork.com/nx/search/jobs/?q=python%20scraping"}
            ]
            
            all_raw_content = ""
            
            # Scrape όλων των πηγών
            for target in targets:
                try:
                    st.write(f"📡 Σύνδεση με {target['platform']}...")
                    # 🔥 Χρήση της επίσημης μεθόδου .scrape με παραμετροποίηση formats
                    scrape_result = firecrawl_app.scrape(target['url'], formats=['markdown'])
                    
                    if isinstance(scrape_result, dict):
                        page_text = scrape_result.get("markdown", "")
                    else:
                        page_text = getattr(scrape_result, 'markdown', '')
                    
                    if page_text:
                        all_raw_content += f"\n\n--- DATA FROM {target['platform']} ---\n\n" + page_text
                        st.write(f"✅ Λήφθηκαν δεδομένα από {target['platform']}.")
                    else:
                        st.write(f"⚠️ Η σελίδα του {target['platform']} επέστρεψε κενό κείμενο.")
                except Exception as e:
                    st.write(f"❌ Αποτυχία scraping στο {target['platform']}: {e}")

            if not all_raw_content.strip():
                st.error("🚨 Δεν μαζεύτηκαν δεδομένα από καμία πλατφόρμα. Το Firecrawl έφαγε block ή οι σελίδες άλλαξαν δομή.")
            else:
                with st.spinner("Το GPT-4o-mini αναλύει ολόκληρο το πακέτο δεδομένων χωρίς περικοπές..."):
                    
                    prompt = f"""
                    Είσαι ο Lead Qualifier και Data Engineer της Does4U (SaaS & AI Automations Studio).
                    Σου δίνω το πλήρες markdown κείμενο από τις σελίδες αγγελιών του Freelancer και του Upwork.
                    
                    Αποστολή σου:
                    1. ΦΙΛΤΡΟ ΧΡΟΝΟΥ: Έλεγξε πότε δημοσιεύτηκε το κάθε project. Κράτα ΜΟΝΟ όσα είναι έως 5 ημέρες παλιά (π.χ. "Today", "just now", "1 day ago", "3 days ago"). Οτιδήποτε παλαιότερο (π.χ. 6+ ημέρες, 2 εβδομάδες, 1 μήνα) ΠΕΤΑΞΕ ΤΟ.
                    2. ΦΙΛΤΡΟ ΘΕΜΑΤΟΣ: Κράτα ΜΟΝΟ projects που ζητάνε Python scripts, Web Scraping, Data Extraction, Bots, AI Automations, OpenAI API integrations ή SaaS Web Apps.
                    3. ΕΞΑΓΩΓΗ KEYWORDS: Για κάθε project που περνάει τα φίλτρα, εξήγαγε:
                       - Το όνομα ή το username του Client/Εταιρείας (για να το δώσουμε στο επόμενο εργαλείο).
                       - Το URL/Link της αγγελίας.
                       - Τον τίτλο της θέσης μεταφρασμένο στα ΕΛΛΗΝΙΚΑ.
                       - Μια σύντομη σύνοψη των τεχνικών απαιτήσεων στα ΕΛΛΗΝΙΚΑ.
                    
                    Επέστρεψε ΑΥΣΤΗΡΑ ΚΑΙ ΜΟΝΟ ένα έγκυρο JSON αντικείμενο με τη μορφή λίστας "leads", ακολουθώντας ακριβώς αυτή τη δομή:
                    {{
                        "leads": [
                            {{
                                "title_gr": "Ο τίτλος του project στα Ελληνικά",
                                "client_keyword": "Το όνομα ή το username του client",
                                "project_link": "Το URL της αγγελίας",
                                "summary_gr": "Τι ακριβώς ζητάει ο πελάτης στα Ελληνικά",
                                "posted_age": "Πότε δημοσιεύτηκε"
                            }}
                        ]
                    }}
                    
                    Αν δεν βρεις κανένα project που να ταιριάζει και στα δύο κριτήρια, επέστρεψε: {{"leads": []}}
                    
                    Κείμενο Προς Ανάλυση:
                    {all_raw_content}
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
                        st.warning("⚠️ Οι σελίδες σκανάρονταν με επιτυχία, αλλά το AI δεν βρήκε κανένα project για Python/Scraping που να είναι νεότερο των 5 ημερών αυτή τη στιγμή.")
                    else:
                        df = pd.DataFrame(leads_list)
                        st.success(f"🎯 Επιτυχία! Το AI επεξεργάστηκε όλα τα δεδομένα και απομόνωσε {len(df)} ενεργά leads!")
                        
                        df.columns = ["Project (Ελληνικά)", "Client / Username (Keyword)", "Link Project", "Τι Ζητάνε (Σύνοψη)", "Ηλικία"]
                        st.dataframe(df[["Project (Ελληνικά)", "Client / Username (Keyword)", "Ηλικία", "Τι Ζητάνε (Σύνοψη)", "Link Project"]], use_container_width=True)
                        st.info("💡 **Έτοιμα για το Στάδιο 2:** Η λίστα με τα Keywords είναι έτοιμη για να τροφοδοτήσει το επόμενο εργαλείο εύρεσης email.")
                        
        except Exception as main_e:
            st.error(f"🚨 Γενικό Σφάλμα Εφαρμογής: {main_e}")