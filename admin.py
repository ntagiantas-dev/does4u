import os
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI
from tavily import TavilyClient

# 1. SETUP & ΑΣΦΑΛΕΙΑ ΚΛΕΙΔΙΩΝ (Cloud + Local)
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
    
    # 🧠 ΜΗΧΑΝΗ ΠΑΡΑΓΩΓΗΣ ΑΡΘΡΩΝ
    def generate_strategic_article(category, target):
        logic = "Disruptive Growth Hacker & B2B Automation Expert. Focus: Maximum ROI, time saving, and automated lead generation."
        query = f"Growth hacking automation {target} lead generation tools business systems 2026"
        img_path = "blog_images/growth_default.jpg"

        with st.spinner("🕵️‍♂️ Η Does4U αναλύει τις παγκόσμιες πηγές Growth Hacking..."):
            try:
                search = tavily.search(query=query, search_depth="advanced", max_results=3)
                
                prompt = f"""
                Role: {logic}
                Task: Write a high-converting, premium business article in Greek based on this target topic: '{target}'.
                
                STRATEGIC WRITING RULES:
                1. Tone: Authoritative, energetic, and highly professional. Speak directly to Business Owners and CEOs.
                2. NO COMPLICATED CODE: Focus on business logic, workflow automation, and tool integrations (Zapier, Make, HubSpot, AI Agents).
                3. ROI Driven: Highlight the time and money saved through automation.
                
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

    # 🎛️ UI ΣΤΟΙΧΕΙΑ (Εμφανίζονται κανονικά μέσα στο Tab 1)
    st.subheader("🚀 Κέντρο Παραγωγής")
    category = st.selectbox("Επίλεξε Κατηγορία", ["📈 Growth Hacking & Automations"])
    target = st.text_input("Στόχος / Θέμα Άρθρου (π.χ. How to automate manual customer onboarding)")
    
    if st.button("🚀 Έναρξη Έρευνας & Συγγραφής"):
        if target:
            content, img = generate_strategic_article(category, target)
            if content:
                st.markdown("### 📝 Παραγωγή Draft")
                st.markdown(content)
                st.success("Το άρθρο είναι έτοιμο για έλεγχο!")
        else:
            st.warning("Παρακαλώ εισάγετε ένα θέμα στόχευσης.")

# ==========================================
# TAB 2: DEAL HUNTER BOT (REDDIT LEADS)
# ==========================================
with admin_tab2:
    st.title("🏹 Does4U Deal Hunter Bot")
    st.write("Σκανάρετε το Reddit live για άτομα που ψάχνουν λύσεις αυτοματοποίησης.")
    
    st.info("Το Configuration Panel του Deal Hunter είναι έτοιμο. Εκκρεμεί η σύνδεση των Reddit API Keys.")