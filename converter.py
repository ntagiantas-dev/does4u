import streamlit as st
from fpdf import FPDF
import io

def generate_pdf(text_content):
    # Δημιουργία αντικειμένου PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Προσθήκη γραμματοσειράς που υποστηρίζει Ελληνικά (πρέπει να υπάρχει το αρχείο .ttf)
    # Αν δεν έχεις το αρχείο, χρησιμοποιούμε Arial/Helvetica για το demo
    pdf.set_font("Arial", size=12)
    
    # Διαχωρισμός κειμένου σε γραμμές για να μην βγαίνει εκτός σελίδας
    lines = text_content.split('\n')
    for line in lines:
        # Κωδικοποίηση για αποφυγή προβλημάτων με ειδικούς χαρακτήρες
        safe_line = line.encode('latin-1', 'ignore').decode('latin-1')
        pdf.multi_cell(0, 10, txt=safe_line)
    
    # Επιστροφή του PDF ως Bytes
    return pdf.output(dest='S').encode('latin-1')

def show_converter_ui(processed_text):
    st.divider()
    st.subheader("📄 Μετατροπέας σε PDF")
    
    if processed_text:
        pdf_bytes = generate_pdf(processed_text)
        
        st.download_button(
            label="Λήψη Αποτελεσμάτων σε PDF",
            data=pdf_bytes,
            file_name="does4u_report.pdf",
            mime="application/pdf"
        )
    else:
        st.info("Περιμένετε την ολοκλήρωση της ανάλυσης για να κατεβάσετε το PDF.")