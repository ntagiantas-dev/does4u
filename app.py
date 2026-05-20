import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Does4u Pro", layout="wide")

# --- ΣΤΑΘΕΡΕΣ & CONFIG ---
GEOAPIFY_KEY = st.secrets["GEOAPIFY_API_KEY"]

# --- FUNCTIONS ---
def validate_and_process(df):
    required = ['address', 'city', 'postal code']
    if not all(col in df.columns for col in required):
        return False, "Λείπουν στήλες (address, city, postal code)"
    
    if 'status' not in df.columns:
        df['status'] = 'Pending'
    if 'type' not in df.columns:
        df['type'] = 'Παράδοση'
    return True, df

# --- UI LOGIC ---
st.title("🚚 Does4u - Professional Driver Portal")

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()

uploaded_file = st.file_uploader("Ανέβασε τη λίστα σου (CSV)", type="csv")

if uploaded_file and st.session_state.df.empty: 
    raw_df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
    raw_df['status'] = 'Pending' 
    success, result = validate_and_process(raw_df)
    if not success:
        st.error(result)
    else:
        st.session_state.df = result
        st.success("Λίστα φορτώθηκε με επιτυχία!")

# --- DRIVER WORKFLOW ---
if not st.session_state.df.empty:
    
    # 0. Βελτιστοποίηση Διαδρομής
    if st.button("🔀 Βελτιστοποίηση Διαδρομής"):
        with st.spinner('Υπολογισμός βέλτιστης διαδρομής...'):
            pending = st.session_state.df[st.session_state.df['status'] == 'Pending'].copy()
            done = st.session_state.df[st.session_state.df['status'] != 'Pending']
            # Εδώ γίνεται η αναδιάταξη (για την ώρα τοποθετεί τα Pending σε αντίστροφη σειρά ως placeholder)
            st.session_state.df = pd.concat([pending.iloc[::-1], done])
            st.rerun()

    pending = st.session_state.df[st.session_state.df['status'] == 'Pending']
    
    if not pending.empty:
        current_idx = pending.index[0]
        current = st.session_state.df.loc[current_idx]
        
        # 1. Επιλογή Τύπου Στάσης
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
            
        # 3. Google Maps Navigation
        maps_link = f"https://www.google.com/maps/dir/?api=1&destination={current['address']},{current['city']}"
        st.link_button("🚀 Έναρξη Πλοήγησης στο Maps", maps_link)
        
    else:
        st.success("🎉 Όλες οι στάσεις ολοκληρώθηκαν!")

    # Sidebar
    with st.sidebar:
        st.write("### Πρόοδος")
        st.dataframe(st.session_state.df[['address', 'status', 'type']])