import streamlit as st
import docx
import PyPDF2
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors

# ==========================================
# 🛠️ ΜΗΧΑΝΙΣΜΟΙ ΔΙΑΒΑΣΜΑΤΟΣ
# ==========================================

def read_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text if text.strip() else "Δεν βρέθηκε αναγνώσιμο κείμενο."
    except Exception as e:
        return f"Σφάλμα ανάγνωσης PDF: {e}"

def read_docx(file):
    try:
        doc = docx.Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        return f"Σφάλμα ανάγνωσης Word: {e}"

def read_txt(file):
    try:
        return file.read().decode("utf-8")
    except:
        return file.read().decode("latin-1")

# ==========================================
# 📦 ΜΗΧΑΝΙΣΜΟΙ ΔΗΜΙΟΥΡΓΙΑΣ
# ==========================================

def create_pdf(text_content):
    import os
    import urllib.request
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    
    font_name = 'DejaVuSans'
    font_file = 'DejaVuSans.ttf'
    
    if not os.path.exists(font_file):
        url = "https://github.com/mcmaster-btech/mcmaster-btech.github.io/raw/master/fonts/DejaVuSans.ttf"
        try:
            urllib.request.urlretrieve(url, font_file)
        except Exception as e:
            pass

    try:
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_file))
        font_name = 'DejaVuSans'
    except:
        font_name = 'Helvetica'

    styles = getSampleStyleSheet()
    greek_style = ParagraphStyle('GStyle', parent=styles['Normal'], fontName=font_name, fontSize=11, leading=16)
    
    story = []
    lines = text_content.split('\n')
    for line in lines:
        if line.strip():
            story.append(Paragraph(line, greek_style))
            story.append(Spacer(1, 6))
            
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def create_docx(text_content):
    doc = docx.Document()
    lines = text_content.split('\n')
    for line in lines:
        if line.strip():
            doc.add_paragraph(line)
    
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()

# ==========================================
# 🖥️ Η ΒΙΤΡΙΝΑ ΤΟΥ ΜΕΤΑΤΡΟΠΕΑ (UI)
# ==========================================
# Εδώ προσθέτουμε το key_id για να δέχεται την παράμετρο από το app.py!
def show_converter_ui(key_id="default_converter"):
    st.write("---")
    st.markdown("### 🔄 Πολυμορφικός Μετατροπέας Εγγράφων")
    
    uploaded_file = st.session_state.get('conv_up', None)
    
    if uploaded_file is not None:
        file_name = uploaded_file.name
        file_type = file_name.split('.')[-1].lower()
        
        st.success(f"📥 Το αρχείο **{file_name}** φορτώθηκε επιτυχώς!")
        
        raw_text = ""
        if file_type == "pdf":
            raw_text = read_pdf(uploaded_file)
        elif file_type == "docx":
            raw_text = read_docx(uploaded_file)
        elif file_type == "txt":
            raw_text = read_txt(uploaded_file)
        else:
            st.warning("⚠️ Για φωτογραφίες (.jpg, .png) απαιτείται σύνδεση με OCR.")
            return

        st.markdown("#### 🎯 Επιλέξτε τη μορφή του τελικού εγγράφου:")
        
        # Το selectbox χρησιμοποιεί το key_id που έρχεται από το app.py
        conversion_target = st.selectbox(
            "Διαθέσιμες Μετατροπές:",
            [
                "--- Παρακαλώ επιλέξτε ---",
                "Μετατροπή σε Αρχείο Word (.docx)",
                "Μετατροπή σε Έγγραφο PDF (.pdf)",
                "Μετατροπή σε Απλό Κείμενο (.txt)"
            ],
            key=f"selectbox_{key_id}"
        )
        
        if conversion_target == "Μετατροπή σε Αρχείο Word (.docx)":
            docx_bytes = create_docx(raw_text)
            st.download_button(
                label="📥 Λήψη έτοιμου εγγράφου Word (.docx)",
                data=docx_bytes,
                file_name="does4u_converted.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                key=f"btn_docx_{key_id}"
            )
                
        elif conversion_target == "Μετατροπή σε Έγγραφο PDF (.pdf)":
            pdf_bytes = create_pdf(raw_text)
            st.download_button(
                label="📥 Λήψη έτοιμου εγγράφου PDF (.pdf)",
                data=pdf_bytes,
                file_name="does4u_converted.pdf",
                mime="application/pdf",
                use_container_width=True,
                key=f"btn_pdf_{key_id}"
            )
                
        elif conversion_target == "Μετατροπή σε Απλό Κείμενο (.txt)":
            st.download_button(
                label="📥 Λήψη αρχείου Κειμένου (.txt)",
                data=raw_text,
                file_name="does4u_converted.txt",
                mime="text/plain",
                use_container_width=True,
                key=f"btn_txt_{key_id}"
            )
            
    else:
        st.warning("⚠️ Παρακαλώ ανεβάστε πρώτα ένα έγγραφο στο δεξί κουτί (Convert Box).")