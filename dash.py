import streamlit as st
import json
import os

# Το αρχείο που θα αποθηκεύει τους κωδικούς σου μόνιμα
CODES_FILE = "promo_codes.json"

def load_codes():
    if os.path.exists(CODES_FILE):
        try:
            with open(CODES_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_codes(codes):
    with open(CODES_FILE, "w") as f:
        json.dump(codes, f)

# Η κύρια συνάρτηση που θα εμφανίζει το Dashboard
def show_promo_dashboard():
    st.markdown("### 🎫 Does4U Revenue Control")
    
    # Φόρτωση των κωδικών
    codes = load_codes()

    # Προσθήκη νέου κωδικού
    with st.expander("➕ Προσθήκη Νέου Κωδικού"):
        new_c = st.text_input("Γράψε τον κωδικό (π.β. CLIENT100):").upper().strip()
        if st.button("Ενεργοποίηση"):
            if new_c and new_c not in codes:
                codes.append(new_c)
                save_codes(codes)
                st.success(f"Ο κωδικός {new_c} είναι πλέον LIVE!")
                st.rerun()

    st.write("---")
    
    # Λίστα διαχείρισης
    st.write("#### Ενεργοί Κωδικοί στην Πλατφόρμα:")
    if not codes:
        st.info("Δεν υπάρχουν ενεργοί κωδικοί.")
    else:
        for c in codes:
            col1, col2 = st.columns([4, 1])
            col1.code(c)
            if col2.button("❌", key=f"del_{c}"):
                codes.remove(c)
                save_codes(codes)
                st.rerun()