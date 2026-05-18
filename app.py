import streamlit as st
import requests
from openai import OpenAI
import json
import pandas as pd

# Ρύθμιση Σελίδας
st.set_page_config(page_title="Does4U - Jina Xing Sniper v0.0.1", page_icon="🦊", layout="wide")
st.title("🦊 Does4U Jina AI Xing Sniper v0.0.1")
st.subheader("Στάδιο 1: Απομονωμένη Συλλογή Keywords από το Xing")

# Έλεγχος και Διάβασμα των κλειδιών από τα Secrets
try:
    JINA_API_KEY = st.secrets["JINA_API_KEY"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("🚨 Σφάλμα: Λείπει το JINA_API_KEY ή το OPENAI_API_KEY από τα Secrets του Streamlit!")
    st.stop()

# Το στοχευμένο URL στο Xing για Python Remote εργασίες
XING_TARGET_URL = "https://www.xing.com/jobs/search?keywords=python%20remote"

st.info(f"🎯 **Στόχος:** Σκανάρισμα της σελίδας: `{XING_TARGET_URL}`")

if st.button("🔥 ΕΝΑΡΞΗ ΞΕΣΚΟΝΙΣΜΑΤΟΣ JINA v0.0.1"):
    st.write("📡 Η Jina AI χτυπάει το Xing και μετατρέπει τη σελίδα σε Markdown...")
    
    try:
        # Κλήση στο Jina Reader API
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
            
            if len(raw_markdown).strip() < 200:
                st.error("⚠️ Το κείμενο που επέστρεψε η Jina είναι πολύ μικρό. Πιθανό block ασφαλείας από το Xing.")
            else:
                st.success(f"✅ Η Jina AI διάβασε τη σελίδα επιτυχώς ({len(raw_markdown)} χαρακτήρες)!")
                
                with st.spinner("Το GPT-4o-mini αναλύει το κείμενο για να απομονώσει τα Keywords..."):
                    openai_client = OpenAI(api_key=OPENAI_API_KEY)
                    
                    prompt = """
                    Είσαι ο precise Data Extractor της Does4U. Σου δίνω το Markdown κείμενο μιας σελίδας αγγελιών από το Xing.
                    
                    Αποστολή σου:
                    1. ΦΙΛΤΡΑΡΙΣΜΑ: Κράτα ΜΟΝΟ τις αγγελίες που ζητάνε Python, Web Scraping, Automations, Bots, AI ή SaaS και είναι πρόσφατες (έως 5-6 ημέρες).
                    2. ΑΥΣΤΗΡΑ KEYWORDS: Για κάθε match, βρες και εξήγαγε ΜΟΝΟ τα στοιχεία που χρειαζόμαστε για το επόμενο στάδιο (Match):
                       - Καθαρό Όνομα Εταιρείας ή Όνομα Client (Keyword 1). Αν δεν υπάρχει, γράψε Ν/Α.
                       - Username ή ID χρήστη (Keyword 2). Αν δεν υπάρχει, γράψε Ν/Α.
                    3. Μην βάζεις κανέναν κόφτη στον όγκο. Βγάλε ΟΛΑ τα πιθανά leads που υπάρχουν μέσα στο κείμενο.
                    
                    Επέστρεψε ΑΥΣΤΗΡΑ ΚΑΙ ΜΟΝΟ ένα JSON αντικείμενο με τη συγκεκριμένη δομή:
                    {
                        "leads": [
                            {
                                "title_gr": "Ο τίτλος της αγγελίας στα Ελληνικά",
                                "client_company_keyword": "Όνομα Εταιρείας ή Client",
                                "social_username_keyword": "Username ή ID χρήστη",
                                "project_link": "Το link της αγγελίας στο Xing",
                                "summary_gr": "Τι ζητάει σύντομα στα Ελληνικά"
                            }
                        ]
                    }
                    """
                    
                    ai_response = openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        response_format={"type": "json_object"},
                        messages=[
                            {"role": "system", "content": "You are a data extraction bot. Return only valid JSON."},
                            {"role": "user", "content": f"{prompt}\n\nΚείμενο Xing:\n{raw_markdown}"}
                        ],
                        temperature=0.2
                    )
                    
                    ai_data = json.loads(ai_response.choices[0].message.content)
                    leads_list = ai_data.get("leads", [])
                    
                    if len(leads_list) == 0:
                        st.warning("⚠️ Το AI διάβασε το Markdown αλλά δεν εντόπισε πρόσφατες αγγελίες Python.")
                    else:
                        df = pd.DataFrame(leads_list)
                        st.success(f"🔥 Επιτυχία! Εντοπίστηκαν {len(df)} leads από το Xing!")
                        
                        # Μορφοποίηση στηλών για την οθόνη σου
                        df.columns = ["Project (Ελληνικά)", "Εταιρεία (Keyword 1)", "Social Username (Keyword 2)", "Link", "Σύνοψη"]
                        st.dataframe(df[["Project (Ελληνικά)", "Εταιρεία (Keyword 1)", "Social Username (Keyword 2)", "Σύνοψη", "Link"]], use_container_width=True)
                        
    except Exception as main_e:
        st.error(f"🚨 Σφάλμα κατά την εκτέλεση: {main_e}")