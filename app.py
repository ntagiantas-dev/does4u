import streamlit as st
import pandas as pd

st.set_page_config(page_title="Does4u Pro", layout="wide")

# --- FUNCTIONS ---
def validate_and_process(df):
    required = ['address', 'city', 'postal code']
    if not all(col in df.columns for col in required):
        return False, "Λείπουν στήλες (address, city, postal code)"
    if 'status' not in df.columns: df['status'] = 'Pending'
    if 'type' not in df.columns: df['type'] = 'Παράδοση'
    return True, df

# --- UI LOGIC ---
st.title("🚚 Does4u - Professional Driver Portal")

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()

# Upload File
uploaded_file = st.file_uploader("Ανέβασε τη λίστα σου (CSV)", type="csv")
if uploaded_file and st.session_state.df.empty: 
    raw_df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
    success, result = validate_and_process(raw_df)
    if success:
        st.session_state.df = result
        st.success("Λίστα φορτώθηκε!")

# --- ΠΡΟΣΘΗΚΗ ΕΚΤΑΚΤΗΣ ΣΤΑΣΗΣ ---
with st.expander("➕ Προσθήκη Έκτακτης Στάσης"):
    col_a, col_b, col_c = st.columns(3)
    new_addr = col_a.text_input("Διεύθυνση")
    new_city = col_b.text_input("Πόλη")
    new_zip = col_c.text_input("ΤΚ")
    new_type = st.radio("Τύπος:", ['Παράδοση', 'Παραλαβή'], index=1)
    
    if st.button("Προσθήκη στη Λίστα"):
        new_row = pd.DataFrame({'address': [new_addr], 'city': [new_city], 'postal code': [new_zip], 
                                'type': [new_type], 'status': ['Pending']})
        st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
        st.rerun()

# --- DRIVER WORKFLOW ---
if not st.session_state.df.empty:
    
    # Βελτιστοποίηση
    if st.button("🔀 Βελτιστοποίηση Διαδρομής"):
        pending = st.session_state.df[st.session_state.df['status'] == 'Pending'].copy()
        done = st.session_state.df[st.session_state.df['status'] != 'Pending']
        # Εδώ μπαίνει η λογική βελτιστοποίησης
        st.session_state.df = pd.concat([pending.iloc[::-1], done])
        st.rerun()

    pending = st.session_state.df[st.session_state.df['status'] == 'Pending']
    
    if not pending.empty:
        current_idx = pending.index[0]
        current = st.session_state.df.loc[current_idx]
        
        st.subheader(f"📍 Στάση: {current['address']}")
        st.session_state.df.at[current_idx, 'type'] = st.radio(
            "Τύπος:", ['Παράδοση', 'Παραλαβή'], index=0 if current['type'] == 'Παράδοση' else 1
        )
        
        # Controls
        c1, c2 = st.columns(2)
        if c1.button("✅ Ολοκλήρωση"):
            st.session_state.df.loc[current_idx, 'status'] = 'Done'
            st.rerun()
        if c2.button("⏭️ Skip"):
            st.session_state.df.loc[current_idx, 'status'] = 'Skipped'
            st.rerun()
            
        maps_link = f"https://www.google.com/maps/dir/?api=1&destination={current['address']},{current['city']}"
        st.link_button("🚀 Έναρξη Πλοήγησης", maps_link)
    else:
        st.success("🎉 Όλες οι στάσεις ολοκληρώθηκαν!")

    with st.sidebar:
        st.dataframe(st.session_state.df[['address', 'status', 'type']])