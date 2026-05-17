#=======================================================
#== 🎨 ΕΝΟΤΗΤΑ 1: Setup, Εισαγωγή Streamlit & Global CSS
#=======================================================
import streamlit as st
import json
import os
from datetime import datetime

# 1. Ρύθμιση Σελίδας
st.set_page_config(page_title="Does4U | Strategic Intelligence", layout="wide")

# 2. Εφαρμογή Custom CSS (Στυλ, Tags, Banners)
st.markdown("""
    <style>
        /* Εξαφανίζει το κουμπί collapse (βελάκι) του sidebar */
        [data-testid="stSidebarCollapseButton"] { display: none !important; }
        
        /* Μηδενίζει το κενό στην κορυφή του Sidebar */
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] { padding-top: 0rem !important; }
        
        /* Τραβάει το Logo τέρμα πάνω */
        [data-testid="stSidebar"] img { margin-top: -45px !important; width: 100%; height: auto; }

        /* Στυλ για τα Tags των κατηγοριών */
        .category-tag {
            background-color: #002b5b;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.75rem;
            font-weight: bold;
            text-transform: uppercase;
        }

        /* Banner Exchange Box (Δεξί Sidebar) */
        .banner-exchange-box {
            background: #f8f9fa;
            border: 2px dashed #ccc;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            color: #999;
            font-weight: bold;
            margin-bottom: 20px;
        }

        .main-title {
            color: #002b5b;
            font-family: 'Segoe UI', sans-serif;
            font-weight: 800;
        }
    </style>
""", unsafe_allow_html=True)
#===================================================================
#== 📦 ΕΝΟΤΗΤΑ 2: Συναρτήσεις Δεδομένων & Σχεδιασμός Άρθρου (Render)
#====================================================================
# 1. Φόρτωση άρθρων από τη βάση δεδομένων JSON
def load_posts():
    if os.path.exists("blog_data.json"):
        with open("blog_data.json", "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

# 2. Σχεδιασμός του άρθρου σε 2 στήλες (Εικόνα αριστερά - Κείμενο δεξιά)
def render_post(p):
    """Σχεδιάζει το άρθρο και φορτώνει τη μόνιμη εικόνα από τον φάκελο blog_images"""
    with st.container():
        col_img, col_txt = st.columns([1, 2.5])
        
        with col_img:
            img_path = p.get('image', '')
            
            # ΔΙΟΡΘΩΣΗ: Έλεγχος αν η μόνιμη εικόνα υπάρχει στον φάκελό μας
            if img_path and os.path.exists(img_path):
                st.image(img_path, use_container_width=True)
            else:
                # Αν για κάποιο λόγο δεν βρεθεί, βάζουμε μια γενική ειδοποίηση
                st.info("📷 AI Visual σε εκκρεμότητα")
        
        with col_txt:
            # Εμφάνιση Κατηγορίας, Τίτλου, Ημερομηνίας και Κειμένου
            st.markdown(f'<span class="category-tag">{p.get("category", "Ανάλυση")}</span>', unsafe_allow_html=True)
            st.header(p.get('title', 'Untitled'))
            st.caption(f"📅 {p.get('date', '')} | 🎯 Στόχος: {p.get('title', 'Γενικός')}")
            st.write(p.get('content', ''))
            
            # Εμφάνιση του Teaser για Social Media (αν υπάρχει)
            if p.get('teaser'):
                with st.expander("📱 Προεπισκόπηση Social Media Post"):
                    st.info(p['teaser'])
        st.divider()
#===================================================================
#== 📩 ΕΝΟΤΗΤΑ 3: Αριστερό Sidebar (Logo, Ειδοποιήσεις & Newsletter)
#===================================================================
with st.sidebar:
    # 1. Εμφάνιση Λογοτύπου Does4U
    if os.path.exists("does4u_logo.png"):
        st.image("does4u_logo.png")
    else:
        st.title("DOES4U AI")

    # 2. Notification Box
    st.markdown("""
        <div style="background: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #002b5b; margin: 10px 0;">
            <h4 style="margin:0; color: #002b5b;">🔔 Ειδοποιήσεις</h4>
            <p style="font-size: 0.85rem; color: #444; margin-top:5px;">
                Ενημερώσεις σε πραγματικό χρόνο για νέα ΦΕΚ και νομοσχέδια.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.write("")

    # 3. Λειτουργικό Newsletter System
    st.markdown("#### 📩 Newsletter")
    email_input = st.text_input("Email Address", placeholder="info@company.gr", label_visibility="collapsed", key="side_email_unique")
    if st.button("Εγγραφή τώρα", use_container_width=True, key="side_btn_unique"):
        if email_input and "@" in email_input:
            try:
                with open("subscribers.txt", "a", encoding="utf-8") as f:
                    f.write(f"{email_input}\n")
                st.success("Η εγγραφή ολοκληρώθηκε! 🎉")
            except:
                st.error("Σφάλμα αποθήκευσης.")
        else:
            st.warning("Βάλτε ένα έγκυρο email.")

    st.divider()
    st.caption("© 2026 Does4U Strategic Intelligence")
#=======================================================================
#== 📰 ΕΝΟΤΗΤΑ 4: Κεντρική Οθόνη Blog (Επικεφαλίδα & Tabs Φιλτραρίσματος)
#=======================================================================
# Χωρίζουμε την κύρια οθόνη σε 2 μέρη (Κεντρικό Blog και Δεξί Διαφημιστικό Sidebar)
col_main, col_exchange = st.columns([4, 1])

with col_main:
    # 1. Κεντρική εντυπωσιακή επικεφαλίδα με τα επίσημα χρώματα (Μπλε - Κίτρινο)
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="font-family: 'Segoe UI', sans-serif; font-weight: 800; font-size: 2.8rem; margin-bottom: 5px; line-height: 1.2;">
                <span style="color: #333;">Ιστολόγιο</span> 
                <span style="color: #002b5b;">does</span><span style="color: #f3a61c;">4u</span>
            </h1>
            <p style="color: #666; font-size: 1.1rem; font-style: italic;">
                Στρατηγική Ανάλυση Δεδομένων & Νομοθεσίας
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 2. Δημιουργία των Tabs
    t_all, t_fek, t_parl, t_bus = st.tabs([
        "🗂️ Όλες οι Αναλύσεις", 
        "📜 ΦΕΚ", 
        "🏛️ Βουλή", 
        "💡 Επιχειρηματικότητα"
    ])

    # Φόρτωση των άρθρων
    posts = load_posts()

    # TAB 1: Όλα τα άρθρα (Εμφανίζονται πρώτα τα πιο πρόσφατα - δεν χρειάζεται reversed αν το Admin κάνει ήδη insert στο 0)
    with t_all:
        if posts:
            for p in posts: 
                render_post(p)
        else:
            st.info("Δεν υπάρχουν ακόμη αναλύσεις.")

    # TAB 2: Φιλτράρισμα μόνο για ΦΕΚ
    with t_fek:
        # ΔΙΟΡΘΩΣΗ: Συγχρονισμός με το όνομα κατηγορίας του Admin ("ΦΕΚ")
        fek_posts = [p for p in posts if p.get('category') == "ΦΕΚ"]
        if fek_posts:
            for p in fek_posts: 
                render_post(p)
        else:
            st.info("Δεν βρέθηκαν αναλύσεις ΦΕΚ.")

    # TAB 3: Φιλτράρισμα μόνο για τη Βουλή
    with t_parl:
        # ΔΙΟΡΘΩΣΗ: Συγχρονισμός με το όνομα κατηγορίας του Admin ("Βουλή")
        parl_posts = [p for p in posts if p.get('category') == "Βουλή"]
        if parl_posts:
            for p in parl_posts: 
                render_post(p)
        else:
            st.info("Δεν βρέθηκαν αναλύσεις για τη Βουλή.")

    # TAB 4: Φιλτράρισμα για την Επιχειρηματικότητα
    with t_bus:
        # ΔΙΟΡΘΩΣΗ: Συγχρονισμός με το όνομα κατηγορίας του Admin ("Επιχειρηματικότητα")
        bus_posts = [p for p in posts if p.get('category') == "Επιχειρηματικότητα"]
        if bus_posts:
            for p in bus_posts: 
                render_post(p)
        else:
            st.info("Δεν υπάρχουν ακόμη αναλύσεις Επιχειρηματικότητας.")
#====================================================================
#==🚀 ΕΝΟΤΗΤΑ 5: Δεξί Sidebar (Banner Exchange & App Promo) & Footer
#====================================================================
with col_exchange:
    st.markdown("### 🚀 Partners")
    
    # 1. Box Ανταλλαγής Διαφημιστικών Banners
    st.markdown("""
        <div class="banner-exchange-box">
            AD SPACE<br>BANNER EXCHANGE
        </div>
    """, unsafe_allow_html=True)

    # 2. Κάρτα Προώθησης της Πλατφόρμας (Promo Card)
    st.markdown("""
        <div style="background: linear-gradient(180deg, #002b5b 0%, #001a38 100%); padding: 25px; border-radius: 20px; color: white; text-align: center;">
            <p style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; opacity: 0.8; margin-bottom: 10px;">Coming Soon</p>
            <h4 style="color: white; margin: 10px 0;">Does4U AI Platform</h4>
            <p style="font-size: 0.8rem; opacity: 0.9; line-height: 1.4;">
                Ο απόλυτος ψηφιακός αναλυτής για επιχειρήσεις.
            </p>
            <div style="background: rgba(255,255,255,0.15); padding: 10px; border-radius: 10px; margin-top: 20px; font-size: 0.75rem; font-weight: bold;">
                ⚡ ΑΠΟΚΛΕΙΣΤΙΚΑ ΓΙΑ ΤΟ 2026
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    st.info("💡 Το Intelligence Hub ενημερώνεται αυτόματα.")

# 3. FOOTER (Το κάτω μέρος της σελίδας)
st.markdown("---")
st.caption("Does4U Intelligence System v1.0 | Professional Grade Analysis")
#======================================================