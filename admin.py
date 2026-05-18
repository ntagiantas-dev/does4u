import os
import json
from datetime import datetime
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI
from tavily import TavilyClient

# 1. SETUP & ΑΣΦΑΛΕΙΑ ΚΛΕΙΔΙΩΝ
load_dotenv()
openai_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
tavily_key = st.secrets.get("TAVILY_API_KEY", os.getenv("TAVILY_API_KEY"))

client = OpenAI(api_key=openai_key)
tavily = TavilyClient(api_key=tavily_key)

st.set_page_config(page_title="Does4U | Command Center", page_icon="⚡", layout="wide")

# ==========================================
# 🎛️ ΔΙΑΧΕΙΡΙΣΗ TABS (COMMAND CENTER)
# ==========================================
admin_tab1, admin_tab2 = st.tabs(["📝 Blog Management", "🏹 Deal Hunter Bot"])

# ==========================================
# TAB 1: BLOG MANAGEMENT (GROWTH HACKING)
# ==========================================
with admin_tab1:
    st.title("🎯 Does4U Content Pack Generator")
    st.write("Δημιουργήστε και εγκρίνετε στρατηγικά άρθρα για το Growth Blog σας.")
    
    # 🧠 Hybrid OpenAI Engine (Mini Filter + Main Writer)
    def generate_strategic_article(category, target):
        query = f"Growth hacking automation {target} lead generation tools business systems 2026"
        img_path = "blog_images/growth_default.jpg"

        # ΣΤΑΘΜΟΣ 1: Live Έρευνα με Tavily
        with st.spinner("🕵️‍♂️ Το Tavily «χτενίζει» το διαδίκτυο για live πηγές του 2026..."):
            try:
                search_results = tavily.search(query=query, search_depth="advanced", max_results=3)
            except Exception as e:
                st.error(f"Σφάλμα Tavily Search: {e}")
                return None, None

        # ΣΤΑΘΜΟΣ 2: Φιλτράρισμα & Data Extraction από το GPT-4o Mini
        with st.spinner("🧠 το GPT-4o mini καθαρίζει τα δεδομένα και απομονώνει τα core facts..."):
            try:
                filter_prompt = f"""
                Analyze these raw search results about '{target}'. 
                Extract ONLY the most relevant automation tools, integration workflows, and specific business benchmarks.
                Remove all marketing fluff, duplicates, or irrelevant text.
                
                Raw Data: {str(search_results)}
                """
                filter_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": filter_prompt}]
                )
                clean_knowledge_pack = filter_response.choices[0].message.content
            except Exception as e:
                st.error(f"Σφάλμα GPT-4o-mini: {e}")
                return None, None

        # ΣΤΑΘΜΟΣ 3: Premium SEO Συγγραφή από το μεγάλο GPT-4o
        with st.spinner("✍️ Το GPT-4o συνθέτει το premium SEO άρθρο..."):
            try:
                seo_prompt = f"""
                Role: Senior B2B SEO Copywriter & Growth Automation Strategist.
                Task: Write a deep, value-first, SEO-optimized blog article in Greek based on this target topic: '{target}'.
                Use this clean knowledge pack for your facts: {clean_knowledge_pack}
                
                CRITICAL SEO & CONTENT RULES:
                1. STRICTLY NO EMAIL FORMATTING: Do NOT include greetings (e.g., 'Αγαπητοί Επιχειρηματίες'), do NOT write in a letter format, and do NOT use sign-offs/placeholders (e.g., 'Με σεβασμό', '[Το Όνομά σας]'). Write strictly as a website blog post.
                2. VALUE-FIRST: Focus 80% on actionable strategies, workflow logic, and real tool benchmarks (Zapier, Make, HubSpot), and only 20% on the final conversion pitch.
                3. SEO STRUCTURE: Use clear Markdown hierarchy (H1 for title, H2 and H3 for subheadings).
                4. TONE: Professional, instructional, authoritative.
                
                Required Layout:
                - Captivating, SEO-friendly Title (H1)
                - Introduction: Hook the reader by explaining the industry challenge.
                - Section 1 (H2): The Architectural Workflow (Step-by-step how the automation connects data safely).
                - Section 2 (H2): Core Tools & Setup Benchmarks (How Make/Zapier interact with CRM APIs).
                - Conclusion & Premium CTA (H2): Invite them to book a free Automation Audit with the Does4U team to build this for them.
                """
                
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": seo_prompt}]
                )
                return response.choices[0].message.content, img_path
            except Exception as e:
                st.error(f"Σφάλμα GPT-4o: {e}")
                return None, None

    # 🎛️ UI ΣΤΟΙΧΕΙΑ
    st.subheader("🚀 Κέντρο Παραγωγής")
    category = st.selectbox("Επίλεξε Κατηγορία", ["📈 Growth Hacking & Automations"])
    target = st.text_input("Στόχος / Θέμα Άρθρου (π.χ. How to automate cold LinkedIn outreach and sync warm leads to HubSpot using AI Agents)")
    
    # Session state για να μην χάνεται το άρθρο αν γίνει click στο κουμπί δημοσίευσης
    if "current_article" not in st.session_state:
        st.session_state.current_article = None
    if "current_img" not in st.session_state:
        st.session_state.current_img = None

    if st.button("🚀 Έναρξη Έρευνας & Συγγραφής"):
        if target:
            content, img = generate_strategic_article(category, target)
            if content:
                st.session_state.current_article = content
                st.session_state.current_img = img
        else:
            st.warning("Παρακαλώ εισάγετε ένα θέμα στόχευσης.")

    # Εμφάνιση του άρθρου και του κουμπιού δημοσίευσης αν υπάρχει παραχθέν περιεχόμενο
    if st.session_state.current_article:
        st.markdown("---")
        st.markdown("### 📝 Παραγωγή Draft (SEO Optimized)")
        st.markdown(st.session_state.current_article)
        
        if st.button("✅ Έγκριση & Live Δημοσίευση στο Blog"):
            data_file = "blog_data.json"
            
            # Καθαρισμός τίτλου για το αρχείο
            clean_title = target if len(target) < 60 else target[:57] + "..."
            
            new_article = {
                "title": clean_title,
                "date": datetime.now().strftime("%d/%m/%Y"),
                "category": "Growth Hacking & Automations",
                "content": st.session_state.current_article,
                "image": st.session_state.current_img
            }
            
            try:
                if os.path.exists(data_file):
                    with open(data_file, "r", encoding="utf-8") as f:
                        articles = json.load(f)
                else:
                    articles = []
            except:
                articles = []
                
            articles.insert(0, new_article)
            
            with open(data_file, "w", encoding="utf-8") as f:
                json.dump(articles, f, ensure_ascii=False, indent=4)
                
            st.success("🎉 Το άρθρο αποθηκεύτηκε επιτυχώς στο blog_data.json!")
            # Μηδενισμός του state μετά τη δημοσίευση
            st.session_state.current_article = None

# ==========================================
# TAB 2: DEAL HUNTER BOT (REDDIT LEADS)
# ==========================================
with admin_tab2:
    st.title("🏹 Does4U Deal Hunter Bot")
    st.write("Σκανάρετε το Reddit live για άτομα που ψάχνουν λύσεις αυτοματοποίησης.")
    st.info("Το Configuration Panel του Deal Hunter είναι έτοιμο. Εκκρεμεί η σύνδεση των Reddit API Keys.")