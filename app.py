import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim

# Αρχικοποίηση του geocoder
geolocator = Nominatim(user_agent="my_route_app")

def get_lat_lon(row):
    # Ενώνουμε τις τρεις στήλες σε μία πλήρη διεύθυνση
    full_address = f"{row['address']}, {row['city']}, {row['postal code']}, Greece"
    try:
        location = geolocator.geocode(full_address)
        if location:
            return location.latitude, location.longitude
    except:
        return None, None
    return None, None

# Στο σημείο που διαβάζεις το CSV:
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    if 'lat' not in df.columns:
        with st.spinner('Μετατροπή διευθύνσεων...'):
            # Εδώ περνάμε ολόκληρη τη γραμμή (row) στη συνάρτηση
            coords = df.apply(get_lat_lon, axis=1)
            df['lat'], df['lon'] = zip(*coords)
            st.session_state.stops_data = df.dropna()
def show_route_planner():
    st.title("📍 Route Planner")
    uploaded_file = st.file_uploader("Ανέβασε το CSV με τις στάσεις σου", type="csv")

    if uploaded_file is not None: # Πιο ασφαλής έλεγχος
        try:
            df = pd.read_csv(uploaded_file)
            
            # Ελέγχουμε αν υπάρχουν οι σωστές στήλες
            required_cols = ['address', 'city', 'postal code']
            if all(col in df.columns for col in required_cols):
                
                if 'lat' not in df.columns:
                    with st.spinner('Μετατροπή διευθύνσεων σε χάρτη...'):
                        coords = df.apply(get_lat_lon, axis=1)
                        df['lat'], df['lon'] = zip(*coords)
                        st.session_state.stops_data = df.dropna()
                
                # Εμφάνιση Χάρτη
                if 'stops_data' in st.session_state:
                    st.map(st.session_state.stops_data)
            else:
                st.error(f"Το αρχείο πρέπει να έχει τις στήλες: {required_cols}")
        except Exception as e:
            st.error(f"Σφάλμα κατά την ανάγνωση του αρχείου: {e}")
        
        # Μετατροπή διευθύνσεων σε lat/lon αν δεν υπάρχουν
        if 'lat' not in df.columns:
            with st.spinner('Μετατροπή διευθύνσεων...'):
                coords = df['address'].apply(get_lat_lon)
                df['lat'], df['lon'] = zip(*coords)
                st.session_state.stops_data = df.dropna() # Πετάμε όσες δεν βρέθηκαν

        # Εμφάνιση Χάρτη
        if 'stops_data' in st.session_state:
            st.map(st.session_state.stops_data)
            
            # Διαχείριση Στάσεων
            st.subheader("Λίστα Στάσεων")
            st.dataframe(st.session_state.stops_data)

# Sidebar μενού
st.sidebar.title("Navigation")
menu = st.sidebar.selectbox("Επίλεξε Εργαλείο", ["Route Planner"])
if menu == "Route Planner":
    show_route_planner()