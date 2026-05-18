import streamlit as st
from firecrawl import Firecrawl
from openai import OpenAI
import json
import pandas as pd

# Ρύθμιση Σελίδας
st.set_page_config(page_title="Does4U - Lead Volume Engine", page_icon="📈", layout="wide")
st.title("📈 Does4U Lead Volume Engine v22.0")
st.subheader("Στάδιο 1: Μαζικό Scraping από 5 Πηγές για Εξαγωγή Συγκεκριμένων Keywords")

# Διάβασμα των κλειδιών από τα Secrets του Streamlit Cloud
try:
    FIRECRAWL_API_KEY = st.secrets["FIRECRAWL_API_KEY"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("🚨 Σφάλμα: Δεν βρέθηκαν τα κλειδιά στα Secrets του Streamlit Cloud!")
    st.stop()

if st.button("🔥 ΕΝΑΡΞΗ ΜΑΖΙΚΗΣ ΣΥΛΛΟΓΗΣ ΑΠΟ 5 ΠΛΑΤΦΟΡΜΕΣ"):
    with st.spinner("Το Firecrawl σκανάρει και τις 5 πλατφόρμες για να πιάσουμε τον στόχο..."):
        
        try:
            firecrawl_app = Firecrawl(api_key=FIRECRAWL_API_KEY)
            openai_client = OpenAI(api_key=OPENAI_API_KEY)
            
            # 🌐 ΟΙ 5 ΕΣΤΙΑΣΜΕΝΕΣ ΠΗΓΕΣ ΓΙΑ ΜΕΓΙΣΤΟ ΟΓΚΟ
            targets = [
                {"platform": "Upwork", "url": "https://www.upwork.com/nx/search/jobs/?q=python%20scraping"},
                {"platform": "Freelancer", "url": "https://www.freelancer.com/jobs/python"},
                {"platform": "Fiverr", "url": "https://www.fiverr.com/search/gigs?query=python%20automation"},
                {"platform": "WeWorkRemotely", "url": "https://weworkremotely.com/categories/remote-programming-jobs"},
                {"platform": "RemoteOK", "url": "https://remoteok.com/remote-python-jobs"}
            ]
            
            all_raw_content = ""
            
            # Σαρώνομαι όλες τις πηγές
            for target in targets:
                try:
                    st.write(f"📡 Σύνδεση με: **{target['platform']}**...")
                    scrape_result = firecrawl_app.scrape(target['url'], formats=['markdown'])
                    
                    if isinstance(scrape_result, dict):
                        page_text = scrape_result.get("markdown", "")
                    else:
                        page_text = getattr(scrape_result, 'markdown', '')
                    
                    if page_text and len(page_text).strip() > 200:
                        all_raw_content += f"\n\n--- DATA FROM {target['platform']} ---\n\n" + page_text
                        st.write(f"✅ Λήφθηκαν δεδομένα από {target['platform']}.")
                    else:
                        st.write(f"⚠️ Το {target['platform']} δεν επέστρεψε επαρκές κείμενο (πιθανό block).")
                except Exception as e:
                    st.write(f"❌ Αποτυχία στο {target['platform']}: {e}")

            if not all_raw_content.strip():
                st.error("🚨 Δεν μαζεύτηκαν δεδομένα από καμία πλατφόρμα. Όλες οι πηγές μπλόκαραν το scraping.")
            else:
                with st.spinner("Το GPT-4o-mini εξάγει τα αυστηρά Keywords για τα 2 επόμενα εργαλεία..."):
                    
                    prompt = f"""
                    Είσαι ο Data Extractor της Does4U. Σου δίνω το markdown κείμενο από 5 μεγάλες πλατφόρμες εύρεσης εργασίας.
                    
                    Αποστολή σου:
                    1. ΦΙΛΤΡΑΡΙΣΜΑ: Κράτα ΜΟΝΟ αγγελίες ή posts που ζητάνε Python, Web Scraping, Automations, Bots, AI ή SaaS και έχουν ηλικία έως 5 ημέρες.
                    2. ΑΥΣΤΗΡΑ KEYWORDS: Για κάθε match, βρες και απομόνωσε ΜΟΝΟ τα στοιχεία που χρειάζονται για τα 2 εργαλεία ταυτοποίησης:
                       - Αν πρόκειται για εταιρεία/job board: Βρες το καθαρό Όνομα Εταιρείας ή Όνομα Client (για το εργαλείο εταιρειών).
                       - Αν πρόκειται για profile/user: Βρες το συγκεκριμένο Username ή ID του χρήστη (για το εργαλείο social).
                    3. Μην βάζεις όριο στο πόσα αποτελέσματα θα φέρεις. Φέρε ΟΣΑ περισσότερα βρεις μέσα στο κείμενο για να πιάσουμε τον στόχο των 10+.
                    
                    Επέστρεψε ΑΥΣΤΗΡΑ ΚΑΙ ΜΟΝΟ ένα JSON αντικείμενο:
                    {{
                        "leads": [
                            {{
                                "title_gr": "Ο τίτλος της αγγελίας στα Ελληνικά",
                                "client_company_keyword": "Όνομα Εταιρείας ή Client (Αν δεν υπάρχει, γράψε Ν/Α)",
                                "social_username_keyword": "Username ή ID χρήστη (Αν δεν υπάρχει, γράψε Ν/Α)",
                                "source_platform": "Η πλατφόρμα προέλευσης (π.χ. Upwork, WeWorkRemotely κλπ)",
                                "project_link": "Το link της αγγελίας",
                                "summary_gr": "Τι ζητάει σύντομα στα Ελληνικά"
                            }}
                        ]
                    }}
                    """
                    
                    response = openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        response_format={"type": "json_object"},
                        messages=[
                            {"role": "system", "content": "You are a precise data extractor. Return only valid JSON."},
                            {"role": "user", "content": f"{prompt}\n\nΚείμενο:\n{all_raw_content}"}
                        ],
                        temperature=0.1
                    )
                    
                    ai_data = json.loads(response.choices[0].message.content)
                    leads_list = ai_data.get("leads", [])
                    
                    if len(leads_list) == 0:
                        st.warning("⚠️ Το AI δεν εντόπισε κατάλληλα projects < 5 ημερών στο κείμενο αυτή τη στιγμή.")
                    else:
                        df = pd.DataFrame(leads_list)
                        st.success(f"🎯 Επιτυχία! Εντοπίστηκαν {len(df)} leads από τις 5 πηγές!")
                        
                        # Οργάνωση στηλών για τον πίνακα
                        df.columns = ["Project (Ελληνικά)", "Εταιρεία (Keyword 1)", "Social Username (Keyword 2)", "Πηγή", "Link", "Σύνοψη"]
                        
                        # Εμφάνιση του τελικού πίνακα
                        st.dataframe(df[["Project (Ελληνικά)", "Εταιρεία (Keyword 1)", "Social Username (Keyword 2)", "Πηγή", "Σύνοψη", "Link"]], use_container_width=True)
                        
        except Exception as main_e:
            st.error(f"🚨 Σφάλμα συστήματος: {main_e}")