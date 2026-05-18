import streamlit as st
import requests
from openai import OpenAI
import json
import pandas as pd

# Ρύθμιση Σελίδας
st.set_page_config(page_title="Does4U - Fixed-Price Sniper v0.0.4", page_icon="🦊", layout="wide")
st.title("🦊 Does4U Jina AI Fixed-Price Sniper v0.0.4")
st.subheader("Στάδιο 1: Φιλτράρισμα για One-Off Projects (Παράδοση & Πληρωμή)")

# Έλεγχος και Διάβασμα των κλειδιών από τα Secrets
try:
    JINA_API_KEY = st.secrets["JINA_API_KEY"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("🚨 Σφάλμα: Λείπει το JINA_API_KEY ή το OPENAI_API_KEY από τα Secrets του Streamlit!")
    st.stop()

# 🎯 ΝΕΟ URL: Στοχεύουμε ειδικά σε Freelance/Projekt κομμάτια στο Xing
XING_TARGET_URL = "https://www.xing.com/jobs/search?keywords=python%20freelance"

st.info(f"🎯 **Στόχος:** Αναζήτηση One-Off Projects στην πηγή: `{XING_TARGET_URL}`")

if st.button("🔥 ΕΝΑΡΞΗ ΦΙΛΤΡΑΡΙΣΜΑΤΟΣ JINA v0.0.4"):
    st.write("📡 Η Jina AI σκανάρει το Xing για Freelance ευκαιρίες...")
    
    try:
        jina_endpoint = f"https://r.jina.ai/{XING_TARGET_URL}"
        headers = {
            "Authorization": f"Bearer {JINA_API_KEY}",
            "X-Return-Format": "markdown"
        }
        
        response = requests.get(jina_endpoint, headers=headers)
        
        if response.status_code != 200:
            st.error(f"❌ Η Jina AI επέστρεψε σφάλμα συστήματος (Status Code: {response.status_code}).")
        else:
            raw_markdown = response.text
            
            if not raw_markdown or len(raw_markdown.strip()) < 200:
                st.error("⚠️ Το κείμενο που επέστρεψε η Jina είναι πολύ μικρό ή άδειο.")
            else:
                st.success(f"✅ Η Jina AI διάβασε τη σελίδα επιτυχώς ({len(raw_markdown)} χαρακτήρες)!")
                
                with st.spinner("Το GPT-4o-mini ξεσκαρτάρει μόνιμες δουλειές και κρατάει ΜΟΝΟ τα One-Off Projects..."):
                    openai_client = OpenAI(api_key=OPENAI_API_KEY)
                    
                    prompt = """
                    Είσαι ο φονικός Data Extractor της Does4U. Σου δίνω το Markdown κείμενο αγγελιών από το Xing.
                    
                    Η ΑΠΟΣΤΟΛΗ ΣΟΥ ΕΙΝΑΙ ΕΞΑΙΡΕΤΙΚΑ ΚΡΙΣΙΜΗ:
                    Θέλουμε ΜΟΝΟ projects που είναι "Fixed-Price" ή "Projektbasiert" (One-off / Παράδοση και τέλος). 
                    Πέταξε στα σκουπίδια θέσεις για μόνιμη απασχόληση (Festanstellung, Full-time, Vollzeit) ή μακροχρόνια συμβόλαια που ζητάνε 'υπάλληλο'.
                    
                    Κράτα αγγελίες που:
                    - Ζητάνε εξωτερικό συνεργάτη (Freelancer / Κατ' αποκοπήν).
                    - Αφορούν συγκεκριμένο task (π.χ. "Φτιάξε ένα bot", "Κάνε migration μια βάση δεδομένων", "Στήσε ένα automation").
                    - Είναι Python, Web Scraping, AI, Bots ή SaaS.
                    
                    Για κάθε match, εξήγαγε:
                    - Καθαρό Όνομα Εταιρείας ή Όνομα Client (Keyword 1).
                    - Username ή ID χρήστη αν υπάρχει, αλλιώς Ν/Α (Keyword 2).
                    
                    Επέστρεψε ΑΥΣΤΗΡΑ ΚΑΙ ΜΟΝΟ ένα JSON αντικείμενο με τη συγκεκριμένη δομή:
                    {
                        "leads": [
                            {
                                "title_gr": "Ο τίτλος του project στα Ελληνικά",
                                "client_company_keyword": "Όνομα Εταιρείας ή Client",
                                "social_username_keyword": "Username ή ID χρήστη",
                                "project_link": "Το link του project στο Xing",
                                "summary_gr": "Τι συγκεκριμένο έργο ζητάνε να παραδοθεί (στα Ελληνικά)"
                            }
                        ]
                    }
                    """
                    
                    ai_response = openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        response_format={"type": "json_object"},
                        messages=[
                            {"role": "system", "content": "You are a data extraction bot filtering strictly for freelance, one-off projects. Return only valid JSON."},
                            {"role": "user", "content": f"{prompt}\n\nΚείμενο Xing:\n{raw_markdown}"}
                        ],
                        temperature=0.1 # Χαμηλό temperature για μέγιστη ακρίβεια στα φίλτρα
                    )
                    
                    ai_data = json.loads(ai_response.choices[0].message.content)
                    leads_list = ai_data.get("leads", [])
                    
                    if len(leads_list) == 0:
                        st.warning("⚠️ Το AI δεν βρήκε καθαρά 'one-off' projects σε αυτή τη σελίδα. Όλες οι αγγελίες αφορούσαν μόνιμη απασχόληση.")
                    else:
                        df = pd.DataFrame(leads_list)
                        st.success(f"🔥 Επιτυχία! Εντοπίστηκαν {len(df)} One-Off Projects (Μια φορά και τέλος)!")
                        
                        df.columns = ["Project (Ελληνικά)", "Εταιρεία (Keyword 1)", "Social Username (Keyword 2)", "Link", "Τι πρέπει να παραδώσεις"]
                        st.dataframe(df[["Project (Ελληνικά)", "Εταιρεία (Keyword 1)", "Social Username (Keyword 2)", "Τι πρέπει να παραδώσεις", "Link"]], use_container_width=True)
                        
    except Exception as main_e:
        st.error(f"🚨 Σφάλμα κατά την εκτέλεση: {main_e}")