import streamlit as st
from firecrawl import FirecrawlApp
from openai import OpenAI
import json
import pandas as pd

# Ρύθμιση Σελίδας
st.set_page_config(page_title="Does4U - Xing Lead Hunter", page_icon="🎯", layout="wide")
st.title("🎯 Does4U Xing Lead Hunter v4.0")
st.subheader("Αυστηρό Φιλτράρισμα Αγγελιών & Αυτόματη Μετάφραση στα Ελληνικά")

# Διάβασμα των κλειδιών από τα Secrets του Streamlit Cloud
try:
    FIRECRAWL_API_KEY = st.secrets["FIRECRAWL_API_KEY"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("🚨 Σφάλμα: Δεν βρέθηκαν τα κλειδιά στα Secrets του Streamlit Cloud!")
    st.stop()

# Κύρια Μπάρα Αναζήτησης
query = st.text_input("Τι είδους αγγελία ψάχνεις στο Xing;", placeholder="π.χ. python automation developer, web scraping expert")

if st.button("🚀 Έναρξη Κυνηγιού στο Xing"):
    if not query:
        st.warning("Γράψε ένα query για αναζήτηση.")
    else:
        with st.spinner("Αναζήτηση, αυστηρό φιλτράρισμα και μετάφραση lead..."):
            try:
                # Αρχικοποίηση εργαλείων
                firecrawl_app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
                openai_client = OpenAI(api_key=OPENAI_API_KEY)
                
                # Αναζήτηση αποκλειστικά στο Xing Jobs
                xing_query = f'site:xing.com/jobs "{query}"'
                search_result = firecrawl_app.search(xing_query, limit=5)
                
                if not search_result.data:
                    st.warning("Δεν βρέθηκαν αγγελίες στο Xing για αυτό το query.")
                else:
                    leads_list = []
                    
                    for item in search_result.data:
                        url = getattr(item, 'url', '')
                        content = getattr(item, 'markdown', '')[:4000] if getattr(item, 'markdown', '') else ''
                        
                        # Το έξυπνο Prompt που φιλτράρει, μεταφράζει και γράφει email
                        prompt = f"""
                        Είσαι ο Lead Qualifier και Μεταφραστής της εταιρείας Does4U (SaaS Engineering & AI Automations).
                        Εξετάζεις μια σελίδα/αγγελία από το Xing.
                        
                        Αποστολή σου:
                        1. ΕΛΕΓΧΟΣ MATCH: Επιβεβαίωσε αν πρόκειται για ΠΡΑΓΜΑΤΙΚΗ ΚΑΙ ΕΝΕΡΓΗ αγγελία εργασίας ή project όπου ψάχνουν developer/freelancer. Αν είναι άρθρο, προφίλ ατόμου, ή γενικό κείμενο, βάλε "is_match": false.
                        2. ΜΕΤΑΦΡΑΣΗ: Αν είναι match, μετάφρασε τον Τίτλο της θέσης και μια πολύ σύντομη σύνοψη των απαιτήσεων ΑΥΣΤΗΡΑ ΣΤΑ ΕΛΛΗΝΙΚΑ.
                        3. EMAIL ΕΠΙΚΟΙΝΩΝΙΑΣ: Ψάξε εξαντλητικά για email, όνομα υπευθύνου ή εταιρείας.
                        4. COLD EMAIL: Γράψε ένα επαγγελματικό cold email εκ μέρους της Does4U. Αν η αγγελία είναι στα Γερμανικά, γράψε το email στα Γερμανικά (ή στα Αγγλικά αν προτιμάται επαγγελματικά), προσφέροντας τις υπηρεσίες μας.
                        
                        Επέστρεψε ΑΥΣΤΗΡΑ ΜΟΝΟ ένα έγκυρο JSON αντικείμενο με αυτή τη δομή:
                        {{
                            "is_match": true ή false,
                            "translated_title": "Ο τίτλος της θέσης μεταφρασμένος στα Ελληνικά",
                            "summary_greek": "Σύντομη περιγραφή του τι ζητάνε στα Ελληνικά (1-2 προτάσεις)",
                            "email": "το email που βρήκες ή Δεν βρέθηκε",
                            "generated_email": "Το έτοιμο cold email για τον πελάτη (Γερμανικά/Αγγλικά)"
                        }}
                        
                        Κείμενο αγγελίας:
                        {content}
                        """
                        
                        response = openai_client.chat.completions.create(
                            model="gpt-4o-mini",
                            response_format={"type": "json_object"},
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.1 # Χαμηλό για μέγιστη ακρίβεια στο φιλτράρισμα
                        )
                        
                        ai_data = json.loads(response.choices[0].message.content)
                        
                        # ΦΙΛΤΡΑΡΙΣΜΑ: Αν δεν είναι αληθινή αγγελία, κόβεται αμέσως
                        if ai_data.get("is_match") is not True:
                            continue
                            
                        # Προσθήκη στη λίστα του πίνακα
                        leads_list.append({
                            "Τίτλος Θέσης (Ελληνικά)": ai_data.get("translated_title"),
                            "Τι Ζητάνε (Σύνοψη)": ai_data.get("summary_greek"),
                            "Email Επικοινωνίας": ai_data.get("email"),
                            "Σύνδεσμος (URL)": url,
                            "Έτοιμο Email Does4U": ai_data.get("generated_email")
                        })
                    
                    # Εμφάνιση Αποτελεσμάτων
                    if len(leads_list) == 0:
                        st.info("⚠️ Το AI σκάναρε το Xing αλλά δεν βρήκε κάποια φρέσκια, έγκυρη αγγελία για αυτό το query. Ο πίνακας έμεινε καθαρός.")
                    else:
                        df = pd.DataFrame(leads_list)
                        st.success(f"🎯 Βρέθηκαν {len(df)} πραγματικές αγγελίες στο Xing μεταφρασμένες στα Ελληνικά!")
                        
                        # 1. Εμφάνιση του Πίνακα στα Ελληνικά
                        st.dataframe(df[["Τίτλος Θέσης (Ελληνικά)", "Τι Ζητάνε (Σύνοψη)", "Email Επικοινωνίας", "Σύνδεσμος (URL)"]], use_container_width=True)
                        
                        # 2. Τα Emails από κάτω
                        st.markdown("### 📝 Έτοιμα Emails προς Αντιγραφή:")
                        for idx, row in df.iterrows():
                            with st.expander(f"✉️ Pitch για: {row['Τίτλος Θέσης (Ελληνικά)']} ({row['Email Επικοινωνίας']})"):
                                st.text_area("Κείμενο Email (Έτοιμο για αποστολή):", row['Έτοιμο Email Does4U'], height=250, key=f"txt_{idx}")
                                st.caption(f"Πηγή στο Xing: {row['Σύνδεσμος (URL)']}")
                                
            except Exception as e:
                st.error(f"Παρουσιάστηκε σφάλμα: {e}")