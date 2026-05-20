import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Does4u Pro", layout="wide")

# --- ΣΤΑΘΕΡΕΣ & CONFIG ---
GEOAPIFY_KEY = st.secrets["GEOAPIFY_API_KEY"]

# --- FUNCTIONS ---
def validate_and_process(df):
    """Έλεγχος δεδομένων και προετοιμασία"""
    required = ['address', 'city', 'postal code']
    if not all(col in df.columns for col in required):
        return False, "Λείπουν στήλες (address, city, postal code)"
    
    # Αρχικοποίηση status αν δεν υπάρχουν
    if 'status' not in df.columns:
        df['status'] = 'Pending'
    if 'type' not in df.columns:
        df['type'] = 'Παράδοση' # Default type
    return True, df

# --- UI LOGIC ---
st.title("🚚 Does4u - Professional Driver Portal")

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()

uploaded_file = st.file_uploader("Ανέβασε τη λίστα σου (CSV)", type="csv")

if uploaded_file:
    raw_df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
    success, result = validate_and_process(raw_df)
    
    if not success:
        st.error(result)
    else:
        st.session_state.df = result
        st.success("Λίστα φορτώθηκε με επιτυχία!")

# --- DRIVER WORKFLOW (Η καρδιά του συστήματος) ---
if not st.session_state.df.empty:
    pending = st.session_state.df[st.session_state.df['status'] == 'Pending']
    
    if not pending.empty:
        current_idx = pending.index[0]
        current = st.session_state.df.loc[current_idx]
        
        # 1. Επιλογή Τύπου Στάσης (Παράδοση/Παραλαβή)
        st.subheader(f"📍 Στάση: {current['address']}")
        st.session_state.df.at[current_idx, 'type'] = st.radio(
            "Τύπος Στάσης:", ['Παράδοση', 'Παραλαβή'], 
            index=0 if current['type'] == 'Παράδοση' else 1
        )
        
        # 2. Controls
        c1, c2 = st.columns(2)
        if c1.button("✅ Ολοκλήρωση"):
            st.session_state.df.loc[current_idx, 'status'] = 'Done'
            st.rerun()
        if c2.button("⏭️ Skip"):
            st.session_state.df.loc[current_idx, 'status'] = 'Skipped'
            st.rerun()
            
        # 3. Google Maps Navigation (Deep Link)
        maps_link = f"https://www.google.com/maps/dir/?api=1&destination={current['address']},{current['city']}"
        st.link_button("🚀 Έναρξη Πλοήγησης στο Maps", maps_link)
        
    else:
        st.success("🎉 Όλες οι στάσεις ολοκληρώθηκαν!")

    # Sidebar: Πίνακας Ελέγχου
    with st.sidebar:
        st.write("### Πρόοδος")
        st.dataframe(st.session_state.df[['address', 'status', 'type']])