import streamlit as st
import json
import os
from datetime import datetime
from openai import OpenAI
from tavily import TavilyClient

# ==============================================================================
# 🏛️ SETUP & ΑΣΦΑΛΕΙΑ ADMIN
# ==============================================================================
st.set_page_config(page_title="Does4U | Command Center", layout="wide")

# Αρχικοποίηση Clients (Αντικατάστησε τα 'YOUR_KEY' με τα secrets σου ή st.secrets)
# Για ασφάλεια στο Cloud χρησιμοποιούμε st.secrets, αλλιώς βάζεις τα keys σου εδώ για δοκιμή
openai_key = st.secrets.get("OPENAI_API_KEY", "YOUR_OPENAI_KEY")
tavily_key = st.secrets.get("TAVILY_API_KEY", "YOUR_TAVILY_KEY")

client = OpenAI(api_key=openai_key)
tavily = TavilyClient(api_key=tavily_key)

DB_FILE = "blog_data.json"

# ==============================================================================
# 🗺️ ΔΗΜΙΟΥΡΓΙΑ ΚΕΝΤΡΙΚΩΝ TABS (COMMAND CENTER)
# ==============================================================================
admin_tab1, admin_tab2 = st.tabs(["📝 Blog Management", "🏹 Deal Hunter Bot"])

# ==============================================================================
# 🧠 TAB 1: BLOG MANAGEMENT (Tech & Growth)
# ==============================================================================
with admin_tab1:
    st.title("🎯 Does4U Content Pack Generator (Admin Panel)")
    st.write("Δημιουργήστε και εγκρίνετε στρατηγικά άρθρα για το Tech & Growth Blog σας.")


#==================================================
# 🧠 ΜΗΧΑΝΗ ΠΑΡΑΓΩΓΗΣ ΑΡΘΡΩΝ (GROWTH HACKING ONLY)
# =================================================
def generate_strategic_article(category, target):
    # Enterprise Prompt εστιασμένο αποκλειστικά σε Business Automation & Growth
    logic = "Disruptive Growth Hacker & B2B Automation Expert. Focus: Maximum ROI, saving time, and automated lead generation."
    query = f"Growth hacking automation {target} lead generation tools business systems 2026"
    img_path = "blog_images/growth_default.jpg"

    with st.spinner("🕵️‍♂️ Η Does4U αναλύει τις παγκόσμιες πηγές Growth Hacking..."):
        try:
            # Ζωντανή αναζήτηση μέσω Tavily για να πιάσουμε τα πιο hot trends του 2026
            search = tavily.search(query=query, search_depth="advanced", max_results=3)
            
            # Σύνταξη από το GPT-4o με focus στο να «κλείσει» τον πελάτη
            prompt = f"""
            Role: {logic}
            Task: Write a high-converting, premium business article based on this target topic: '{target}'.
            
            STRATEGIC WRITING RULES:
            1. Tone: Authoritative, energetic, and highly professional. Speak directly to Business Owners, Founders, and CEOs.
            2. Language: Greek (Ελληνικά).
            3. NO COMPLICATED CODE: Focus on the business logic, the strategy, and the software tools (e.g., Zapier, Make, HubSpot, AI Agents), NOT raw coding. Do not write complex scripts that can break.
            4. ROI Driven: Explain exactly how much time or money the business owner will save by implementing this.
            
            Structure:
            - Mind-blowing, Premium Title (Focus on growth/automation)
            - The Problem (Why manual work is killing their margins in 2026)
            - The Automated Strategy (Step-by-step how the system works conceptually)
            - Real-World Business Benefits (Time saved, leads generated)
            - High-Ticket Call to Action (CTA): A paragraph urging the reader to book a free automation audit with the Does4U team to build this system for them.
            
            Return the final output in clean, beautifully formatted Markdown.
            """
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": f"You are a master of content marketing. Context from web search: {str(search)}"},
                    {"role": "user", "content": prompt}
                ]
            )
            
            article_content = response.choices[0].message.content
            return article_content, img_path
            
        except Exception as e:
            st.error(f"Σφάλμα κατά την παραγωγή: {e}")
            return None, None

        with st.spinner("🕵️ Η Does4U σκανάρει στοχευμένα τα επίσημα Tech Domains..."):
            try:
                # Ζωντανή αναζήτηση ΜΟΝΟ στα επιλεγμένα domains
                search = tavily.search(
                    query=query, 
                    search_depth="advanced", 
                    max_results=3,
                    include_domains=domains_to_search # 👈 ΕΔΩ ΓΙΝΕΤΑΙ ΤΟ ΜΑΓΙΚΟ!
                )
                
                # Σύνταξη από GPT-4o
                prompt = f"""
                Role: {logic}
                ΘΕΜΑ: {target}
                ΠΡΩΤΟΓΕΝΗ ΔΕΔΟΜΕΝΑ ΑΠΟ ΕΠΙΣΗΜΕΣ ΠΗΓΕΣ: {str(search)}
                
                ΟΔΗΓΙΕΣ:
                1. Γράψε ένα κορυφαίο άρθρο, τουλάχιστον 500 λέξεων, στα ΕΛΛΗΝΙΚΑ.
                2. Βασίσου ΑΥΣΤΗΡΑ στις τεχνικές λεπτομέρειες των δεδομένων. Μίλα για συγκεκριμένα libraries, APIs ή εκδόσεις του 2026.
                3. Μην χρησιμοποιείς AI κλισέ. Μπες κατευθείαν στο ψητό με Markdown (H2, H3, Bullets).
                4. Στο ΤΕΛΟΣ του κειμένου, γράψε ΑΚΡΙΒΩΣ τη λέξη: SPLIT_HERE
                5. Μετά τη λέξη SPLIT_HERE, γράψε ένα social media post (LinkedIn/Reddit) με δυνατά hooks και hashtags.
                """
                
                res = client.chat.completions.create(
                    model="gpt-4o", 
                    messages=[{"role": "system", "content": prompt}]
                )
                full_response = res.choices[0].message.content

                if "SPLIT_HERE" in full_response:
                    parts = full_response.split("SPLIT_HERE")
                    article_body = parts[0].strip()
                    teaser_final = parts[1].strip()
                else:
                    article_body = full_response
                    teaser_final = "🚀 New Tech Deep-Dive Alert on Does4U!"

                return {
                    "title": target,
                    "content": article_body,
                    "teaser": teaser_final,
                    "category": category,
                    "target": target,
                    "date": datetime.now().strftime("%d/%m/%Y"),
                    "image": img_path
                }
            except Exception as e:
                st.error(f"❌ Σφάλμα κατά την παραγωγή: {e}")
                return None

        with st.spinner("🕵️ Η Does4U αναλύει τις παγκόσμιες πηγές..."):
            try:
                # Ζωντανή αναζήτηση
                search = tavily.search(query=query, search_depth="advanced", max_results=3)
                
                # Σύνταξη από GPT-4o
                prompt = f"""
                Role: {logic}
                ΘΕΜΑ: {target}
                ΔΕΔΟΜΕΝΑ: {str(search)}
                
                ΟΔΗΓΙΕΣ:
                1. Γράψε ένα κορυφαίο άρθρο, τουλάχιστον 500 λέξεων, στα ΕΛΛΗΝΙΚΑ.
                2. Μην χρησιμοποιείς AI κλισέ. Μπες κατευθείαν στο ψητό με Markdown (H2, H3, Bullets).
                3. Στο ΤΕΛΟΣ του κειμένου, γράψε ΑΚΡΙΒΩΣ τη λέξη: SPLIT_HERE
                4. Μετά τη λέξη SPLIT_HERE, γράψε ένα social media post (LinkedIn/Reddit) με δυνατά hooks και hashtags.
                """
                
                res = client.chat.completions.create(
                    model="gpt-4o", 
                    messages=[{"role": "system", "content": prompt}]
                )
                full_response = res.choices[0].message.content

                if "SPLIT_HERE" in full_response:
                    parts = full_response.split("SPLIT_HERE")
                    article_body = parts[0].strip()
                    teaser_final = parts[1].strip()
                else:
                    article_body = full_response
                    teaser_final = "🚀 New Article Alert on Does4U!"

                return {
                    "title": target,
                    "content": article_body,
                    "teaser": teaser_final,
                    "category": category,
                    "target": target,
                    "date": datetime.now().strftime("%d/%m/%Y"),
                    "image": img_path
                }
            except Exception as e:
                st.error(f"❌ Σφάλμα κατά την παραγωγή: {e}")
                return None

    # UI για το Blog Generator
    st.markdown("### 🛠️ Ρύθμιση Νέου Άρθρου")
    col_cat, col_tar = st.columns(2)
    with col_cat:
        category = st.radio("🗂️ Επιλέξτε Κατηγορία:", ["💻 Python & AI Updates", "📈 Growth Hacking"])
    with col_tar:
        target = st.text_input("🎯 Στόχος / Θέμα Άρθρου:", placeholder="π.χ. How to scrape LinkedIn without getting banned")

    if st.button("🚀 Έναρξη Έρευνας & Συγγραφής", use_container_width=True):
        if target:
            generated_data = generate_strategic_article(category, target)
            if generated_data:
                st.session_state['draft_article'] = generated_data
                st.success("🎉 Το Draft δημιουργήθηκε με επιτυχία!")
        else:
            st.warning("Παρακαλώ συμπληρώστε ένα θέμα.")

    # Εμφάνιση Draft & Έγκριση
    if 'draft_article' in st.session_state:
        draft = st.session_state['draft_article']
        st.markdown("---")
        st.subheader("📝 Προεπισκόπηση Draft Άρθρου")
        
        tab_preview, tab_social = st.tabs(["📖 Κείμενο Άρθρου", "📱 Social Media Teaser"])
        with tab_preview:
            st.markdown(f"**Τίτλος:** {draft['title']}")
            st.markdown(draft['content'])
        with tab_social:
            st.code(draft['teaser'])

        # Κουμπί Δημοσίευσης
        if st.button("✅ Έγκριση & Live Δημοσίευση", type="primary", use_container_width=True):
            posts = []
            if os.path.exists(DB_FILE):
                with open(DB_FILE, "r", encoding="utf-8") as f:
                    try: posts = json.load(f)
                    except: posts = []
            
            posts.insert(0, draft) # Προσθήκη στην αρχή
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(posts, f, ensure_ascii=False, indent=4)
                
            st.success("🚀 Το άρθρο δημοσιεύτηκε live στο Blog! Καθάρισμα draft...")
            del st.session_state['draft_article']

# ==============================================================================
# 🏹 TAB 2: DEAL HUNTER BOT (The Core Machine)
# ==============================================================================
with admin_tab2:
    st.title("🏹 Deal Hunter Bot")
    st.write("Σκανάρισμα της αγοράς σε πραγματικό χρόνο για leads, projects και ευκαιρίες αυτοματοποίησης.")

    # 1. Configuration Panel του Bot
    st.markdown("### ⚙️ Ραντάρ Αναζήτησης")
    col_source, col_keyword = st.columns(2)
    with col_source:
        platform = st.multiselect("🌐 Πηγές Σκαναρίσματος:", ["Reddit", "LinkedIn (Soon)", "Upwork (Soon)"], default=["Reddit"])
    with col_keyword:
        keywords = st.text_input("🔑 Λέξεις-Κλειδιά (χωρισμένες με κόμμα):", value="web scraping, python script, automate business, ai agent")

    # 2. Reddit API Credentials Check
    st.sidebar.markdown("### 🔑 Deal Hunter API Keys")
    reddit_client = st.sidebar.text_input("Reddit Client ID", type="password")
    reddit_secret = st.sidebar.text_input("Reddit Client Secret", type="password")

    # 3. Action Button
    if st.button("🔍 Έναρξη Σκαναρίσματος Αγοράς", type="primary", use_container_width=True):
        st.info("🛰️ Το ραντάρ ενεργοποιείται... Αναζήτηση για πελάτες που χρειάζονται Python & AI Automations.")
        
        # Εδώ θα μπει η συνάρτηση fetch_reddit_deals(keywords) στο επόμενο βήμα!
        st.warning("⚠️ Εκκρεμεί η σύνδεση των Reddit Keys για να τραβήξουμε live posts.")
        
        # Mock Data για να δεις το UI πώς θα εμφανίζει τα αποτελέσματα
        st.markdown("### 📊 Πρόσφατα Ευρήματα (Δείγμα)")
        mock_leads = [
            {"title": "Need a python script to scrape property data daily", "source": "r/PythonJobs", "user": "dev_hunter99", "link": "#"},
            {"title": "Looking for an AI automation expert to integrate OpenAI with our CRM", "source": "r/Automate", "user": "biz_owner_2026", "link": "#"}
        ]
        for lead in mock_leads:
            with st.expander(f"📌 {lead['title']} [{lead['source']}]"):
                st.write(f"**Χρήστης:** {lead['user']}")
                st.write("🤖 **Προτεινόμενο AI Pitch (Does4U):**")
                st.code(f"Hey {lead['user']}, I'm a SaaS Engineer specialized in exactly this. I can build a stable automation in Python that runs 24/7 on Streamlit Cloud...")
                st.link_button("🔗 Άνοιγμα Post", lead['link'])