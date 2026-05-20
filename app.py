import streamlit as st
import pandas as pd

st.set_page_config(page_title="Does4u Pro", layout="wide")

# --- INITIALIZATION ---
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()
if 'is_optimized' not in st.session_state:
    st.session_state.is_optimized = False
if 'depot_info' not in st.session_state:
    st.session_state.depot_info = None

# --- FUNCTIONS ---
def validate_and_process(df):
    required = ['address', 'city', 'postal code']
    if not all(col in df.columns for col in required):
        return False, "Λείπουν στήλες (address, city, postal code)"
    df['status'] = 'Pending'
    df['type'] = 'Παράδοση'
    return True, df

def optimize_route_logic(depot_addr, depot_city, depot_zip):
    # Δημιουργία εγγραφών Depot
    depot_start = pd.DataFrame({'address': [depot_addr], 'city': [depot_city], 'postal code': [depot_zip], 'status': ['Depot'], 'type': ['Αφετηρία']})
    depot_end = pd.DataFrame({'address': [depot_addr], 'city': [depot_city], 'postal code': [depot_zip], 'status': ['Depot'], 'type': ['Τερματισμός']})
    
    pending = st.session_state.df[st.session_state.df['status'] == 'Pending']
    done = st.session_state.df[st.session_state.df['status'] == 'Done']
    
    # Βελτιστοποίηση μόνο των Pending
    optimized_pending = pending.sort_values(by='address')
    
    # Σύνθεση: Depot Start + Optimized Pending + Done + Depot End
    st.session_state.df = pd.concat([depot_start, optimized_pending, done, depot_end], ignore_index=True)
    st.session_state.is_optimized = True
    st.session_state.depot_info = {'address': depot_addr, 'city': depot_city, 'zip': depot_zip}

# --- UI LOGIC ---
st.title("🚚 Does4u - Professional Driver Portal")

uploaded_file = st.file_uploader("Ανέβασε τη λίστα σου (CSV)", type="csv")
if uploaded_file and st.session_state.df.empty:
    raw_df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
    success, result = validate_and_process(raw_df)
    if success:
        st.session_state.df = result
        st.success("Λίστα φορτώθηκε!")
    else:
        st.error(result)

with st.sidebar:
    st.write("### 🛠️ Εργαλεία")
    
    with st.expander("➕ Προσθήκη Έκτακτης Στάσης"):
        with st.form("emergency_stop"):
            addr = st.text_input("Διεύθυνση")
            city = st.text_input("Πόλη")
            zip_c = st.text_input("Τ.Κ.")
            if st.form_submit_button("Ενσωμάτωση"):
                new_row = pd.DataFrame({'address': [addr], 'city': [city], 'postal code': [zip_c], 'status': ['Pending'], 'type': ['Παράδοση']})
                st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                st.session_state.is_optimized = False
                st.rerun()

    if not st.session_state.df.empty:
        # Αν δεν έχει οριστεί Depot, ζητάμε στοιχεία
        if not st.session_state.is_optimized:
            with st.expander("📍 Ορισμός Αφετηρίας για Βελτιστοποίηση", expanded=True):
                with st.form("depot_form"):
                    d_addr = st.text_input("Διεύθυνση Αφετηρίας", value=st.session_state.depot_info['address'] if st.session_state.depot_info else "")
                    d_city = st.text_input("Πόλη", value=st.session_state.depot_info['city'] if st.session_state.depot_info else "")
                    d_zip = st.text_input("Τ.Κ.", value=st.session_state.depot_info['zip'] if st.session_state.depot_info else "")
                    if st.form_submit_button("🚀 Εκτέλεση Βελτιστοποίησης"):
                        optimize_route_logic(d_addr, d_city, d_zip)
                        st.rerun()
            
        st.write("### Πρόοδος")
        st.dataframe(st.session_state.df[['address', 'status', 'type']])

if not st.session_state.df.empty and st.session_state.is_optimized:
    # Φιλτράρουμε τις ενεργές στάσεις (αγνοούμε τις γραμμές Depot)
    pending = st.session_state.df[st.session_state.df['status'] == 'Pending']
    
    if not pending.empty:
        current = pending.iloc[0]
        st.subheader(f"📍 Επόμενη Στάση: {current['address']}")
        
        c1, c2 = st.columns(2)
        if c1.button("✅ Ολοκλήρωση"):
            st.session_state.df.loc[st.session_state.df.index == current.name, 'status'] = 'Done'
            st.rerun()
        if c2.button("⏭️ Skip"):
            st.session_state.df.loc[st.session_state.df.index == current.name, 'status'] = 'Skipped'
            st.rerun()
            
        maps_link = f"https://www.google.com/maps/dir/?api=1&destination={current['address']},{current['city']}"
        st.link_button("🚀 Έναρξη Πλοήγησης", maps_link)
    else:
        st.success("🎉 Όλες οι στάσεις ολοκληρώθηκαν! Επιστροφή στη βάση.")