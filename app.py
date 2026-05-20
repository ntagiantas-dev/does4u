import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim

# Ρύθμιση για το Geocoding
geolocator = Nominatim(user_agent="my_route_app")

def get_lat_lon(row):
    full_address = f"{row['address']}, {row['city']}, {row['postal code']}, Greece"
    try:
        location = geolocator.geocode(full_address)
        if location:
            return location.latitude, location.longitude
    except:
        pass
    return None, None

def show_route_planner():
    st.title("📍 Route Planner")
    
    # Το σωστό σημείο για να ορίσουμε το uploaded_file
    uploaded_file = st.file_uploader("Ανέβασε το CSV (με στήλες: address, city, postal code)", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        
        # Έλεγχος αν υπάρχουν οι σωστές στήλες
        if all(col in df.columns for col in ['address', 'city', 'postal code']):
            
            # Μετατροπή μόνο αν δεν έχουμε ήδη lat/lon
            if 'lat' not in df.columns:
                with st.spinner('Μετατροπή διευθύνσεων...'):
                    coords = df.apply(get_lat_lon, axis=1)
                    df['lat'], df['lon'] = zip(*coords)
                    st.session_state.stops_data = df.dropna()
            
            # Εμφάνιση Χάρτη
            if 'stops_data' in st.session_state:
                st.map(st.session_state.stops_data)
        else:
            st.error("Το αρχείο πρέπει να έχει τις στήλες: address, city, postal code")

# Κύριο μενού
show_route_planner()import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim

# Ρύθμιση για το Geocoding
geolocator = Nominatim(user_agent="my_route_app")

def get_lat_lon(row):
    full_address = f"{row['address']}, {row['city']}, {row['postal code']}, Greece"
    try:
        location = geolocator.geocode(full_address)
        if location:
            return location.latitude, location.longitude
    except:
        pass
    return None, None

def show_route_planner():
    st.title("📍 Route Planner")
    
    # Το σωστό σημείο για να ορίσουμε το uploaded_file
    uploaded_file = st.file_uploader("Ανέβασε το CSV (με στήλες: address, city, postal code)", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        
        # Έλεγχος αν υπάρχουν οι σωστές στήλες
        if all(col in df.columns for col in ['address', 'city', 'postal code']):
            
            # Μετατροπή μόνο αν δεν έχουμε ήδη lat/lon
            if 'lat' not in df.columns:
                with st.spinner('Μετατροπή διευθύνσεων...'):
                    coords = df.apply(get_lat_lon, axis=1)
                    df['lat'], df['lon'] = zip(*coords)
                    st.session_state.stops_data = df.dropna()
            
            # Εμφάνιση Χάρτη
            if 'stops_data' in st.session_state:
                st.map(st.session_state.stops_data)
        else:
            st.error("Το αρχείο πρέπει να έχει τις στήλες: address, city, postal code")

# Κύριο μενού
show_route_planner()