import streamlit as st
import pandas as pd
import requests
import os

st.set_page_config(page_title="Does4u Logistics", layout="wide")
st.title("🚚 Does4u - Professional Logistics Manager")

# Φόρτωση API Key
GEOAPIFY_KEY = st.secrets["GEOAPIFY_API_KEY"]

# Συναρτήσεις εργαλείων
def get_coords(row):
    url = f"https://api.geoapify.com/v1/geocode/search?text={row['address']}, {row['postal code']}, {row['city']}, Greece&apiKey={GEOAPIFY_KEY}"
    try:
        resp = requests.get(url).json()
        if resp['features']:
            coords = resp['features'][0]['geometry']['coordinates']
            return coords[1], coords[0] # lat, lon
    except:
        pass
    return None, None

# Αρχικοποίηση Session
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()

# 1. Upload & Auto-Geocode
uploaded_file = st.file_uploader("Ανέβασε τη λίστα σου (CSV)", type="csv")
if uploaded_file and st.session_state.df.empty:
    df = pd.read_csv(uploaded_file)
    df['status'] = 'Pending'
    with st.spinner('Το Does4u καθαρίζει τις διευθύνσεις...'):
        coords = df.apply(get_coords, axis=1)
        df['lat'], df['lon'] = zip(*coords)
        st.session_state.df = df
        st.rerun()

# 2. Διαχείριση Στάσεων
    if not st.session_state.df.empty and 'status' in st.session_state.df.columns:
        pending = st.session_state.df[st.session_state.df['status'] == 'Pending']
        
        if not pending.empty:
            current = pending.iloc[0]
            st.subheader(f"📍 Επόμενη Στάση: {current['address']} ({current['type']})")
        
        c1, c2 = st.columns(2)
        if c1.button("✅ Ολοκλήρωση"):
            st.session_state.df.loc[current.name, 'status'] = 'Done'
            st.rerun()
        if c2.button("⏭️ Skip"):
            st.session_state.df.loc[current.name, 'status'] = 'Skipped'
            st.rerun()
        
        st.map(pd.DataFrame([current]))
    else:
        st.success("Όλες οι στάσεις ολοκληρώθηκαν!")

    # 3. Export για ασφάλεια
    st.write("### Πίνακας Ελέγχου")
    st.dataframe(st.session_state.df)
    
    csv = st.session_state.df.to_csv(index=False).encode('utf-8')
    st.download_button("💾 Αποθήκευση Προόδου (Export CSV)", csv, "today_progress.csv", "text/csv")