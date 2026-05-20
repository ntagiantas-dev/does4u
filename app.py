import streamlit as st
import pandas as pd
import gspread

# 1. Ρύθμιση σελίδας
st.set_page_config(page_title="Does4u Manual", layout="wide")

# 2. Σύνδεση με Google Sheets (Χρησιμοποιώντας τα Secrets)
# Στο Streamlit Cloud -> Manage App -> Secrets, πρέπει να έχεις το JSON του service account σου!
@st.cache_resource
def get_gspread_client():
    creds_dict = st.secrets["gcp_service_account"]
    return gspread.service_account_from_dict(creds_dict)

gc = get_gspread_client()
SHEET_URL = "https://docs.google.com/spreadsheets/d/1s1tNfms8eF_Vuo36DDNoEXKDO4qOhiMdcpTSVdYwloM/edit"

# 3. Λειτουργία ανάγνωσης δεδομένων
def load_data():
    sh = gc.open_by_url(SHEET_URL)
    worksheet = sh.sheet1
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

st.title("🚚 Does4u - Manual Entry Portal")

# 4. Φόρμα εισαγωγής (Manual)
with st.form("entry_form", clear_on_submit=True):
    address = st.text_input("Γράψε τη διεύθυνση:")
    city = st.text_input("Πόλη:", value="N/A")
    status = st.selectbox("Κατάσταση:", ["Pending", "Completed", "Cancelled"])
    
    submit = st.form_submit_button("Προσθήκη Στάσης")
    
    if submit and address:
        sh = gc.open_by_url(SHEET_URL)
        worksheet = sh.sheet1
        # Προσθήκη νέας γραμμής
        worksheet.append_row([address, city, 'N/A', status, 'Manual'])
        st.success(f"Η στάση '{address}' προστέθηκε!")

# 5. Εμφάνιση δεδομένων
st.subheader("Τρέχουσες Στάσεις")
if st.button("🔄 Ανανέωση Λίστας"):
    st.session_state.df = load_data()
    st.rerun()

if 'df' in st.session_state:
    st.dataframe(st.session_state.df)
else:
    st.info("Πατήστε ανανέωση για να δείτε τα δεδομένα.")