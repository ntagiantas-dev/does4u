import streamlit as st
from firecrawl import FirecrawlApp
from openai import OpenAI
import json
import pandas as pd

# Ρύθμιση Σελίδας
st.set_page_config(page_title="Deal Hunter AI", page_icon="🎯", layout="wide")
st.title("🎯 Deal Hunter AI v2.1")
st.subheader("Αυτοματοποιημένο Κυνήγι Leads & Σύνταξη Emails μέσω Streamlit Cloud Secrets")

# Διάβασμα των κλειδιών από τα Secrets του Streamlit Cloud
try:
    FIRECRAWL_API_KEY = st.secrets["FIRECRAWL_API_KEY"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("🚨 Σφάλμα: Δεν βρέθηκαν τα κλειδιά στα Secrets του Streamlit! Παρακαλώ πρόσθεσε τα 'FIRECRAWL_API_KEY' και 'OPENAI_API_KEY'.")
    st.stop()

# Κύρια Μπάρα Αναζήτησης
query = st.text_input("Τι είδους αγγελίες/leads ψάχνεις σήμερα;", placeholder="e.g. looking for python web scraper developer")

if st.button("🚀 Έναρξη Κυνηγιού"):
    if not query:
        st.warning("Γράψε ένα query για αναζήτηση.")
    else:
        with st.spinner("Ο Deal Hunter σκανάρει το web και το GPT-4o-mini αναλύει..."):
            try:
                # Αρχικοποίηση εργαλείων με τα κλειδιά από τα Secrets
                firecrawl_app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
                openai_client = OpenAI(api_key=OPENAI_API_KEY)
                
                # Αναζήτηση με Firecrawl (φέρνουμε τα top 4 αποτελέσματα)
                search_result = firecrawl_app.search(query, params={"limit": 4})
                
                if not search_result.get("data"):
                    st.warning("Δεν βρέθηκαν αποτελέσματα.")
                else:
                    leads_list = []
                    
                    for item in search_result.get("data", []):
                        title = item.get('title', 'Αγγελία χωρίς τίτλο')
                        url = item.get('url')
                        content = item.get('markdown', '')[:3000]
                        
                        # Prompt για JSON Mode
                        prompt = f"""
                        Διάβασε το κείμενο αυτής της αγγελίας και επέστρεψε ΜΟΝΟ ένα έγκυρο JSON αντικείμενο (χωρίς markdown code blocks ή άλλες επεξηγήσεις) με τα εξής ακριβώς πεδία:
                        - "email": Το email επικοινωνίας που βρήκες. Αν δεν υπάρχει, γράψε "Δεν βρέθηκε".
                        - "lead_quality": Αξιολόγησε από "High", "Medium", "Low" το πόσο ταιριάζει η αγγελία.
                        - "generated_email": Γράψε ένα σύντομο, άκρως επαγγελματικό cold email (στα Ελληνικά αν η αγγελία είναι ελληνική, στα Αγγλικά αν είναι ξένη) που προσφέρει λύσεις Scraping/Bots/AI βασισμένο στις ανάγκες τους.
                        
                        Κείμενο αγγελίας:
                        {content}
                        """
                        
                        # Κλήση στην OpenAI
                        response = openai_client.chat.completions.create(
                            model="gpt-4o-mini",
                            response_format={"type": "json_object"},
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.7
                        )
                        
                        ai_data = json.loads(response.choices[0].message.content)
                        
                        leads_list.append({
                            "Τίτλος Αγγελίας": title,
                            "Email Επικοινωνίας": ai_data.get("email"),
                            "Ποιότητα (Lead Quality)": ai_data.get("lead_quality"),
                            "Σύνδεσμος (URL)": url,
                            "Έτοιμο Email": ai_data.get("generated_email")
                        })
                    
                    # Δημιουργία Πίνακα
                    df = pd.DataFrame(leads_list)
                    
                    st.success("🎯 Το κυνήγι ολοκληρώθηκε!")
                    
                    # 1. Εμφάνιση Πίνακα Αποτελεσμάτων
                    st.dataframe(df, use_container_width=True)
                    
                    # 2. Ανάπτυξη των Emails κάτω από τον πίνακα
                    st.markdown("### 📝 Αναλυτικά τα Έτοιμα Emails για Αντιγραφή:")
                    for idx, row in df.iterrows():
                        with st.expander(f"✉️ Email για: {row['Τίτλος Αγγελίας']} ({row['Email Επικοινωνίας']})"):
                            st.text_area("Αντιγράψτε το κείμενο:", row['Έτοιμο Email'], height=250, key=f"txt_{idx}")
                            st.caption(f"Σύνδεσμος αγγελίας: {row['Σύνδεσμος (URL)']}")
                            
            except Exception as e:
                st.error(f"Παρουσιάστηκε σφάλμα: {e}")