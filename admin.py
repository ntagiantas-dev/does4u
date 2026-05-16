# ==========================================================
# SECTION 1: SETUP, KEYS & DIRECTORIES
# ==========================================================
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


# Φόρτωση κλειδιών
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Ρύθμιση Σελίδας
st.set_page_config(
    page_title="Does4U | Strategic Admin",
    page_icon="🏛️",
    layout="wide"
)

# Δημιουργία φακέλου για τις εικόνες (για να μην λήγουν της DALL-E)
IMAGE_DIR = "blog_images"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# Αρχεία Βάσης
DB_FILE = "blog_data.json"
DRAFTS_FILE = "drafts_data.json"

# --- ΣΥΝΑΡΤΗΣΗ ΓΙΑ ΤΟΠΙΚΗ ΑΠΟΘΗΚΕΥΣΗ ΕΙΚΟΝΑΣ ---
def download_image(image_url):
    """Κατεβάζει την εικόνα από την OpenAI και την σώζει μόνιμα τοπικά"""
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{IMAGE_DIR}/img_{timestamp}.png"
            with open(filename, "wb") as f:
                f.write(response.content)
            return filename # Επιστρέφει το τοπικό μονοπάτι
    except Exception as e:
        st.error(f"Σφάλμα αποθήκευσης εικόνας: {e}")
    return None
# ==========================================================
# SECTION 2: DATABASE LOGIC (MAX 30 POSTS)
# ==========================================================
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
    
    posts.insert(0, data) # Το βάζει πρώτο (πιο πρόσφατο)
    posts = posts[:30]    # ΚΡΑΤΑΕΙ ΜΟΝΟ ΤΑ 30 ΤΕΛΕΥΤΑΙΑ
    
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=4)

def save_drafts_permanently(drafts_list):
    """Σώζει τα πρόχειρα (Drafts) - Κρατάει τα τελευταία 30"""
    with open(DRAFTS_FILE, "w", encoding="utf-8") as f:
        json.dump(drafts_list[:30], f, ensure_ascii=False, indent=4)

def load_permanent_drafts():
    """Φορτώνει τα drafts κατά την εκκίνηση"""
    if os.path.exists(DRAFTS_FILE):
        with open(DRAFTS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []
#==============================================================
# SECTION 3: ΣΥΝΑΤΗΣΗ ΠΑΡΑΓΩΓΗΣ (LOGIC & AI)
#==============================================================
def generate_strategic_article(category, target):
    # 1. Λογική ανά κατηγορία
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
            # Α. Αναζήτηση
            search = tavily.search(query=query, search_depth="advanced", max_results=3)
            
            # --- Β. ΠΑΡΑΓΩΓΗ ΚΕΙΜΕΝΟΥ ---
            prompt = f"""
            Role: {logic}
            ΘΕΜΑ: {target}
            ΔΕΔΟΜΕΝΑ: {str(search)}
            
            ΟΔΗΓΙΕΣ:
            1. Γράψε ένα άρθρο 500 λέξεων στα Ελληνικά.
            2. Στο ΤΕΛΟΣ του κειμένου, γράψε ΑΚΡΙΒΩΣ τη λέξη: SPLIT_HERE
            3. Μετά τη λέξη SPLIT_HERE, γράψε ένα social media post.
            """
            
            res = client.chat.completions.create(
                model="gpt-4o", 
                messages=[{"role": "system", "content": prompt}]
            )
            full_response = res.choices[0].message.content

            # ΔΙΑΧΩΡΙΣΜΟΣ 
            if "SPLIT_HERE" in full_response:
                parts = full_response.split("SPLIT_HERE")
                article_body = parts[0].strip()
                teaser_final = parts[1].strip()
            else:
                article_body = full_response
                teaser_final = "Δείτε το πλήρες άρθρο στο blog μας!"

            # --- Γ. ΕΠΙΛΟΓΗ ΕΙΚΟΝΑΣ ---
            if category == "ΦΕΚ":
                img_path = "blog_images/fek_default.jpg"
            elif category == "ΒΟΥΛΗ":
                img_path = "blog_images/parliament_default.jpg"
            else:
                img_path = "blog_images/business_default.jpg"

            # --- Δ. ΕΠΙΣΤΡΟΦΗ ΔΕΔΟΜΕΝΩΝ (ΠΡΟΣΟΧΗ: ΧΩΡΙΣ ΜΕΤΑΦΡΑΣΜΕΝΕΣ ΕΝΤΟΛΕΣ) ---
            return {
                "title": target,
                "content": article_body.strip(),
                "teaser": teaser_final.strip(),
                "category": category,
                "target": target,
                "date": datetime.now().strftime("%d/%m/%Y"),
                "image": img_path,
                "sources": [res['url'] for res in search] if isinstance(search, list) else []
            }
            

        except Exception as e:
            st.error(f"❌ Σφάλμα: {e}")
            return None
# ==========================================================
# SECTION 4: ΔΗΜΟΣΙΕΥΣΗ ΣΤΟ BLOG (FINAL ACTION)
# ==========================================================

def handle_publish(draft_data, index):
    """Μεταφέρει το άρθρο από τα Drafts στο οριστικό Blog με τις πηγές"""
    
    # Φτιάχνουμε το τελικό κείμενο που θα βλέπει ο αναγνώστης
    # Προσθέτουμε τις πηγές στο τέλος του content
    final_content = draft_data["content"]
    
    if draft_data.get("sources"):
        final_content += "\n\n---\n### 🔗 Πηγές & Αναφορές:\n"
        for source in draft_data["sources"]:
            final_content += f"- {source}\n"
    
    # Δημιουργούμε το τελικό αντικείμενο προς αποθήκευση
    blog_post = {
        "title": draft_data["title"],
        "content": final_content, # Το άρθρο ΜΑΖΙ με τις πηγές
        "image": draft_data["image"],
        "date": draft_data["date"],
        "category": draft_data["category"],
        "teaser": draft_data["teaser"] # Το teaser μένει ξεχωριστό πεδίο
    }
    
    # 1. Αποθήκευση στο blog_data.json
    save_to_blog(blog_post)
    
    # 2. Αφαίρεση από τα drafts
    st.session_state.single_drafts.pop(index)
    save_drafts_permanently(st.session_state.single_drafts)
    
    st.success("🚀 Το άρθρο δημοσιεύτηκε με επιτυχία μαζί με τις πηγές του!")
    time.sleep(1)
    st.rerun()
# ==========================================================
# SECTION 5: ΠΛΕΥΡΙΚΟ ΜΕΝΟΥ (SIDEBAR NAVIGATION)
# ==========================================================
with st.sidebar:
    st.image("does4u_logo.png", caption="Does4U Admin v2.0")
    st.title("🏛️ Στρατηγείο Διαχείρισης")
    st.divider()
    
    # ΕΔΩ ΕΙΝΑΙ ΤΟ ΜΕΝΟΥ ΠΟΥ ΑΛΛΑΖΕΙ ΤΙΣ ΣΕΛΙΔΕΣ!
    admin_page = st.radio(
        "Πλοήγηση", 
        ["📝 Παραγωγή Blog", "🔑 Διαχείριση Promo Codes"]
    )
    st.divider()
    # ==========================================================
# SECTION 6: ΛΟΓΙΚΗ ΕΜΦΑΝΙΣΗΣ ΑΝΑ ΣΕΛΙΔΑ
# ==========================================================

# --- ΚΑΡΤΕΛΑ 1: ΠΑΡΑΓΩΓΗ BLOG ---
if admin_page == "📝 Παραγωγή Blog":
    
    # Ξαναχτίζουμε τα πεδία του Blog στο sidebar μόνο για αυτή τη σελίδα
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
                    save_drafts_permanently([article_data])
                    st.success("✅ Το άρθρο ολοκληρώθηκε!")

    # --- DISPLAY AREA (Κύρια Οθόνη Blog) ---
    if 'latest_article' in st.session_state:
        art = st.session_state['latest_article']
        st.divider()
        st.header(art['title'])
        st.markdown(art['content'])
        
        if art.get('sources'):
            st.subheader("🔗 Πηγές & Αναφορές")
            for src in art['sources']:
                st.write(f"• {src}")

        st.subheader("📱 Teaser για Social Media")
        st.info(art.get('teaser', 'Δείτε το πλήρες άρθρο στο blog μας!'))

        if st.button("📥 Αποθήκευση στα Πρόχειρα (Drafts)"):
            save_drafts_permanently([art])
            st.success("Το άρθρο σώθηκε στη λίστα παρακάτω!")

    st.divider()
    st.subheader("📝 Πρόχειρα Άρθρα προς Επιμέλεια")
    saved_drafts = load_permanent_drafts()

    if saved_drafts:
        for idx, d in enumerate(saved_drafts):
            with st.expander(f"📂 {d.get('date', '---')} - {d.get('title', 'Χωρίς Τίτλο')}"):
                st.markdown(d['content'])
                
                # Εμφάνιση Clickable Links για τις πηγές
                if d.get('sources'):
                    st.write("**🔗 Πηγές & Σύνδεσμοι:**")
                    sources_data = d['sources']
                    if isinstance(sources_data, list):
                        for s in sources_data:
                            if str(s).startswith("http"):
                                st.markdown(f"• 🌐 [{s}]({s})")
                            else:
                                st.markdown(f"• 📄 {s}")
                    else:
                        st.write(sources_data)
                
                if st.button(f"🚀 ΔΗΜΟΣΙΕΥΣΗ ΣΤΟ BLOG", key=f"pub_{idx}"):
                    handle_publish(d, idx)
                    st.success("ΤΟ ΑΡΘΡΟ ΑΝΕΒΗΚΕ ΟΡΙΣΤΙΚΑ!")
                    st.rerun()

        if st.button("🗑️ ΚΑΘΑΡΙΣΜΟΣ ΟΛΩΝ ΤΩΝ DRAFTS"):
            with open(DRAFTS_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)
            st.rerun()
    else:
        st.info("Δεν υπάρχουν άρθρα στη λίστα αναμονής.")

# --- ΚΑΡΤΕΛΑ 2: ΔΙΑΧΕΙΡΙΣΗ PROMO CODES ---
elif admin_page == "🔑 Διαχείριση Promo Codes":
    # Η κύρια οθόνη αδειάζει και καλεί το dashboard από το dash.py
    show_promo_dashboard()