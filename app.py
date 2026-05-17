#========================================================
#=== ΕΝΟΤΗΤΑ 1: Εισαγωγή Εργαλείων & Ρυθμίσεις Εμφάνισης 
#========================================================
import streamlit as st
import requests
import json
import os
import time
import PyPDF2
from dotenv import load_dotenv
from openai import OpenAI
from tavily import TavilyClient
from converter import show_converter_ui
from dash import load_codes

# 1. Φόρτωση των έγκυρων Premium κωδικών
valid_codes = load_codes()

# 2. Ρυθμίσεις για το πώς θα φαίνεται η σελίδα στον Browser
st.set_page_config(
    page_title="Does4U | Premium Legal AI", 
    page_icon="⚖️", 
    layout="wide"
)

# 3. Το "μακιγιάζ" (CSS) της σελίδας (Χρώματα, Κουμπιά, Sidebar)
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #f8f9fb; color: #002b5c; }
    div.stButton > button { background-color: #004a99 !important; color: white !important; font-weight: bold; width: 100%; }
    .main-header { font-family: 'Georgia', serif; color: #002b5c; text-align: center; padding: 10px; }
    .report-container { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)
#==========================================================
#= ΕΝΟΤΗΤΑ 2: Ο "Εγκέφαλος" του AI & Τα Κλειδιά Ασφαλείας
#==========================================================
# 1. Οι οδηγίες προς το AI για το πώς θα απαντάει στον πελάτη
SYSTEM_PROMPT = """
Είσαι η Does4U, η πιο εξελιγμένη Τεχνητή Νοημοσύνη Νομικής, Φορολογικής και Στρατηγικής Ανάλυσης στην Ελλάδα.
Ο ρόλος σου είναι να αναλύεις ερωτήματα χρηστών με βάση:
1. Το κείμενο από τα PDF που σου παρέχονται (αν υπάρχουν).
2. Την ισχύουσα ελληνική νομοθεσία και επικαιρότητα μέσω live έρευνας στο διαδίκτυο (Live Search).

Δομή Απάντησης:
⚖️ ΝΟΜΙΚΟ & ΣΤΡΑΤΗΓΙΚΟ ΠΛΑΙΣΙΟ: Αναφορά σε συγκεκριμένα άρθρα, νόμους ή πηγές.
🔍 ΑΝΑΛΥΣΗ: Επεξήγηση των δεδομένων με απλά, κατανοητά και επιχειρηματικά λόγια.
🛠️ ΠΡΟΤΑΣΗ: Συγκεκριμένες, πρακτικές κινήσεις και επόμενα βήματα για τον χρήστη.
"""

# 2. Ενεργοποίηση των API Keys
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) 
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# 3. Αρχική κατάσταση: Όλα κλειδωμένα μέχρι να μπει σωστός κωδικός
if "unlock_converter" not in st.session_state:
    st.session_state.unlock_converter = False
if "unlock_analysis" not in st.session_state:
    st.session_state.unlock_analysis = False
#=========================================================
#= ΕΝΟΤΗΤΑ 3: Το Πλευρικό Μενού (Sidebar) & Έλεγχος Κωδικών
#==========================================================
with st.sidebar:
    # α. Εμφάνιση του Λογοτύπου
    try:
        st.image("does4u_logo.png", use_container_width=True)
    except:
        st.warning("⚠️ Το αρχείο does4u_logo.png δεν βρέθηκε.")
    
    st.write("---")
    
    # β. Κουτί εισαγωγής Promo Code
    st.subheader("🎟️ Premium Πρόσβαση")
    promo_input = st.text_input("Εισάγετε κωδικό...", placeholder="π.χ. PREMIUM26", key="promo_code")
    
    if st.button("ΕΝΕΡΓΟΠΟΙΗΣΗ"):
        code_upper = promo_input.upper().strip()
        
        if code_upper in valid_codes:
            code_type = valid_codes[code_upper].get("type", "converter")
            
            # Αν ο κωδικός είναι για Ανάλυση, ξεκλειδώνει τα ΠΑΝΤΑ
            if code_type == "analysis":
                st.session_state.unlock_analysis = True
                st.session_state.unlock_converter = True  
                st.success("🚀 Premium Κωδικός Ανάλυσης Ενεργός!")
            # Αν είναι απλός κωδικός, ξεκλειδώνει μόνο τον Μετατροπέα
            else:
                st.session_state.unlock_converter = True
                st.session_state.unlock_analysis = False  
                st.success("🔄 Κωδικός Μετατροπών (Convert) Ενεργός!")
                
            time.sleep(1)
            st.rerun()
        else:
            st.error("❌ Άκυρος ή ληγμένος κωδικός. Προσπαθήστε ξανά.")
    
    st.write("---")
    
    # γ. Επιλογή Μοντέλου OpenAI (Tiers)
    st.subheader("📦 Επιλογή Επιπέδου Νοημοσύνης")
    package = st.radio("Διαθέσιμα Tiers:", ["1. Έμπειρος Αναλυτής", "2. Στρατηγικός Εταίρος", "3. OS-1 Neural"])
    
    model_map = {
        "1. Έμπειρος Αναλυτής": "gpt-4o-mini",
        "2. Στρατηγικός Εταίρος": "gpt-4o",
        "3. OS-1 Neural": "gpt-4-turbo"
    }
    selected_model = model_map[package]
#===============================================================
#== ΕΝΟΤΗΤΑ 4: Η Κύρια Οθόνη & Τα Δύο Κουτιά Ανεβάσματος (Boxes)
#===============================================================
# 1. Κεντρικός Τίτλος
st.markdown('<div class="main-header"><h1>ΕΞΕΙΔΙΚΕΥΜΕΝΗ ΠΟΛΥΜΟΡΦΙΚΗ ΑΝΑΛΥΣΗ</h1></div>', unsafe_allow_html=True)

# 2. Δημιουργία δύο ισόποσων στηλών στην οθόνη
col1, col2 = st.columns(2)

with col1:
    st.subheader("⚖️ Analysis Box")
    uploaded_file = st.file_uploader("Ανέβασμα PDF για Νομικό/Στρατηγικό Έλεγχο", type="pdf", key="analysis_up")

with col2:
    st.subheader("🔄 Convert Box")
    uploaded_conv = st.file_uploader("Ανέβασμα για Μετατροπή (PDF, TXT, DOCX)", type=["pdf", "txt", "docx"], key="conv_up")

# 3. Αυτόματη ενεργοποίηση του Μετατροπέα (Converter) αν ανέβει αρχείο
if st.session_state.get('conv_up') is not None:
    if st.session_state.get('unlock_converter', False):
        show_converter_ui() # Καλεί τον κώδικα από το converter.py
    else:
        st.warning("🔒 Η μετατροπή εγγράφων είναι Premium υπηρεσία. Εισάγετε κωδικό πρόσβασης στο Sidebar.")

st.write("---")
#============================================================
#== ΕΝΟΤΗΤΑ 5: Η Μηχανή Έρευνας & Το Κουμπί "Έναρξη Ανάλυσης"
#============================================================
st.markdown("### 💬 Premium Μηχανή Έρευνας & Ανάλυσης")
user_query = st.text_input("Θέστε το ερώτημά σας προς έρευνα (π.χ. Αλλαγές στο ΦΕΚ τουρισμού):", key="analysis_query")

# Έξυπνο διάβασμα του PDF της Ανάλυσης (γίνεται μόνο μια φορά για να μην κολλάει)
if uploaded_file:
    if "analysis_pdf_text" not in st.session_state or st.session_state.get("last_analysis_file") != uploaded_file.name:
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            st.session_state["analysis_pdf_text"] = "".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
            st.session_state["last_analysis_file"] = uploaded_file.name
            st.toast("✅ Το αρχείο PDF ενσωματώθηκε στην ανάλυση!")
        except:
            st.session_state["analysis_pdf_text"] = ""
else:
    st.session_state["analysis_pdf_text"] = ""

st.write("") 

# ΤΟ ΜΕΓΑΛΟ ΚΟΥΜΠΙ ΤΗΣ ΕΦΑΡΜΟΓΗΣ
if st.button("🚀 ΕΝΑΡΞΗ PREMIUM ΑΝΑΛΥΣΗΣ", use_container_width=True):
    
    # Έλεγχος 1: Έχει βάλει Premium κωδικό;
    if not st.session_state.get('unlock_analysis', False):
        st.error("🔒 Η Premium Ανάλυση & Live Έρευνα είναι κλειδωμένη. Απαιτείται Premium Promo Code.")
    
    # Έλεγχος 2: Έγραψε ερώτηση στο κουτί;
    elif not user_query:
        st.warning("⚠️ Παρακαλώ πληκτρολογήστε το ερώτημα ή το θέμα που σας ενδιαφέρει.")
        
    # Αν όλα είναι ΟΚ, ξεκινάει η διεργασία
    else:
        with st.status("⚖️ Η Does4U επεξεργάζεται και ερευνά το αίτημα...") as status:
            
            # Βήμα Α: Ζωντανή έρευνα στο Ίντερνετ
            st.write("🔍 Ζωντανή αναζήτηση δεδομένων στο διαδίκτυο (Tavily)...")
            urls_found = []
            try:
                search_results = tavily.search(query=user_query, search_depth="advanced", max_results=3)
                context_web = ""
                for res in search_results['results']:
                    context_web += f"\nΠΗΓΗ: {res['url']}\nΠΕΡΙΕΧΟΜΕΝΟ: {res['content']}\n"
                    urls_found.append(res['url'])
            except:
                context_web = "Δεν βρέθηκαν live δεδομένα κατά την αναζήτηση."
                
            # Βήμα Β: Αποστολή στο OpenAI για τη σύνταξη του νομικού εγγράφου
            st.write("🧠 Διασταύρωση πηγών, ανάλυση και σύνταξη στρατηγικού πορίσματος...")
            try:
                pdf_text = st.session_state.get("analysis_pdf_text", "")
                document_context = pdf_text[:8000] if pdf_text else "Δεν έχει ανεβαστεί αρχείο PDF από τον χρήστη."
                
                enriched_prompt = f"ΚΕΙΜΕΝΟ PDF:\n{document_context}\n\nINTERNET:\n{context_web}\n\nΕΡΩΤΗΣΗ:\n{user_query}"
                
                response = client.chat.completions.create(
                    model=selected_model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": enriched_prompt}
                    ]
                )
                
                final_answer = response.choices[0].message.content
                status.update(label="✅ Η ανάλυση ολοκληρώθηκε!", state="complete", expanded=False)

                # Βήμα Γ: Εμφάνιση του τελικού αποτελέσματος στον πελάτη
                st.markdown('<div class="report-container">', unsafe_allow_html=True)
                st.subheader("📝 ΠΟΡΙΣΜΑ ΣΤΡΑΤΗΓΙΚΗΣ ΑΝΑΛΥΣΗΣ")
                st.markdown(final_answer)
                
                # Εμφάνιση των Links/Πηγών από το Google
                if urls_found:
                    st.write("---")
                    st.markdown("### 🔗 Πηγές που εντοπίστηκαν:")
                    for idx_url, url in enumerate(urls_found):
                        st.markdown(f"**[{idx_url + 1}]** 🌐 [{url}]({url})")
                        
                st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Σφάλμα κατά τη σύνταξη της απάντησης: {e}")

# --- FOOTER ---
st.write("---")
st.caption("© 2026 Does4U. All rights reserved.")
#=========================================================
#============= DOES4U APP =============================
#======================================================

