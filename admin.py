import os
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI
from tavily import TavilyClient
import praw

# ==========================================
# 🔑 1. SETUP & ΑΣΦΑΛΕΙΑ ΚΛΕΙΔΙΩΝ
# ==========================================
load_dotenv()
openai_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
tavily_key = st.secrets.get("TAVILY_API_KEY", os.getenv("TAVILY_API_KEY"))

# Reddit Keys
reddit_id = st.secrets.get("REDDIT_CLIENT_ID", os.getenv("REDDIT_CLIENT_ID"))
reddit_secret = st.secrets.get("REDDIT_CLIENT_SECRET", os.getenv("REDDIT_CLIENT_SECRET"))
reddit_ua = st.secrets.get("REDDIT_USER_AGENT", os.getenv("REDDIT_USER_AGENT"))

client = OpenAI(api_key=openai_key)
tavily = TavilyClient(api_key=tavily_key)

st.set_page_config(page_title="Does4U | Command Center", page_icon="⚡", layout="wide")

# ==========================================
# 🎛️ 2. ΔΙΑΧΕΙΡΙΣΗ TABS
# ==========================================
admin_tab1, admin_tab2 = st.tabs(["📝 Blog Management", "🏹 Deal Hunter Bot"])

# ==========================================
# 📝 TAB 1: BLOG MANAGEMENT (FULL COMPACT)
# ==========================================
with admin_tab1:
    st.title("🎯 Does4U Content Pack Generator")
    st.write("Δημιουργήστε, επεξεργαστείτε και εγκρίνετε στρατηγικά άρθρα και Social Media posts.")
    st.write("---")
    
    # 🧠 Μηχανή Παραγωγής με Advanced Search & Στρατηγικό Prompt
    def generate_strategic_article(category, target):
        logic = "Disruptive Growth Hacker & B2B Automation Expert. Focus: Maximum ROI, saving time, and automated lead generation."
        query = f"Growth hacking automation {target} lead generation tools business systems 2026"
        img_path = "blog_images/growth_default.jpg"

        with st.spinner("🕵️‍♂️ Η Does4U αναλύει τις παγκόσμιες πηγές Growth Hacking μέσω Tavily..."):
            try:
                search = tavily.search(query=query, search_depth="advanced", max_results=3)
                
                prompt = f"""
                Role: {logic}
                Task: Write a high-converting, premium business article in Greek based on this target topic: '{target}'.
                
                STRATEGIC WRITING RULES:
                1. Tone: Authoritative, energetic, and highly professional. Speak directly to Business Owners, Founders, and CEOs.
                2. Language: Greek (Ελληνικά).
                3. NO COMPLICATED CODE: Focus on the business logic, workflow automation, and SaaS tools (Zapier, Make, HubSpot, AI Agents).
                4. ROI Driven: Explain exactly how much time or money the business owner saves.
                
                Structure:
                - Mind-blowing, Premium Title (Focus on growth/automation)
                - The Problem (Why manual work is killing their margins in 2026)
                - The Automated Strategy (Step-by-step how the system works conceptually)
                - Real-World Business Benefits (Time saved, leads generated)
                - High-Ticket Call to Action (CTA): Urge them to book an automation audit with Does4U.
                
                Return the output in clean, beautifully formatted Markdown.
                """
                
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": f"Context from web search: {str(search)}"},
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.choices[0].message.content, img_path
            except Exception as e:
                st.error(f"Σφάλμα κατά την παραγωγή: {e}")
                return None, None

    # UI Στοιχεία Παραγωγής
    st.subheader("🚀 Κέντρο Παραγωγής")
    category = st.selectbox("Επίλεξε Κατηγορία", ["📈 Growth Hacking & Automations"])
    target = st.text_input("Στόχος / Θέμα Άρθρου (π.χ. How to automate cold LinkedIn outreach and sync warm leads to HubSpot using AI Agents)")
    
    # Session State για να κρατάμε το κείμενο στην οθόνη χωρίς να χάνεται
    if "draft_content" not in st.session_state:
        st.session_state.draft_content = ""
        st.session_state.draft_img = ""

    if st.button("🚀 Έναρξη Έρευνας & Συγγραφής"):
        if target:
            content, img = generate_strategic_article(category, target)
            if content:
                st.session_state.draft_content = content
                st.session_state.draft_img = img
        else:
            st.warning("Παρακαλώ εισάγετε ένα θέμα στόχευσης.")

    # Εμφάνιση του Draft και των Επιλογών Έγκρισης (Αν υπάρχει περιεχόμενο)
    if st.session_state.draft_content:
        st.write("---")
        st.markdown("### 📝 Παραγωγή Draft")
        
        # Επεξεργάσιμο πλαίσιο κειμένου για να διορθώνεις ό,τι θες πριν το publish
        edited_content = st.text_area("Επεξεργασία Κειμένου Άρθρου", value=st.session_state.draft_content, height=400)
        
        st.write(f"📸 **Επιλεγμένη Εικόνα:** `{st.session_state.draft_img}`")
        
        col_app1, col_app2 = st.columns(2)
        with col_app1:
            if st.button("✅ Έγκριση & Δημοσίευση στο Blog"):
                st.success("🎉 Το άρθρο εγκρίθηκε και ανέβηκε live στο Does4U Blog!")
                # Εδώ μελλοντικά μπαίνει το save_to_database() ή το api call
        with col_app2:
            if st.button("🗑️ Απόρριψη Draft"):
                st.session_state.draft_content = ""
                st.session_state.draft_img = ""
                st.rerun()

# ==========================================
# 🏹 TAB 2: DEAL HUNTER BOT (REDDIT LEADS)
# ==========================================
with admin_tab2:
    st.title("🏹 Does4U Deal Hunter Bot")
    st.write("Σκανάρετε το Reddit live για άτομα που ψάχνουν λύσεις αυτοματοποίησης, scrapers ή lead generation.")
    st.write("---")
    
    # Φίλτρα Αναζήτησης για τα Leads
    col_bot1, col_bot2 = st.columns(2)
    with col_bot1:
        subreddit_input = st.selectbox("Επίλεξε Κοινότητα (Subreddit)", ["all", "startups", "smallbusiness", "tech", "saas", "automation"])
    with col_bot2:
        keyword = st.text_input("Λέξη-Κλειδί Αναζήτησης (π.χ. automate, scraper, crm help)", "automate")
        
    limit = st.slider("Αριθμός πρόσφατων posts για έλεγχο", min_value=10, max_value=100, value=40)
    
    if st.button("🏹 Έναρξη Live Hunting"):
        if not reddit_id or not reddit_secret:
            st.error("❌ Λείπουν τα Reddit API Keys από τα Secrets του Streamlit Cloud!")
        else:
            with st.spinner(f"🔍 Σκανάρισμα στο r/{subreddit_input} για τη λέξη '{keyword}'..."):
                try:
                    # Σύνδεση με το Reddit API
                    reddit = praw.Reddit(
                        client_id=reddit_id,
                        client_secret=reddit_secret,
                        user_agent=reddit_ua
                    )
                    
                    found_posts = []
                    # Τράβηγμα των νέων posts
                    for submission in reddit.subreddit(subreddit_input).new(limit=limit):
                        if keyword.lower() in submission.title.lower() or keyword.lower() in submission.selftext.lower():
                            found_posts.append({
                                "Τίτλος": submission.title,
                                "Subreddit": f"r/{submission.subreddit.display_name}",
                                "Σχόλια": submission.num_comments,
                                "Σύνδεσμος": f"https://reddit.com{submission.permalink}"
                            })
                    
                    if found_posts:
                        st.success(f"🎯 Βρέθηκαν {len(found_posts)} καυτά leads που ψάχνουν βοήθεια!")
                        # Εμφάνιση σε διαδραστικό full-width πίνακα
                        st.dataframe(found_posts, use_container_width=True)
                        st.info("💡 Tip: Κάνε κλικ στα links των posts για να μπεις στο Reddit και να τους στείλεις DM προσφέροντας τις υπηρεσίες της Does4U!")
                    else:
                        st.warning("😢 Δεν βρέθηκε κάποιο σχετικό post αυτή τη στιγμή. Δοκίμασε άλλη λέξη-κλειδί ή επίλεξε το r/all.")
                        
                except Exception as e:
                    st.error(f"Σφάλμα κατά το live scanning στο Reddit: {e}")