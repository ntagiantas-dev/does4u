import streamlit as st
import json
import os

# ==============================================================================
# 🏛️ ΡΥΘΜΙΣΗ ΣΕΛΙΔΑΣ & PREMIUM DESIGN
# ==============================================================================
st.set_page_config(
    page_title="Does4U | SaaS Engineering & AI Automations",
    page_icon="⚡",
    layout="wide"
)

# Custom CSS για καθαρή, επαγγελματική business εμφάνιση
st.markdown("""
    <style>
    .hero-title { font-size: 3rem !important; font-weight: 800 !important; color: #1E3A8A; text-align: center; margin-bottom: 0.5rem; }
    .hero-subtitle { font-size: 1.4rem !important; color: #4B5563; text-align: center; margin-bottom: 2.5rem; }
    .card-title { font-size: 1.4rem !important; font-weight: 700 !important; color: #1E3A8A; margin-bottom: 0.5rem; }
    .result-card { background-color: #F3F4F6; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; border-left: 5px solid #1E3A8A; }
    .blog-title { font-size: 1.8rem !important; font-weight: 700 !important; color: #1E3A8A; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 🗺️ ΔΗΜΙΟΥΡΓΙΑ ΚΑΡΤΕΛΩΝ (TABS)
# ==============================================================================
main_tab1, main_tab2 = st.tabs(["⚡ Does4U | Agency", "📝 Insight Blog"])

# ==============================================================================
# 🚀 ΚΑΡΤΕΛΑ 1: LANDING PAGE (SaaS & AI Automations - ROI Focused)
# ==============================================================================
with main_tab1:
    st.markdown('<h1 class="hero-title">Stop Wasting Hours. Automate Your Business with Custom AI & SaaS Solutions.</h1>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Σχεδιάζω και υλοποιώ αυτόνομα AI Agents, έξυπνα Web Scraping συστήματα και custom SaaS εφαρμογές που τρέχουν 24/7 για να φέρνουν πελάτες και δεδομένα στο πιάτο σου.</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Τα 3 Βασικά Pillars των Υπηρεσιών σου
    st.markdown("## 🛠️ High-ROI Services")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<p class="card-title">🤖 AI Agents & Automations</p>', unsafe_allow_html=True)
        st.write("""
        Αντικαταστήστε τις χειροκίνητες, επαναλαμβανόμενες διαδικασίες με έξυπνα, αυτόνομα bots. 
        Σύνδεση με OpenAI API, Tavily Live Data και αυτοματοποίηση καθημερινών tasks.
        """)
        st.caption("**Αποτέλεσμα:** Μείωση λειτουργικού χρόνου έως και 80%.")
        
    with col2:
        st.markdown('<p class="card-title">🔍 Advanced Web Scraping</p>', unsafe_allow_html=True)
        st.write("""
        Έξυπνη και γρήγορη συλλογή δεδομένων από 'δύσκολα' οικοσυστήματα (LinkedIn, Reddit, Telegram). 
        Μετατρέπουμε το χάος του διαδικτύου σε καθαρά leads και market intelligence.
        """)
        st.caption("**Αποτέλεσμα:** Live δεδομένα ανταγωνιστών απευθείας στο CRM σας.")
        
    with col3:
        st.markdown('<p class="card-title">🚀 Custom SaaS Development</p>', unsafe_allow_html=True)
        st.write("""
        Μετατρέπουμε την επιχειρηματική σας ιδέα σε λειτουργικό MVP (Minimum Viable Product) σε χρόνο μηδέν. 
        Σταθερές εφαρμογές σε Python & Streamlit έτοιμες για scaling.
        """)
        st.caption("**Αποτέλεσμα:** Γρήγορο deployment στην αγορά με το ελάχιστο κόστος.")
        
    st.markdown("---")
    
    # Section για τα μελλοντικά σου έργα / Case Studies (Εδώ θα μπει ο Deal Hunter!)
    st.markdown("## 📂 Our Case Studies & Live Tools")
    st.info("🎯 **Coming Soon:** Live επίδειξη του 'Deal Hunter Bot' — Πώς αυτοματοποιήσαμε το δικό μας lead generation σε LinkedIn & Reddit χρησιμοποιώντας Python και LLMs.")

# ==============================================================================
# 📝 ΚΑΡΤΕΛΑ 2: TO LIVE BLOG (Διαβάζει από το blog_data.json)
# ==============================================================================
with main_tab2:
    st.markdown("## 📝 The Does4U Insight Blog")
    st.write("Στρατηγική γνώση γύρω από την τεχνολογία και την ανάπτυξη επιχειρήσεων.")
    
    # Φόρτωση των δημοσιευμένων άρθρων
    DB_FILE = "blog_data.json"
    blog_posts = []
    
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try:
                blog_posts = json.load(f)
            except:
                blog_posts = []
                
    if not blog_posts:
        st.info("📚 Το blog προετοιμάζεται! Σύντομα θα αναρτηθούν τα πρώτα άρθρα Growth Hacking και Tech Updates.")
    else:
        # Φίλτρο κατηγοριών για τον επισκέπτη
        categories = ["Όλα τα άρθρα", "💻 Python & AI Updates", "📈 Growth Hacking"]
        selected_filter = st.selectbox("🎯 Φιλτράρισμα ανά κατηγορία:", categories)
        
        st.markdown("---")
        
        # Εμφάνιση των άρθρων με βάση το φίλτρο
        for post in blog_posts:
            # Έλεγχος αν το άρθρο ταιριάζει στο φίλτρο
            if selected_filter != "Όλα τα άρθρα" and post.get("category") != selected_filter:
                continue
                
            # Στήσιμο του άρθρου στην οθόνη
            with st.container():
                st.markdown(f'<p class="blog-title">{post["title"]}</p>', unsafe_allow_html=True)
                st.caption(f"📅 Δημοσιεύτηκε: {post['date']} | 🗂️ Κατηγορία: {post.get('category', 'Γενικά')}")
                
                # Εμφάνιση κειμένου (χρησιμοποιούμε expander για να μην πιάνει όλη την οθόνη αν είναι μεγάλο)
                with st.expander("📖 Διαβάστε το πλήρες άρθρο"):
                    st.markdown(post["content"])
                    
                st.markdown("<br>", unsafe_allow_html=True)