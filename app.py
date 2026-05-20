import streamlit as st
import pandas as pd
import requests
import os

# Ρύθμιση σελίδας
st.set_page_config(page_title="Does4u", layout="wide")
st.title("📍 Does4u - Geocoding & Mapping")

# Φόρτωση API Key από τα secrets
GEOAPIFY_KEY = st.secrets["GEOAPIFY_API_KEY"]

@st.cache_data # Αυτό κάνει το "μαγικό" να μην ξανατρέχει αν δεν αλλάξουν τα δεδομένα
def get_clean_data(df):
    results = []
    for _, row in df.iterrows():
        address_query = f"{row['address']}, {row['postal code']}, {row['city']}, Greece"
        url = f"https://api.geoapify.com/v1/geocode/search?text={address_query}&apiKey={GEOAPIFY_KEY}"
        
        try:
            response = requests.get(url).json()
            if response['features']:
                prop = response['features'][0]['properties']
                results.append({'lat': prop.get('lat'), 'lon': prop.get('lon'), 'formatted': prop.get('formatted')})
            else:
                results.append({'lat': None, 'lon': None, 'formatted': None})
        except:
            results.append({'lat': None, 'lon': None, 'formatted': None})
    
    return pd.concat([df, pd.DataFrame(results)], axis=1)

# --- Ροή Εργασίας ---
# 1. Έλεγχος για το δοκιμαστικό αρχείο
test_file = "test_addresses.csv"
if os.path.exists(test_file):
    st.info(f"Ανιχνεύθηκε το {test_file}! Χρήση του για τις δοκιμές σας.")
    df = pd.read_csv(test_file)
else:
    uploaded_file = st.file_uploader("Ανέβασε το CSV (αν δεν υπάρχει το test_addresses.csv)", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
    else:
        df = None

# 2. Επεξεργασία
if df is not None:
    if st.button("🚀 Καθαρισμός Δεδομένων"):
        with st.spinner('Το Does4u δουλεύει...'):
            df_cleaned = get_clean_data(df)
            st.session_state.df = df_cleaned
            st.success("Έτοιμο!")

    # 3. Εμφάνιση
    if 'df' in st.session_state:
        st.dataframe(st.session_state.df)
        st.map(st.session_state.df[['lat', 'lon']])