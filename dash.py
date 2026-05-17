import streamlit as st
import json
import os

# =====================================================================
# === ΕΝΟΤΗΤΑ 1: Setup & Συναρτήσεις "Αποθήκης" (JSON)
# =====================================================================
# Το αρχείο που θα αποθηκεύει τους κωδικούς σου μόνιμα
CODES_FILE = "promo_codes.json"

def load_codes():
    """Φορτώνει τους κωδικούς με υποστήριξη ελληνικών χαρακτήρων (utf-8)"""
    if os.path.exists(CODES_FILE):
        try:
            with open(CODES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_codes(codes):
    """Αποθηκεύει τους κωδικούς τακτοποιημένους με όμορφη στοίχιση"""
    with open(CODES_FILE, "w", encoding="utf-8") as f:
        json.dump(codes, f, ensure_ascii=False, indent=4)


# =====================================================================
# === ΕΝΟΤΗΤΑ 2: Η Κύρια Οθόνη & Φόρμα Προσθήκης Κωδικού
# =====================================================================
def show_promo_dashboard():
    """Η κύρια συνάρτηση που εμφανίζει το Dashboard των Promo Codes στο Admin"""
    st.markdown("### 🎫 Does4U Revenue Control")
    
    # Φόρτωση των τρεχόντων κωδικών
    codes = load_codes()

    # Προσθήκη νέου κωδικού προσφοράς
    with st.expander("➕ Προσθήκη Νέου Κωδικού"):
        new_c = st.text_input("Γράψε τον κωδικό (π.χ. CLIENT100):").upper().strip()
        if st.button("Ενεργοποίηση"):
            if new_c and new_c not in codes:
                codes.append(new_c)
                save_codes(codes)
                st.success(f"Ο κωδικός {new_c} είναι πλέον LIVE!")
                st.rerun()
            elif new_c in codes:
                st.warning("⚠️ Αυτός ο κωδικός υπάρχει ήδη!")


# =====================================================================
# === ΕΝΟΤΗΤΑ 3: Λίστα Ενεργών Κωδικών & Διαγραφή
# =====================================================================
    st.write("---")
    
    # Λίστα διαχείρισης και επισκόπησης των κωδικών
    st.write("#### Ενεργοί Κωδικοί στην Πλατφόρμα:")
    if not codes:
        st.info("Δεν υπάρχουν ενεργοί κωδικοί αυτή τη στιγμή.")
    else:
        for c in codes:
            col1, col2 = st.columns([4, 1])
            # Εμφάνιση του κωδικού σε γκρι πλαίσιο κώδικα για να ξεχωρίζει
            col1.code(c)
            # Κουμπί άμεσης διαγραφής
            if col2.button("❌", key=f"del_{c}"):
                codes.remove(c)
                save_codes(codes)
                st.rerun()