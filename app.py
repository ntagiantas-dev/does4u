#--- 1. Εισαγωγες (import & config) ---
import streamlit as st
import PyPDF2
import os
from dotenv import load_dotenv
from openai import OpenAI
from tavily import TavilyClient
from converter import show_converter_ui
from dash import load_codes

valid_codes = load_codes()

# --- ΡΥΘΜΙΣΕΙΣ ΕΜΦΑΝΙΣΗΣ ---
st.set_page_config(page_title="Does4U | Premium Legal AI", page_icon="⚖️", layout="wide")

# --- CSS (ΤΟ "ΜΑΚΙΓΙΑΖ" ΤΗΣ ΣΕΛΙΔΑΣ) ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #f8f9fb; color: #002b5c; }
    div.stButton > button { background-color: #004a99 !important; color: white !important; font-weight: bold; width: 100%; }
    .main-header { font-family: 'Georgia', serif; color: #002b5c; text-align: center; padding: 10px; }
    .report-container { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

#--- 2. Tο μυαλό (System Prompt)---
SYSTEM_PROMPT = """
Είσαι η Does4U, η πιο εξελιγμένη Τεχνητή Νοημοσύνη Νομικής και Φορολογικής Ανάλυσης στην Ελλάδα.
Ο ρόλος σου είναι να αναλύεις ερωτήματα χρηστών με βάση:
1. Το κείμενο από τα PDF που σου παρέχονται.
2. Την ισχύουσα ελληνική νομοθεσία (Live Search).

Δομή Απάντησης:
⚖️ ΝΟΜΙΚΟ ΠΛΑΙΣΙΟ: Αναφορά σε συγκεκριμένα άρθρα.
🔍 ΑΝΑΛΥΣΗ: Επεξήγηση με απλά λόγια.
🛠️ ΠΡΟΤΑΣΗ: Συγκεκριμένες κινήσεις για τον χρήστη.
"""

#--- 3. Τα Κλειδιά (ΑΠΙ Keys & Session)---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) 
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Αρχικοποίηση "Μνήμης"
if "unlock_converter" not in st.session_state:
    st.session_state.unlock_converter = False
if "unlock_analysis" not in st.session_state:
    st.session_state.unlock_analysis = False

#--- 4. SideBar & Promo Codes (ΔΙΟΡΘΩΜΕΝΟ)---
with st.sidebar:
    # a. Λογότυπο
    try:
        st.image("does4u_logo.png", use_container_width=True)
    except:
        st.warning("⚠️ Το αρχείο does4u_logo.png δεν βρέθηκε.")
    
    st.write("---")
    
    # b. Σύστημα Promo Codes
    st.subheader("🎟️ Promo Code")
    promo_input = st.text_input("Εισάγετε κωδικό...", placeholder="π.χ. legal24", key="promo_code")
    
    if st.button("ΕΝΕΡΓΟΠΟΙΗΣΗ"):
        if promo_input.upper().strip() in valid_codes:
            st.success("Ο κωδικός ενεργοποιήθηκε!")
            st.session_state.unlock_analysis = True  
            st.session_state.unlock_converter = True 
            st.rerun()
        else:
            st.error("Άκυρος κωδικός. Προσπαθήστε ξανά.")
    
    st.write("---")
    
    # c. Επιλογή Πακέτου (AI Model)
    st.subheader("📦 Επιλογή Επιπέδου Νοημοσύνης")
    package = st.radio("Διαθέσιμα Tiers:", ["1. Έμπειρος Αναλυτής", "2. Στρατηγικός Εταίρος", "3. OS-1 Neural"])
    
    model_map = {
        "1. Έμπειρος Αναλυτής": "gpt-4o-mini",
        "2. Στρατηγικός Εταίρος": "gpt-4o",
        "3. OS-1 Neural": "gpt-4-turbo"
    }
    selected_model = model_map[package]

#--- 5. Η βιτρίνα και το ανέβασμα των αρχείων (Main UI & Uploaders)---
st.markdown('<div class="main-header"><h1>ΕΞΕΙΔΙΚΕΥΜΕΝΗ ΠΟΛΥΜΟΡΦΙΚΗ ΑΝΑΛΥΣΗ</h1></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("⚖️ Analysis Box")
    uploaded_file = st.file_uploader("Ανέβασμα PDF για Νομικό Έλεγχο", type="pdf", key="analysis_up")

with col2:
    st.subheader("🔄 Convert Box")
    uploaded_conv = st.file_uploader("Ανέβασμα για Μετατροπή (PDF, JPG, κλπ)", type=["pdf", "txt", "docx","png", "jpg"], key="conv_up")

if uploaded_conv:
    if st.session_state.get('unlock_converter', False):
        st.success("✅ Υπηρεσία Μετατροπής Ενεργή")
        show_converter_ui() 
    else:
        st.warning("🔒 Η μετατροπή είναι Premium υπηρεσία. Βάλτε το Promo Code στο Sidebar.")

#--- 6 Η μηχανή Ανάλυσης (Core Logic)---
user_query = st.text_input("💬 Θέστε το ερώτημά σας (π.χ. Έλεγχος συμμόρφωσης με ΦΕΚ):")

pdf_text = ""
if uploaded_file:
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    pdf_text = "".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    st.toast("✅ Το αρχείο φορτώθηκε!")

if st.button("🚀 ΕΝΑΡΞΗ ΑΝΑΛΥΣΗΣ"):
    if not st.session_state.get('unlock_analysis', False):
        st.error("🔒 Η Premium Ανάλυση είναι κλειδωμένη. Εισάγετε Promo Code στο Sidebar.")
    
    elif uploaded_file and user_query:
        with st.status("⚖️ Η Does4U επεξεργάζεται το αίτημα...") as status:
            
            st.write("🔍 Αναζήτηση πρόσφατης νομοθεσίας (Tavily)...")
            try:
                search_results = tavily.search(query=user_query, search_depth="advanced", max_results=3)
                context_web = ""
                for res in search_results['results']:
                    context_web += f"\nΠΗΓΗ: {res['url']}\nΠΕΡΙΕΧΟΜΕΝΟ: {res['content']}\n"
            except:
                context_web = "Δεν βρέθηκαν live δεδομένα."
                
            st.write("🧠 Ανάλυση δεδομένων και σύνταξη πορίσματος...")
            try:
                enriched_prompt = f"""
                ΚΕΙΜΕΝΟ PDF ΠΕΛΑΤΗ:
                {pdf_text[:8000]} 

                ΠΡΟΣΦΑΤΕΣ ΝΟΜΙΚΕΣ ΕΞΕΛΙΞΕΙΣ:
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
                st.subheader("📝 ΠΟΡΙΣΜΑ ΑΝΑΛΥΣΗΣ")
                st.markdown(final_answer)
                st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Σφάλμα επικοινωνίας: {e}")
                
    elif not uploaded_file:
        st.warning("⚠️ Ανέβασε ένα PDF για να ξεκινήσουμε.")
    elif not user_query:
        st.warning("⚠️ Πρέπει να γράψεις τι θέλεις να κάνει η Does4U.")

# --- 7. FOOTER (ΤΟ ΚΑΤΩ ΜΕΡΟΣ) ---
st.write("---")
st.caption("Does4U AI Legal Assistant v2.0 | Secured Connection")