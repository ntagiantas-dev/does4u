import streamlit as st
import urllib.parse
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from openai import OpenAI

# Ρύθμιση σελίδας Streamlit
st.set_page_config(page_title="Xing Lead Generator & GPT Translator", layout="wide")

st.title("🇩🇪 Αυτοματοποιημένο Xing Lead Hunter & GPT Translator")
st.write("Μάζεψε, μετάφρασε και ανάλυσε όλα τα leads από τη Γερμανική/Αυστριακή αγορά αυτόματα σε έναν πίνακα!")

# --- ΠΛΕΥΡΙΚΟ ΜΕΝΟΥ (SETTINGS) ---
st.sidebar.header("🎯 Φίλτρα Αναζήτησης")
keyword = st.sidebar.text_input("Τι ψάχνεις; (π.χ. Web Design, Python, E-commerce)", "Web Design")
city = st.sidebar.text_input("Πόλη / Περιοχή (π.χ. Munich, Vienna, Berlin)", "Munich")

st.sidebar.subheader("🔑 Ρυθμίσεις OpenAI API")
# Σου έβαλα πεδίο για να βάζεις το κλειδί σου εύκολα. 
# Μπορείς επίσης να το καρφώσεις στον κώδικα αν θες: client = OpenAI(api_key="ΤΟ_ΚΛΕΙΔΙ_ΣΟΥ")
openai_key = st.sidebar.text_input("OpenAI API Key:", type="password")

st.sidebar.subheader("🤖 GPT Προσφορά (Pitch)")
user_pitch = st.sidebar.text_area(
    "Γράψε την προσφορά σου στα Ελληνικά:", 
    "Γεια σας, είδα την εταιρεία σας και μπορώ να σας βοηθήσω να φτιάξετε μια σύγχρονη ιστοσελίδα πιο οικονομικά."
)

# --- ΣΥΝΑΡΤΗΣΗ SCRAPING (ΣΥΛΛΟΓΗ Leads ΣΤΟ ΠΑΡΑΣΚΗΝΙΟ) ---
def fetch_xing_leads(keyword, city):
    search_query = f'site:xing.com/pages/ "{keyword}" "{city}"'
    encoded_query = urllib.parse.quote(search_query)
    url = f"https://www.google.com/search?q={encoded_query}"
    
    # Fake user agent για να μην μας μπλοκάρει η Google κατά την αναζήτηση
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return []
            
        soup = BeautifulSoup(response.text, "html.parser")
        leads = []
        
        # Εντοπισμός των αποτελεσμάτων της Google
        for g in soup.find_all('div', class_='g'):
            anchors = g.find_all('a')
            if anchors:
                link = anchors[0]['href']
                title_div = g.find('h3')
                snippet_div = g.find('div', class_='VwiC3b') # Το κείμενο περιγραφής της Google
                
                title = title_div.text if title_div else "Xing Company Page"
                snippet = snippet_div.text if snippet_div else "Δεν υπάρχει διαθέσιμη περιγραφή."
                
                if "xing.com" in link:
                    leads.append({
                        "Τίτλος": title,
                        "Σύνδεσμος (Xing)": link,
                        "Γερμανική Περιγραφή": snippet
                    })
        return leads
    except Exception as e:
        st.error(f"Σφάλμα κατά τη συλλογή: {e}")
        return []

# --- ΚΥΡΙΩΣ ΜΕΝΟΥ ---
st.subheader("🚀 Μαζική Συλλογή & Αυτόματη Μετάφραση")
st.write("Πατώντας το κουμπί, το bot θα μαζέψει τα leads και το GPT θα τα αναλύσει όλα μαζί ταυτόχρονα.")

if st.button("🔥 Έναρξη Αυτόματης Διαδικασίας"):
    if not openai_key:
        st.error("⚠️ Παρακαλώ βάλε το OpenAI API Key σου στο αριστερό μενού για να γίνει η μετάφραση!")
    else:
        # Αρχικοποίηση OpenAI Client
        client = OpenAI(api_key=openai_key)
        
        # Βήμα 1: Συλλογή
        with st.spinner("⏳ Βήμα 1: Συλλέγονται leads από το Xing μέσω Google..."):
            raw_results = fetch_xing_leads(keyword, city)
            
        if not raw_results:
            st.warning("❌ Δεν βρέθηκαν leads ή η Google μπλόκαρε προσωρινά το αίτημα. Δοκίμασε ξανά σε λίγο ή άλλαξε keywords.")
        else:
            st.success(f"✅ Επιτυχής συλλογή! Βρέθηκαν {len(raw_results)} leads στην αγορά του {city}.")
            
            # Βήμα 2: Αυτόματη Μετάφραση και Ανάλυση με GPT
            with st.spinner("🤖 Βήμα 2: Το GPT μεταφράζει και δημιουργεί έτοιμα γερμανικά μηνύματα..."):
                final_leads_list = []
                
                for idx, lead in enumerate(raw_results, 1):
                    # Στήσιμο του prompt για το GPT για μαζική επεξεργασία του κάθε lead
                    gpt_prompt = f"""
                    Έχεις ένα lead από το Xing με τα εξής στοιχεία:
                    Τίτλος: {lead['Τίτλος']}
                    Γερμανικό Κείμενο/Περιγραφή: {lead['Γερμανική Περιγραφή']}

                    Κάνε τα εξής 2 πράγματα:
                    1. Μετάφρασε και εξήγησε σύντομα στα Ελληνικά (μέχρι 2 προτάσεις) τι κάνει αυτή η εταιρεία.
                    2. Μετάφρασε το ακόλουθο ελληνικό μήνυμα προσφοράς σε άκρως επαγγελματικά Γερμανικά (χρησιμοποίησε ευγενικό πληθυντικό 'Sie'), προσαρμοσμένο για αυτή την εταιρεία:
                    "{user_pitch}"

                    Δώσε την απάντησή σου αυστηρά σε αυτή τη μορφή:
                    ΜΕΤΑΦΡΑΣΗ: [Εδώ η ελληνική μετάφραση]
                    ΜΗΝΥΜΑ: [Εδώ το γερμανικό μήνυμα pitch]
                    """
                    
                    try:
                        response = client.chat.completions.create(
                            model="gpt-4o-mini", # Οικονομικό και ταχύτατο
                            messages=[
                                {"role": "system", "content": "Είσαι ένας έμπειρος B2B Lead Generation Assistant για τη γερμανική αγορά."},
                                {"role": "user", "content": gpt_prompt}
                            ],
                            temperature=0.3
                        )
                        
                        gpt_output = response.choices[0].message.content
                        
                        # Διαχωρισμός της απάντησης του GPT σε Μετάφραση και Μήνυμα
                        parts = gpt_output.split("ΜΗΝΥΜΑ:")
                        translation_part = parts[0].replace("ΜΕΤΑΦΡΑΣΗ:", "").strip()
                        message_part = parts[1].strip() if len(parts) > 1 else "Σφάλμα δημιουργίας μηνύματος."
                        
                    except Exception as e:
                        translation_part = f"Σφάλμα API: {e}"
                        message_part = "Δεν δημιουργήθηκε μήνυμα."
                    
                    # Προσθήκη στον τελικό πίνακα
                    final_leads_list.append({
                        "Α/Α": idx,
                        "Εταιρεία (Xing Title)": lead['Τίτλος'],
                        "Τι κάνει (Μετάφραση GPT)": translation_part,
                        "Έτοιμο Γερμανικό Pitch": message_part,
                        "Link Προφίλ": lead['Σύνδεσμος (Xing)']
                    })
                    time.sleep(0.5) # Μικρή παύση για προστασία του Rate Limit
                
                # Μετατροπή σε DataFrame και εμφάνιση
                df = pd.DataFrame(final_leads_list)
                
                st.markdown("---")
                st.subheader("📋 Ολοκληρωμένη Λίστα Έτοιμων Leads")
                
                # Εμφάνιση του διαδραστικού πίνακα στο Streamlit
                st.dataframe(df, use_container_width=True)
                
                # Δημιουργία κουμπιού για κατέβασμα σε αρχείο Excel/CSV
                csv_data = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Κατέβασμα Λίστας σε CSV (Excel)",
                    data=csv_data,
                    file_name=f"xing_leads_{city}_{keyword}.csv",
                    mime="text/csv"
                )
                st.balloons()

st.markdown("---")
st.caption("Does4u Lead Hunter 2026 - Automated Enterprise Edition")