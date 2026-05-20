import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Does4u Pro", layout="wide")

# --- INITIALIZATION ---
if 'df' not in st.session_state: st.session_state.df = pd.DataFrame()
if 'is_optimized' not in st.session_state: st.session_state.is_optimized = False
if 'depot_info' not in st.session_state: st.session_state.depot_info = None
if 'route_info' not in st.session_state: st.session_state.route_info = {'total_time': 0, 'eta': None}

# --- FUNCTIONS ---
def validate_and_process(df):
    required = ['address', 'city', 'postal code']
    if not all(col in df.columns for col in required): return False, "Λείπουν στήλες (address, city, postal code)"
    df['status'] = 'Pending'; df['type'] = 'Παράδοση'
    return True, df

def get_eta_calculation(pending_df):
    pending_count = len(pending_df)
    # 5 λεπτά ανά στάση + 10 λεπτά μέσος όρος οδήγησης ανά στάση
    total_minutes = (pending_count * 5) + (pending_count * 10)
    eta = datetime.now() + timedelta(minutes=total_minutes)
    return total_minutes, eta

def optimize_route_logic(depot_addr, depot_city, depot_zip):
    depot_start = pd.DataFrame({'address': [depot_addr], 'city': [depot_city], 'postal code': [depot_zip], 'status': ['Depot'], 'type': ['Αφετηρία']})
    depot_end = pd.DataFrame({'address': [depot_addr], 'city': [depot_city], 'postal code': [depot_zip], 'status': ['Depot'], 'type': ['Τερματισμός']})
    
    pending = st.session_state.df[st.session_state.df['status'] == 'Pending']
    done = st.session_state.df[st.session_state.df['status'] == 'Done']
    
    optimized_pending = pending.sort_values(by='address')
    st.session_state.df = pd.concat([depot_start, optimized_pending, done, depot_end], ignore_index=True)
    
    total_min, eta = get_eta_calculation(optimized_pending)
    st.session_state.route_info = {'total_time': total_min, 'eta': eta}
    st.session_state.is_optimized = True
    st.session_state.depot_info = {'address': depot_addr, 'city': depot_city, 'zip': depot_zip}

# --- UI ---
st.title("🚚 Does4u - Professional Driver Portal")
uploaded_file = st.file_uploader("Ανέβασε τη λίστα σου (CSV)", type="csv")
if uploaded_file and st.session_state.df.empty:
    success, result = validate_and_process(pd.read_csv(uploaded_file, encoding='utf-8-sig'))
    if success: st.session_state.df = result; st.rerun()
    else: st.error(result)

with st.sidebar:
    st.write("### 🛠️ Εργαλεία")
    
    if st.session_state.is_optimized and st.session_state.route_info['eta'] is not None:
        st.metric("⏳ Συνολικός Χρόνος", f"{st.session_state.route_info['total_time']} λεπτά")
        st.metric("🏁 Εκτιμώμενη Άφιξη", st.session_state.route_info['eta'].strftime("%H:%M"))
    
    with st.expander("➕ Προσθήκη Έκτακτης Στάσης"):
        with st.form("emergency_stop"):
            addr, city, zip_c = st.text_input("Διεύθυνση"), st.text_input("Πόλη"), st.text_input("Τ.Κ.")
            if st.form_submit_button("Ενσωμάτωση"):
                new_row = pd.DataFrame({'address': [addr], 'city': [city], 'postal code': [zip_c], 'status': ['Pending'], 'type': ['Παράδοση']})
                st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                st.session_state.is_optimized = False; st.rerun()

    if not st.session_state.df.empty and not st.session_state.is_optimized:
        with st.expander("📍 Ορισμός Αφετηρίας", expanded=True):
            with st.form("depot_form"):
                d_a = st.text_input("Διεύθυνση", value=(st.session_state.depot_info['address'] if st.session_state.depot_info else ""))
                d_c = st.text_input("Πόλη", value=(st.session_state.depot_info['city'] if st.session_state.depot_info else ""))
                d_z = st.text_input("Τ.Κ.", value=(st.session_state.depot_info['zip'] if st.session_state.depot_info else ""))
                if st.form_submit_button("🚀 Εκτέλεση"): 
                    optimize_route_logic(d_a, d_c, d_z); st.rerun()
                
    st.write("### Πρόοδος")
    
    # Εδώ γίνεται ο έλεγχος: Εμφανίζουμε το dataframe ΜΟΝΟ αν έχει δεδομένα 
    # και αν οι στήλες που ζητάμε υπάρχουν όντως μέσα του.
    if not st.session_state.df.empty:
        # Επιλέγουμε μόνο όσες από τις ζητούμενες στήλες υπάρχουν πραγματικά
        cols_to_show = [col for col in ['address', 'status', 'type'] if col in st.session_state.df.columns]
        
        if cols_to_show:
            st.dataframe(st.session_state.df[cols_to_show])
        else:
            # Αν για κάποιο λόγο το dataframe δεν έχει τις στήλες, δείξε ολόκληρο το dataframe
            st.dataframe(st.session_state.df)
    else:
        st.info("Ανέβασε αρχείο CSV για να εμφανιστεί η λίστα.")