import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim

# Αρχικοποίηση του geocoder
geolocator = Nominatim(user_agent="my_route_app")

def get_lat_lon(address):
    try:
        location = geolocator.geocode(address + ", Athens, Greece")
        if location:
            return location.latitude, location.longitude
    except:
        return None, None
    return None, None

def show_route_planner():
    st.title("📍 Route Planner")
    uploaded_file = st.file_uploader("Ανέβασε το CSV με τις στάσεις σου", type="csv")

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        
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