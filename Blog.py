#== 🎨 ΕΝΟΤΗΤΑ 1: Setup, Εισαγωγή Streamlit & Global CSS
#=======================================================
import streamlit as st
import json
import os
from datetime import datetime

# 1. Ρύθμιση Σελίδας
st.set_page_config(page_title="Does4U | Tech & Growth Insights", layout="wide")

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
            if img_path and os.path.exists(img_path):
                st.image(img_path, use_container_width=True)
            else:
                st.info("📷 AI Visual Technology")
        
        with col_txt:
            st.markdown(f'<span class="category-tag">{p.get("category", "Tech & AI")}</span>', unsafe_allow_html=True)
            st.header(p.get('title', 'Untitled'))
            st.caption(f"📅 {p.get('date', '')} | 🎯 Focus: {p.get('target', 'General')}")
            st.write(p.get('content', ''))
            
            if p.get('teaser'):
                with st.expander("📱 Copy Social Media Post"):
                    st.code(p['teaser'])
        st.divider()

#== 📩 ΕΝΟΤΗΤΑ 3: Αριστερό Sidebar (Logo, Ειδοποιήσεις & Newsletter)
#===================================================================
with st.sidebar:
    if os.path.exists("does4u_logo.png"):
        st.image("does4u_logo.png")
    else:
        st.title("DOES4U AI")

    # 2. Notification Box
    st.markdown("""
        <div style="background: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #002b5b; margin: 10px 0;">
            <h4 style="margin:0; color: #002b5b;">🔔 Live Updates</h4>
            <p style="font-size: 0.85rem; color: #444; margin-top:5px;">
                Πραγματικές αναλύσεις για Python, Web Scraping και Growth Hacking στρατηγικές.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.write("")

    # 3. Λειτουργικό Newsletter System
    st.markdown("#### 📩 Tech Newsletter")
    email_input = st.text_input("Email Address", placeholder="info@company.com", label_visibility="collapsed", key="side_email_unique")
    if st.button("Εγγραφή τώρα", use_container_width=True, key="side_btn_unique"):
        if email_input and "@" in email_input:
            try:
                with open("subscribers.txt", "a", encoding="utf-8") as f:
                    f.write(f"{email_input}\n")
                st.success("Καλώς ήρθες στην ομάδα! 🎉")
            except:
                st.error("Σφάλμα αποθήκευσης.")
        else:
            st.warning("Βάλτε ένα έγκυρο email.")

    st.divider()
    st.caption("© 2026 Does4U Automation Agency")

#=======================================================================
#== 📰 ΕΝΟΤΗΤΑ 4: Κεντρική Οθόνη Blog (Επικεφαλίδα & Tabs Φιλτραρίσματος)
#=======================================================================
col_main, col_exchange = st.columns([4, 1])

with col_main:
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="font-family: 'Segoe UI', sans-serif; font-weight: 800; font-size: 2.8rem; margin-bottom: 5px; line-height: 1.2;">
                <span style="color: #333;">Insights</span> 
                <span style="color: #002b5b;">does</span><span style="color: #f3a61c;">4u</span>
            </h1>
            <p style="color: #666; font-size: 1.1rem; font-style: italic;">
                SaaS Engineering, Advanced Automation & Growth Hacking
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 2. Δημιουργία των Νέων Tabs
    t_all, t_tech, t_growth = st.tabs([
        "🗂️ Όλες οι Αναλύσεις", 
        "💻 Python & AI Updates", 
        "📈 Growth Hacking"
    ])

    # Φόρτωση των άρθρων
    posts = load_posts()

    # TAB 1: Όλα τα άρθρα
    with t_all:
        if posts:
            for p in posts: 
                render_post(p)
        else:
            st.info("Δεν υπάρχουν ακόμη αναλύσεις.")

    # TAB 2: Φιλτράρισμα μόνο για Python & AI
    with t_tech:
        tech_posts = [p for p in posts if p.get('category') == "💻 Python & AI Updates"]
        if tech_posts:
            for p in tech_posts: 
                render_post(p)
        else:
            st.info("Δεν βρέθηκαν αναλύσεις για Python & AI.")

    # TAB 3: Φιλτράρισμα μόνο για Growth Hacking
    with t_growth:
        growth_posts = [p for p in posts if p.get('category') == "📈 Growth Hacking"]
        if growth_posts:
            for p in growth_posts: 
                render_post(p)
        else:
            st.info("Δεν βρέθηκαν αναλύσεις για Growth Hacking.")

#====================================================================
#==🚀 ΕΝΟΤΗΤΑ 5: Δεξί Sidebar (Banner Exchange & App Promo) & Footer
#====================================================================
with col_exchange:
    st.markdown("### 🚀 Products")
    
    st.markdown("""
        <div class="banner-exchange-box">
            DEAL HUNTER<br>BOT ACTIVE
        </div>
    """, unsafe_allow_html=True)

    # 2. Κάρτα Προώθησης της Πλατφόρμας (Promo Card)
    st.markdown("""
        <div style="background: linear-gradient(180deg, #002b5b 0%, #001a38 100%); padding: 25px; border-radius: 20px; color: white; text-align: center;">
            <p style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; opacity: 0.8; margin-bottom: 10px;">Live Automation</p>
            <h4 style="color: white; margin: 10px 0;">Custom SaaS Systems</h4>
            <p style="font-size: 0.8rem; opacity: 0.9; line-height: 1.4;">
                Χτίζουμε τα δικά σας εργαλεία scrapers και AI agents με άμεσο ROI.
            </p>
            <div style="background: rgba(255,255,255,0.15); padding: 10px; border-radius: 10px; margin-top: 20px; font-size: 0.75rem; font-weight: bold;">
                ⚡ Python & Streamlit Engineers
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    st.info("💡 Το Hub ενημερώνεται αυτόματα μέσω του Admin Panel.")

# 3. FOOTER
st.markdown("---")
st.caption("Does4U Automation System Hub v2.0 | High-ROI Grade Content")