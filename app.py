import streamlit as st
import pandas as pd

st.set_page_config(page_title="Does4u Pro", layout="wide")

# --- INITIALIZATION ---
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()
if 'is_optimized' not in st.session_state:
    st.session_state.is_optimized = False

# --- FUNCTIONS ---
def validate_and_process(df):
    required = ['address', 'city', 'postal code']
    if not all(col in df.columns for col in required):
        return False, "Λείπουν στήλες (address, city, postal code)"
    df['status'] = 'Pending'
    df['type'] = 'Παράδοση'
    return True, df

def optimize_route_logic():
    """Εδώ θα έμπαινε το API call του Geoapify."""
    pending = st.session_state.df[st.session_state.df['status'] == 'Pending']
    done = st.session_state.df[st.session_state.df['status'] != 'Pending']
    
    # Placeholder: Ταξινόμηση βάσει διεύθυνσης (αντικατάστησε με Geoapify API logic)
    optimized = pending.sort_values(by='address')
    
    st.session_state.df = pd.concat([optimized, done]).reset_index(drop=True)
    st.session_state.is_optimized = True

# --- UI LOGIC ---
st.title("🚚 Does4u - Professional Driver Portal")

# 1. Φόρτωση αρχείου
uploaded_file = st.file_uploader("Ανέβασε τη λίστα σου (CSV)", type="csv")
if uploaded_file and st.session_state.df.empty:
    raw_df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
    success, result = validate_and_process(raw_df)
    if success:
        st.session_state.df = result
        st.success("Λίστα φορτώθηκε!")
    else:
        st.error(result)

# 2. Sidebar: Διαχείριση
with st.sidebar:
    st.write("### 🛠️ Εργαλεία")
    
    # Προσθήκη Έκτακτης Στάσης
    with st.expander("➕ Προσθήκη Έκτακτης Στάσης"):
        with st.form("emergency_stop"):
            addr = st.text_input("Διεύθυνση")
            city = st.text_input("Πόλη")
            zip_c = st.text_input("Τ.Κ.")
            if st.form_submit_button("Ενσωμάτωση"):
                new_row = pd.DataFrame({'address': [addr], 'city': [city], 'postal code': [zip_c], 'status': ['Pending'], 'type': ['Παράδοση']})
                st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                st.session_state.is_optimized = False # Απαιτείται επανυπολογισμός
                st.rerun()

    if not st.session_state.df.empty:
        if st.button("🚀 Βελτιστοποίηση Διαδρομής"):
            optimize_route_logic()
            st.rerun()
            
        st.write("### Πρόοδος")
        st.dataframe(st.session_state.df[['address', 'status', 'type']])

# 3. Main Workflow
if not st.session_state.df.empty:
    if not st.session_state.is_optimized:
        st.warning("⚠️ Πρέπει να πατήσετε 'Βελτιστοποίηση Διαδρομής' για να ξεκινήσετε.")
    else:
        pending = st.session_state.df[st.session_state.df['status'] == 'Pending']
        if not pending.empty:
            current = pending.iloc[0]
            st.subheader(f"📍 Επόμενη Στάση: {current['address']}")
            
            # Action Buttons
            c1, c2 = st.columns(2)
            if c1.button("✅ Ολοκλήρωση"):
                st.session_state.df.loc[st.session_state.df.index == current.name, 'status'] = 'Done'
                st.rerun()
            if c2.button("⏭️ Skip"):
                st.session_state.df.loc[st.session_state.df.index == current.name, 'status'] = 'Skipped'
                st.rerun()
                
            maps_link = f"https://www.google.com/maps/dir/?api=1&destination={current['address']},{current['city']}"
            st.link_button("🚀 Έναρξη Πλοήγησης (1η στάση)", maps_link)
        else:
            st.success("🎉 Όλες οι στάσεις ολοκληρώθηκαν!")