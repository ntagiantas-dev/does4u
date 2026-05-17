# ==============================================================================
# ΕΝΟΤΗΤΑ 1: ΕΙΣΑΓΩΓΕΣ ΒΙΒΛΙΟΘΗΚΩΝ & ΜΟΝΤΟΥΛΩΝ
# ==============================================================================
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

# ==============================================================================
# ΕΝΟΤΗΤΑ 2: ΑΡΧΙΚΟΠΟΙΗΣΗ & ΡΥΘΜΙΣΕΙΣ ΕΦΑΡΜΟΓΗΣ (CONFIG & CSS)
# ==============================================================================
# Φόρτωση έγκυρων κωδικών από το promo_codes.json
valid_codes = load_codes()

# Ρυθμίσεις εμφάνισης παραθύρου
st.set_page_config(
    page_title="Does4U | Premium Legal AI", 
    page_icon="⚖️", 
    layout="wide"
)

# Εφαρμογή custom CSS για το design της πλατφόρμας
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #f8f9fb; color: #002b5c; }
    div.stButton > button { background-color: #004a99 !important; color: white !important; font-weight: bold; width: 100%; }
    .main-header { font-family: 'Georgia', serif; color: #002b5c; text-align: center; padding: 10px; }
    .report-container { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# ΕΝΟΤΗΤΑ 3: SYSTEM PROMPT & ΡΥΘΜΙΣΕΙΣ API KEYS / SESSION STATE
# ==============================================================================
# Το μυαλό της Does4U (Οδηγίες συμπεριφοράς του LLM)
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

# Φόρτωση περιβάλλοντος και αρχικοποίηση AI Clients
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) 
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Αρχικοποίηση μεταβλητών κατάστασης (Session State)
if "unlock_converter" not in st.session_state:
    st.session_state.unlock_converter = False
if "unlock_analysis" not in st.session_state:
    st.session_state.unlock_analysis = False
if "start_conversion" not in st.session_state:
    st.session_state.start_conversion = False

# ==============================================================================
# ΕΝΟΤΗΤΑ 4: ΠΛΕΥΡΙΚΗ ΜΠΑΡΑ (SIDEBAR - PROMO CODES & TIERS)
# ==============================================================================
with st.sidebar:
    # Εμφάνιση Λογοτύπου
    try:
        st.image("does4u_logo.png", use_container_width=True)
    except:
        st.warning("⚠️ Το αρχείο does4u_logo.png δεν βρέθηκε.")
    
    st.write("---")
    
    # Διαχείριση Κωδικών Πρόσβασης
    st.subheader("🎟️ Premium Πρόσβαση")
    promo_input = st.text_input("Εισάγετε κωδικό...", placeholder="π.χ. PREMIUM26", key="promo_code")
    
    if st.button("ΕΝΕΡΓΟΠΟΙΗΣΗ"):
        code_upper = promo_input.upper().strip()
        
        if code_upper in valid_codes:
            code_type = valid_codes[code_upper].get("type", "converter")
            
            if code_type == "analysis":
                st.session_state.unlock_analysis = True
                st.session_state.unlock_converter = True
                st.success("🚀 Premium Κωδικός Ανάλυσης Ενεργός!")
            else:
                st.session_state.unlock_converter = True
                st.session_state.unlock_analysis = False
                st.success("🔄 Κωδικός Μετατροπών (Convert) Ενεργός!")
                
            time.sleep(1)
            st.rerun()
        else:
            st.error("❌ Άκυρος ή ληγμένος κωδικός. Προσπαθήστε ξανά.")
    
    st.write("---")
    
    # Επιλογή Μοντέλου Νοημοσύνης (LLM Mapping)
    st.subheader("📦 Επιλογή Επιπέδου Νοημοσύνης")
    package = st.radio("Διαθέσιμα Tiers:", ["1. Έμπειρος Αναλυτής", "2. Στρατηγικός Εταίρος", "3. OS-1 Neural"])
    
    model_map = {
        "1. Έμπειρος Αναλυτής": "gpt-4o-mini",
        "2. Στρατηγικός Εταίρος": "gpt-4o",
        "3. OS-1 Neural": "gpt-4-turbo"
    }
    selected_model = model_map[package]

# ==============================================================================
# ΕΝΟΤΗΤΑ 5: ΚΥΡΙΟ UI - ΚΟΥΤΙΑ ΑΝΕΒΑΣΜΑΤΟΣ (ANALYSIS & CONVERT BOX)
# ==============================================================================
# Κεντρικός Τίτλος
st.markdown('<div class="main-header"><h1>ΕΞΕΙΔΙΚΕΥΜΕΝΗ ΠΟΛΥΜΟΡΦΙΚΗ ΑΝΑΛΥΣΗ</h1></div>', unsafe_allow_html=True)

# Δημιουργία δύο στηλών για το ανέβασμα αρχείων
col1, col2 = st.columns(2)

with col1:
    st.subheader("⚖️ Analysis Box")
    uploaded_file = st.file_uploader("Ανέβασμα PDF για Νομικό/Στρατηγικό Έλεγχο", type="pdf", key="analysis_up")

with col2:
    st.subheader("🔄 Convert Box")
    uploaded_conv = st.file_uploader("Ανέβασμα για Μετατροπή (PDF, TXT, DOCX)", type=["pdf", "txt", "docx"], key="conv_up")

# Έλεγχος και ενημέρωση κατάστασης του Convert Box
if uploaded_conv:
    if st.session_state.get('unlock_converter', False):
        st.success("✅ Το αρχείο είναι έτοιμο στο Convert Box. Πιέστε 'ΕΝΑΡΞΗ ΜΕΤΑΤΡΟΠΗΣ' παρακάτω.")
    else:
        st.warning("🔒 Η μετατροπή εγγράφων είναι Premium υπηρεσία. Εισάγετε κωδικό πρόσβασης στο Sidebar.")

st.write("---")


# ==============================================================================
# ΕΝΟΤΗΤΑ 6: ΚΟΥΜΠΙΑ ΔΡΑΣΗΣ & ΕΚΤΕΛΕΣΗ ΜΗΧΑΝΩΝ (PROCESSORS)
# ==============================================================================
col_btn1, col_btn2 = st.columns(2)

# --- ΥΠΟ-ΕΝΟΤΗΤΑ 7.1: ΜΗΧΑΝΗ ΕΝΑΡΞΗΣ ΑΝΑΛΥΣΗΣ ---
with col_btn1:
    if st.button("🚀 ΕΝΑΡΞΗ ΑΝΑΛΥΣΗΣ", use_container_width=True):
        if not st.session_state.get('unlock_analysis', False):
            st.error("🔒 Η Premium Ανάλυση & Live Έρευνα είναι κλειδωμένη. Απαιτείται Premium Promo Code.")
        elif not user_query:
            st.warning("⚠️ Παρακαλώ πληκτρολογήστε το ερώτημα ή το θέμα που σας ενδιαφέρει.")
        else:
            with st.status("⚖️ Η Does4U επεξεργάζεται και ερευνά το αίτημα...") as status:
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
                    
                st.write("🧠 Διασταύρωση πηγών, ανάλυση και σύνταξη στρατηγικού πορίσματος...")
                try:
                    document_context = pdf_text[:8000] if pdf_text else "Δεν έχει ανεβαστεί αρχείο PDF από τον χρήστη."
                    
                    enriched_prompt = f"""
                    ΚΕΙΜΕΝΟ PDF ΠΕΛΑΤΗ:
                    {document_context} 

                    ΠΡΟΣΦΑΤΕΣ ΕΞΕΛΙΞΕΙΣ ΑΠΟ ΤΟ ΔΙΑΔΙΚΤΥΟ (TAVILY):
                    {context_web}

                    ΕΡΩΤΗΣΗ ΠΕΛΑΤΗ:
                    {user_query}
                    """
                    
                    response = client.chat.completions.create(
                        model=selected_model,
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": enriched_prompt}
                        ]
                    )
                    
                    final_answer = response.choices[0].message.content
                    status.update(label="✅ Η ανάλυση ολοκληρώθηκε!", state="complete", expanded=False)

                    st.markdown('<div class="report-container">', unsafe_allow_html=True)
                    st.subheader("📝 ΠΟΡΙΣΜΑ ΣΤΡΑΤΗΓΙΚΗΣ ΑΝΑΛΥΣΗΣ")
                    st.markdown(final_answer)
                    
                    if urls_found:
                        st.write("---")
                        st.markdown("### 🔗 Πηγές που εντοπίστηκαν:")
                        for idx_url, url in enumerate(urls_found):
                            st.markdown(f"**[{idx_url + 1}]** 🌐 [{url}]({url})")
                            
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"❌ Σφάλμα κατά τη σύνταξη της απάντησης: {e}")

# --- ΥΠΟ-ΕΝΟΤΗΤΑ 7.2: ΜΗΧΑΝΗ ΕΝΑΡΞΗΣ ΜΕΤΑΤΡΟΠΗΣ ---
with col_btn2:
    if st.button("🔄 ΕΝΑΡΞΗ ΜΕΤΑΤΡΟΠΗΣ", use_container_width=True):
        if not st.session_state.get('unlock_converter', False):
            st.error("🔒 Η μετατροπή εγγράφων είναι κλειδωμένη. Εισάγετε κωδικό πρόσβασης στο Sidebar.")
        elif not uploaded_conv:
            st.warning("⚠️ Παρακαλώ ανεβάστε πρώτα ένα αρχείο στο Convert Box παραπάνω.")
        else:
            st.session_state.start_conversion = True

# Εμφανίζουμε το UI του μετατροπέα ΜΟΝΟ αν ο χρήστης έχει πατήσει το κουμπί και είναι όλα έτοιμα
if st.session_state.get('start_conversion', False):
    show_converter_ui(key_id="main_app_converter")