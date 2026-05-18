import streamlit as st
import requests
from openai import OpenAI
import json
import pandas as pd

# Ρύθμιση Σελίδας
st.set_page_config(page_title="Does4U - Lead Gen & Copywriter v0.0.6", page_icon="⚡", layout="wide")
st.title("⚡ Does4U Lead Gen & Copywriter v0.0.6")
st.subheader("Στάδιο 1 & 2: Συλλογή, Φιλτράρισμα & Έτοιμα Cold Emails")

# Έλεγχος και Διάβασμα των κλειδιών από τα Secrets
try:
    JINA_API_KEY = st.secrets["JINA_API_KEY"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("🚨 Σφάλμα: Λείπει το JINA_API_KEY ή το OPENAI_API_KEY από τα Secrets του Streamlit!")
    st.stop()

XING_TARGET_URL = "https://www.xing.com/jobs/search?keywords=python%20freelance"

if st.button("🚀 ΕΝΑΡΞΗ ΠΛΗΡΟΥΣ ΑΥΤΟΜΑΤΙΣΜΟΥ v0.0.6"):
    st.write("📡 Η Jina AI σκανάρει το Xing για Freelance/Junior ευκαιρίες...")
    
    try:
        jina_endpoint = f"https://r.jina.ai/{XING_TARGET_URL}"
        headers = {"Authorization": f"Bearer {JINA_API_KEY}", "X-Return-Format": "markdown"}
        response = requests.get(jina_endpoint, headers=headers)
        
        if response.status_code != 200:
            st.error(f"❌ Η Jina API απέτυχε με Status: {response.status_code}")
        else:
            raw_markdown = response.text
            
            if not raw_markdown or len(raw_markdown.strip()) < 200:
                st.error("⚠️ Άδειο ή πολύ μικρό κείμενο επιστράφηκε από τη Jina.")
            else:
                st.success("✅ Τα δεδομένα του Xing λήφθηκαν επιτυχώς!")
                
                with st.spinner("Το GPT-4o-mini αναλύει, φιλτράρει και γράφει τα emails προσέγγισης..."):
                    openai_client = OpenAI(api_key=OPENAI_API_KEY)
                    
                    # Ζητάμε από το AI να κάνει τη συλλογή ΚΑΙ το copywriting ταυτόχρονα
                    prompt = """
                    Είσαι ο κορυφαίος Lead Generator και Cold Copywriter της Does4U. 
                    Ψάξε στο Markdown κείμενο του Xing για projects Python (Freelance, Junior, One-off, fixed price).
                    Αποκλεισέ και πέταξε στα σκουπίδια μόνιμες θέσεις εργασίας (Festanstellung, Vollzeit, μόνιμος υπάλληλος).
                    
                    Για κάθε κατάλληλο lead που βρίσκεις, θέλω να δημιουργήσεις ένα επαγγελματικό, σύντομο και ελκυστικό Cold Email στα Αγγλικά, με σκοπό να τους προσφέρεις τις υπηρεσίες μας (Python automation, Web Scraping, scripts) ως εξωτερικός συνεργάτης. Το email πρέπει να είναι έτοιμο για copy-paste, χωρίς placeholders (αν δεν ξέρεις το όνομα του υπεύθυνου, ξεκίνα με "Dear Hiring Team," ή "Hello,").
                    
                    Επέστρεψε ΑΥΣΤΗΡΑ ΚΑΙ ΜΟΝΟ ένα JSON αντικείμενο με αυτή τη δομή:
                    {
                        "leads": [
                            {
                                "title_gr": "Ο τίτλος της αγγελίας στα Ελληνικά",
                                "client_company_keyword": "Όνομα Εταιρείας",
                                "project_link": "Το link της αγγελίας στο Xing",
                                "summary_gr": "Τι συγκεκριμένο έργο ζητάνε να παραδοθεί (στα Ελληνικά)",
                                "ready_email_en": "Το έτοιμο Cold Email στα Αγγλικά προσαρμοσμένο για αυτή την εταιρεία"
                            }
                        ]
                    }
                    """
                    
                    ai_response = openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        response_format={"type": "json_object"},
                        messages=[
                            {"role": "system", "content": "You are a precise data extractor and business copywriter. Return only valid JSON."},
                            {"role": "user", "content": f"{prompt}\n\nΚείμενο Xing:\n{raw_markdown}"}
                        ],
                        temperature=0.2
                    )
                    
                    ai_data = json.loads(ai_response.choices[0].message.content)
                    leads_list = ai_data.get("leads", [])
                    
                    if len(leads_list) == 0:
                        st.warning("⚠️ Δεν βρέθηκαν One-Off/Freelance projects αυτή τη στιγμή στο Xing.")
                    else:
                        st.success(f"🔥 Επιτυχία! Βρέθηκαν {len(leads_list)} κατάλληλα leads!")
                        
                        # Δημιουργία καθαρού πίνακα για τον χρήστη
                        for idx, lead in enumerate(leads_list):
                            company = lead['client_company_keyword']
                            title = lead['title_gr']
                            summary = lead['summary_gr']
                            link = lead['project_link']
                            email_content = lead['ready_email_en']
                            
                            with st.expander(f"💼 {idx+1}. {company} - {title}"):
                                col1, col2 = st.columns([1, 1])
                                
                                with col1:
                                    st.markdown("#### 📑 Στοιχεία Αγγελίας (Ελληνικά)")
                                    st.write(f"**Εταιρεία:** `{company}`")
                                    st.write(f"**Τι ζητάνε:** {summary}")
                                    st.markdown(f"[🔗 Δες την αγγελία στο Xing]({link})")
                                
                                with col2:
                                    st.markdown("#### ✉️ Έτοιμο Cold Email (Αγγλικά)")
                                    st.text_area(
                                        label="Κάνε Copy-Paste το κείμενο:",
                                        value=email_content,
                                        height=250,
                                        key=f"email_{idx}"
                                    )
                                    st.caption("💡 Μπορείς να αντιγράψεις αυτό το κείμενο και να το στείλεις μέσω Xing ή της φόρμας επικοινωνίας τους.")
                                
    except Exception as e:
        st.error(f"🚨 Σφάλμα συστήματος: {e}")