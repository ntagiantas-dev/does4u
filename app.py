import streamlit as st
from firecrawl import FirecrawlApp
from openai import OpenAI
import json
import pandas as pd

# Ρύθμιση Σελίδας
st.set_page_config(page_title="Does4U - Internal Lead Hunter", page_icon="⚡", layout="wide")
st.title("⚡ Does4U Automated Lead Hunter v5.0")
st.subheader("Εσωτερικό Σύστημα Εντοπισμού & Μετάφρασης Αγγελιών (Xing)")

# Διάβασμα των κλειδιών από τα Secrets του Streamlit Cloud
try:
    FIRECRAWL_API_KEY = st.secrets["FIRECRAWL_API_KEY"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("🚨 Σφάλμα: Δεν βρέθηκαν τα κλειδιά στα Secrets του Streamlit Cloud!")
    st.stop()

st.info("🎯 **Προκαθορισμένος Στόχος:** Το Bot είναι ρυθμισμένο να κυνηγάει αγγελίες που αφορούν: *Web Scraping, AI Automations, Python Scripts, SaaS Engineering*.")

# Ένα και μοναδικό κουμπί για όλη τη δουλειά
if st.button("🚀 ΕΝΑΡΞΗ ΑΥΤΟΜΑΤΟΥ ΚΥΝΗΓΙΟΥ ΣΤΟ XING"):
    with st.spinner("Το Firecrawl σκανάρει το Xing για τις υπηρεσίες της Does4U..."):
        try:
            # Αρχικοποίηση εργαλείων
            firecrawl_app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
            openai_client = OpenAI(api_key=OPENAI_API_KEY)
            
            # 🔥 Προκαθορισμένο, πανίσχυρο Query που συνδυάζει όλες τις υπηρεσίες της Does4U
            # Αποκλείει ρητά tutorials, blogs κλπ.
            fixed_query = 'site:xing.com/jobs ("web scraping" OR "AI automation" OR "Python script" OR "SaaS engineering")'
            
            search_result = firecrawl_app.search(fixed_query, limit=8)
            
            # Διόρθωση σφάλματος: Έλεγχος αν το search_result έχει δεδομένα (είτε ως list είτε ως attribute)
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
                st.warning("Δεν βρέθηκαν φρέσκες αγγελίες αυτή τη στιγμή στο Xing. Δοκίμασε ξανά αργότερα.")
            else:
                leads_list = []
                
                for item in raw_results:
                    url = getattr(item, 'url', '')
                    content = getattr(item, 'markdown', '')[:4000] if getattr(item, 'markdown', '') else ''
                    
                    if not content:
                        continue
                        
                    # Αυστηρό Prompt Φιλτραρίσματος, Μετάφρασης και Εντοπισμού Email
                    prompt = f"""
                    Είσαι ο Lead Qualifier και Μεταφραστής της εταιρείας Does4U (SaaS Engineering & AI Automations).
                    Εξετάζεις μια σελίδα/αγγελία από το Xing.
                    
                    Αποστολή σου:
                    1. ΕΛΕΓΧΟΣ MATCH: Επιβεβαίωσε αν πρόκειται για ΠΡΑΓΜΑΤΙΚΗ ΚΑΙ ΕΝΕΡΓΗ αγγελία εργασίας ή project όπου ψάχνουν developer/freelancer για Web Scraping, AI Automations, Python ή SaaS. Αν είναι άρθρο, προφίλ, ή άσχετο κείμενο, βάλε "is_match": false.
                    2. ΜΕΤΑΦΡΑΣΗ: Αν είναι match, μετάφρασε τον Τίτλο της θέσης και μια σύντομη σύνοψη των απαιτήσεων ΑΥΣΤΗΡΑ ΣΤΑ ΕΛΛΗΝΙΚΑ.
                    3. EMAIL ΕΠΙΚΟΙΝΩΝΙΑΣ: Ψάξε εξαντλητικά για email επικοινωνίας στο κείμενο. Αν βρεις email σε μορφή "name [at] company.com", μετέτρεψέ το σε κανονική μορφή email. Αν δεν υπάρχει ΠΟΥΘΕΝΑ, γράψε "Δεν βρέθηκε".
                    4. COLD EMAIL: Γράψε ένα επαγγελματικό cold email εκ μέρους της Does4U. Αν η αγγελία είναι στα Γερμανικά, γράψε το email στα Γερμανικά (ή στα Αγγλικά αν προτιμάται επαγγελματικά), προσφέροντας τις υπηρεσίες μας για το συγκεκριμένο πρόβλημα.
                    
                    Επέστρεψε ΑΥΣΤΗΡΑ ΜΟΝΟ ένα έγκυρο JSON αντικείμενο με αυτή τη δομή:
                    {{
                        "is_match": true ή false,
                        "translated_title": "Ο τίτλος της θέσης μεταφρασμένος στα Ελληνικά",
                        "summary_greek": "Σύντομη περιγραφή του τι ζητάνε στα Ελληνικά (1-2 προτάσεις)",
                        "email": "το email που βρήκες ή Δεν βρέθηκε",
                        "generated_email": "Το έτοιμο cold email για τον πελάτη στα Γερμανικά/Αγγλικά"
                    }}
                    
                    Κείμενο αγγελίας:
                    {content}
                    """
                    
                    response = openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        response_format={"type": "json_object"},
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.1
                    )
                    
                    ai_data = json.loads(response.choices[0].message.content)
                    
                    # Αυστηρό Φιλτράρισμα: Αν δεν είναι πραγματική δουλειά, προσπερνιέται
                    if ai_data.get("is_match") is not True:
                        continue
                        
                    leads_list.append({
                        "Τίτλος Θέσης (Ελληνικά)": ai_data.get("translated_title"),
                        "Τι Ζητάνε (Σύνοψη)": ai_data.get("summary_greek"),
                        "Email Επικοινωνίας": ai_data.get("email"),
                        "Σύνδεσμος (URL)": url,
                        "Έτοιμο Email Does4U": ai_data.get("generated_email")
                    })
                
                # Εμφάνιση Αποτελεσμάτων στον Χρήστη
                if len(leads_list) == 0:
                    st.info("⚠️ Το AI σκάναρε το Xing αλλά δεν εντόπισε κάποια νέα αγγελία που να ταιριάζει απόλυτα στα κριτήρια της Does4U. Ο πίνακας παρέμεινε καθαρός.")
                else:
                    df = pd.DataFrame(leads_list)
                    st.success(f"🎯 Βρέθηκαν {len(df)} πραγματικά, φρέσκα matches στα Ελληνικά!")
                    
                    # 1. Προβολή του Πίνακα
                    st.dataframe(df[["Τίτλος Θέσης (Ελληνικά)", "Τι Ζητάνε (Σύνοψη)", "Email Επικοινωνίας", "Σύνδεσμος (URL)"]], use_container_width=True)
                    
                    # 2. Προβολή των έτοιμων Emails από κάτω
                    st.markdown("### 📝 Έτοιμα Emails της Does4U προς Αντιγραφή:")
                    for idx, row in df.iterrows():
                        with st.expander(f"✉️ Pitch για: {row['Τίτλος Θέσης (Ελληνικά)']} ({row['Email Επικοινωνίας']})"):
                            st.text_area("Κείμενο Email (Έτοιμο προς αποστολή):", row['Έτοιμο Email Does4U'], height=250, key=f"txt_{idx}")
                            st.caption(f"Πηγή στο Xing: {row['Σύνδεσμος (URL)']}")
                            
        except Exception as e:
            st.error(f"Παρουσιάστηκε σφάλμα κατά την εκτέλεση: {e}")