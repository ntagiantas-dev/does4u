import streamlit as st
import pandas as pd

# --- Λογική Route Planner ---
def show_route_planner():
    st.title("📍 Route Planner")
    uploaded_file = st.file_uploader("Ανέβασε το CSV με τις στάσεις σου", type="csv")

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        if 'status' not in df.columns:
            df['status'] = 'pending'
            st.session_state.stops_data = df

        if 'stops_data' in st.session_state:
            # Εμφάνιση Χάρτη
            st.map(st.session_state.stops_data)

            # Διαχείριση Στάσεων
            st.subheader("Τρέχουσα Διαδρομή")
            for i, row in st.session_state.stops_data.iterrows():
                if row['status'] == 'pending':
                    st.write(f"🛑 Στάση: {row['address']}")
                    col1, col2 = st.columns(2)
                    if col1.button("✅ Ολοκληρώθηκε", key=f"done_{i}"):
                        st.session_state.stops_data.at[i, 'status'] = 'done'
                        st.rerun()
                    if col2.button("⏭️ Skip", key=f"skip_{i}"):
                        st.session_state.stops_data.at[i, 'status'] = 'skipped'
                        st.rerun()
                    break 

# --- Κεντρική σελίδα App ---
st.sidebar.title("Navigation")
menu = st.sidebar.selectbox("Επίλεξε Εργαλείο", ["Route Planner", "Other Tools"])

if menu == "Route Planner":
    show_route_planner()
else:
    st.write("Καλωσήρθες στο DOES4U!")
    