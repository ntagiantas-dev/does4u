#===============================================================
#== 🏛️ ΕΝΟΤΗΤΑ 1: Εισαγωγή Εργαλείων, Κλειδιά & Ρυθμίσεις Φακέλων
#=================================================================
import streamlit as st
import requests
import json
import os
import time
from openai import OpenAI
from tavily import TavilyClient
from datetime import datetime
from dotenv import load_dotenv
from dash import show_promo_dashboard

# 1. Φόρτωση των μυστικών κλειδιών (API Keys)
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# 2. Ρύθμιση του τίτλου και του εικονιδίου στο tab του Browser
st.set_page_config(
    page_title="Does4U | Strategic Admin",
    page_icon="🏛️",
    layout="wide"
)

# 3. Δημιουργία τοπικού φακέλου για την αποθήκευση των εικόνων του Blog
IMAGE_DIR = "blog_images"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# 4. Ορισμός των αρχείων-"αποθηκών" όπου γράφονται τα άρθρα και τα πρόχειρα
DB_FILE = "blog_data.json"
DRAFTS_FILE = "drafts_data.json"

# 5. Λειτουργία για το αυτόματο κατέβασμα και αποθήκευση της εικόνας
def download_image(image_url):
    """Κατεβάζει την εικόνα από την OpenAI και την σώζει μόνιμα τοπικά"""
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{IMAGE_DIR}/img_{timestamp}.png"
            with open(filename, "wb") as f:
                f.write(response.content)
            return filename
    except Exception as e:
        st.error(f"Σφάλμα αποθήκευσης εικόνας: {e}")
    return None
#===========================================================
#== 💾 ΕΝΟΤΗΤΑ 2: Η Λογική της "Αποθήκης" (Μέγιστο 30 Άρθρα)
#===========================================================
# Αρχικοποίηση της μνήμης των πρόχειρων αν είναι άδεια
if "single_drafts" not in st.session_state:
    st.session_state.single_drafts = []

def save_to_blog(data):
    """Αποθηκεύει οριστικά το άρθρο - Κρατάει τα τελευταία 30"""
    posts = []
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try:
                posts = json.load(f)
            except:
                posts = []
    
    posts.insert(0, data) # Τοποθέτηση στην αρχή της λίστας (πρώτο)
    posts = posts[:30]    # Κόψιμο στα 30 άρθρα μέγιστο
    
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=4)

def save_drafts_permanently(drafts_list):
    """Σώζει τα πρόχειρα (Drafts) στο αρχείο - Κρατάει τα τελευταία 30"""
    with open(DRAFTS_FILE, "w", encoding="utf-8") as f:
        json.dump(drafts_list[:30], f, ensure_ascii=False, indent=4)

def load_permanent_drafts():
    """Φορτώνει τα αποθηκευμένα πρόχειρα κατά την εκκίνηση του Admin"""
    if os.path.exists(DRAFTS_FILE):
        with open(DRAFTS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []
#==============================================================
#== 🧠 ΕΝΟΤΗΤΑ 3: Η Μηχανή Παραγωγής Άρθρων (AI & Live Search)
#==============================================================
def generate_strategic_article(category, target):
    # 1. Επιλογή προσωπικότητας AI και στοχευμένης αναζήτησης ανάλογα με την κατηγορία
    if category == "ΦΕΚ":
        logic = "Senior Legal Analyst. Focus: Deep Analysis και προθεσμίες."
        query = f"site:et.gr '{target}' απόφαση 2026"
    elif category == "ΒΟΥΛΗ":
        logic = "Policy Strategist. Focus: Τι αλλάζει για τον επαγγελματία."
        query = f"site:hellenicparliament.gr '{target}' νομοσχέδιο 2026"
    else:
        logic = "Business Strategist. Focus: ESG, CSRD και αγορά."
        query = f"(site:capital.gr OR site:naftemporiki.gr) '{target}' 2026"

    with st.spinner("🕵️ Η Does4U αναλύει το θέμα..."):
        try:
            # Α. Ζωντανή αναζήτηση πηγών στο διαδίκτυο
            search = tavily.search(query=query, search_depth="advanced", max_results=3)
            
            # Β. Σύνταξη κειμένου από το GPT-4o
            prompt = f"""
            Role: {logic}
            ΘΕΜΑ: {target}
            ΔΕΔΟΜΕΝΑ: {str(search)}
            
            ΟΔΗΓΙΕΣ:
            1. Γράψε ένα άρθρο 500 λέξεων στα Ελληνικά.
            2. Στο ΤΕΛΟΣ του κειμένου, γράψε ΑΚΡΙΒΩΣ τη λέξη: SPLIT_HERE
            3. Medά τη λέξη SPLIT_HERE, γράψε ένα social media post.
            """
            
            res = client.chat.completions.create(
                model="gpt-4o", 
                messages=[{"role": "system", "content": prompt}]
            )
            full_response = res.choices[0].message.content

            # Γ. Διαχωρισμός του άρθρου από το Social Media Post
            if "SPLIT_HERE" in full_response:
                parts = full_response.split("SPLIT_HERE")
                article_body = parts[0].strip()
                teaser_final = parts[1].strip()
            else:
                article_body = full_response
                teaser_final = "Δείτε το πλήρες άρθρο στο blog μας!"

            # Δ. Απόδοση της κατάλληλης προκαθορισμένης εικόνας background
            if category == "ΦΕΚ":
                img_path = "blog_images/fek_default.jpg"
            elif category == "ΒΟΥΛΗ":
                img_path = "blog_images/parliament_default.jpg"
            else:
                img_path = "blog_images/business_default.jpg"

            # Ε. Επιστροφή όλων των στοιχείων πακέτο
            return {
                "title": target,
                "content": article_body.strip(),
                "teaser": teaser_final.strip(),
                "category": category,
                "target": target,
                "date": datetime.now().strftime("%d/%m/%Y"),
                "image": img_path,
                "sources": [r['url'] for r in search['results']] if 'results' in search else []
            }

        except Exception as e:
            st.error(f"❌ Σφάλμα κατά την παραγωγή: {e}")
            return None
#===================================================
#== 🚀 ΕΝΟΤΗΤΑ 4: Η Λειτουργία Οριστικής Δημοσίευσης
#===================================================
def handle_publish(draft_data, index):
    """Μεταφέρει το άρθρο από τα Drafts στο οριστικό Blog με τις πηγές"""
    
    final_content = draft_data["content"]
    
    # Αν υπάρχουν πηγές, τις προσθέτουμε με όμορφη μορφή στο τέλος του άρθρου
    if draft_data.get("sources"):
        final_content += "\n\n---\n### 🔗 Πηγές & Αναφορές:\n"
        for source in draft_data["sources"]:
            final_content += f"- {source}\n"
    
    # Κατασκευή του τελικού αντικειμένου Blog Post
    blog_post = {
        "title": draft_data["title"],
        "content": final_content,
        "image": draft_data["image"],
        "date": draft_data["date"],
        "category": draft_data["category"],
        "teaser": draft_data["teaser"]
    }
    
    # 1. Οριστική αποθήκευση στο blog_data.json
    save_to_blog(blog_post)
    
    # 2. Αφαίρεση του άρθρου από τη λίστα των πρόχειρων
    try:
        saved_drafts = load_permanent_drafts()
        if index < len(saved_drafts):
            saved_drafts.pop(index)
            save_drafts_permanently(saved_drafts)
    except:
        pass
    
    st.success("🚀 Το άρθρο δημοσιεύτηκε με επιτυχία μαζί με τις πηγές του!")
    time.sleep(1)
    st.rerun()
#=======================================================
#== 🎛️ ΕΝΟΤΗΤΑ 5: Το Πλευρικό Μενού (Sidebar Navigation)
#=======================================================
with st.sidebar:
    # 1. Εμφάνιση Λογοτύπου και Έκδοσης
    try:
        st.image("does4u_logo.png", caption="Does4U Admin v2.0")
    except:
        st.caption("Does4U Admin v2.0")
        
    st.title("🏛️ Στρατηγείο Διαχείρισης")
    st.divider()
    
    # 2. Το μενού επιλογής σελίδας
    admin_page = st.radio(
        "Πλοήγηση", 
        ["📝 Παραγωγή Blog", "🔑 Διαχείριση Promo Codes"]
    )
    st.divider()
#=====================================================
#== 📺 ΕΝΟΤΗΤΑ 6: Η Κύρια Οθόνη & Η Λογική Ανά Σελίδα
#=====================================================
# --- ΠΕΡΙΠΤΩΣΗ 1: ΣΕΛΙΔΑ ΠΑΡΑΓΩΓΗΣ BLOG ---
if admin_page == "📝 Παραγωγή Blog":
    
    # Προσθήκη των εργαλείων δημιουργίας στο sidebar
    with st.sidebar:
        st.subheader("🚀 Κέντρο Παραγωγής Blog")
        category = st.selectbox("Επίλεξε Κατηγορία", ["ΦΕΚ", "Βουλή", "Επιχειρηματικότητα"])
        target_point = st.text_area(
            "Τι ψάχνουμε; (Target Point)", 
            placeholder="π.χ. Νέες επιδοτήσεις για τουρισμό 2026"
        )
        
        if st.button("✨ ΔΗΜΙΟΥΡΓΙΑ ΑΡΘΡΟΥ", use_container_width=True):
            if not target_point:
                st.warning("⚠️ Πρώτα γράψε ένα θέμα στο παραπάνω πλαίσιο!")
            else:
                article_data = generate_strategic_article(category, target_point)
                if article_data:
                    st.session_state['latest_article'] = article_data
                    # Προσθήκη στα υπάρχοντα πρόχειρα
                    current_drafts = load_permanent_drafts()
                    current_drafts.insert(0, article_data)
                    save_drafts_permanently(current_drafts)
                    st.success("✅ Το άρθρο ολοκληρώθηκε!")

    # --- ΚΕΝΤΡΙΚΗ ΟΘΟΝΗ: ΕΜΦΑΝΙΣΗ ΜΟΛΙΣ ΠΑΡΑΧΘΕΝΤΟΣ ΑΡΘΡΟΥ ---
    if 'latest_article' in st.session_state:
        art = st.session_state['latest_article']
        st.divider()
        st.header(art['title'])
        st.markdown(art['content'])
        
        # Εμφάνιση των πηγών που βρήκε το Google Search
        if art.get('sources'):
            st.subheader("🔗 Πηγές & Αναφορές")
            for src in art['sources']:
                st.write(f"• {src}")

        # Εμφάνιση του έτοιμου κειμένου για Social Media
        st.subheader("📱 Teaser για Social Media")
        st.info(art.get('teaser', 'Δείτε το πλήρες άρθρο στο blog μας!'))

    # --- ΚΑΤΩ ΜΕΡΟΣ: ΛΙΣΤΑ ΜΕ ΤΑ ΑΠΟΘΗΚΕΥΜΕΝΑ ΠΡΟΧΕΙΡΑ ---
    st.divider()
    st.subheader("📝 Πρόχειρα Άρθρα προς Επιμέλεια")
    saved_drafts = load_permanent_drafts()

    if saved_drafts:
        for idx, d in enumerate(saved_drafts):
            # Δημιουργία ακορντεόν (expander) για κάθε πρόχειρο άρθρο
            with st.expander(f"📂 {d.get('date', '---')} - {d.get('title', 'Χωρίς Τίτλο')} ({d.get('category', 'Γενικό')})"):
                st.markdown(d['content'])
                
                # Εμφάνιση των links των πηγών ως clickable συνδέσμους
                if d.get('sources'):
                    st.write("**🔗 Πηγές & Σύνδεσμοι:**")
                    for s in d['sources']:
                        st.markdown(f"• 🌐 [{s}]({s})")
                
                # Κουμπί για οριστικό ανέβασμα στο site
                if st.button(f"🚀 ΔΗΜΟΣΙΕΥΣΗ ΣΤΟ BLOG", key=f"pub_{idx}"):
                    handle_publish(d, idx)

        # Κουμπί ολικής διαγραφής των πρόχειρων
        st.write("")
        if st.button("🗑️ ΚΑΘΑΡΙΣΜΟΣ ΟΛΩΝ ΤΩΝ DRAFTS", use_container_width=True):
            with open(DRAFTS_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)
            st.rerun()
    else:
        st.info("Δεν υπάρχουν άρθρα στη λίστα αναμονής.")

# --- ΠΕΡΙΠΤΩΣΗ 2: ΣΕΛΙΔΑ ΔΙΑΧΕΙΡΙΣΗΣ ΚΩΔΙΚΩΝ ---
elif admin_page == "🔑 Διαχείριση Promo Codes":
    # Φορτώνει απευθείας το dashboard από το αρχείο dash.py
    show_promo_dashboard()
        