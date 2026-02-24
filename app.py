import streamlit as st
import PyPDF2
import re
from google import genai
from fpdf import FPDF
from docx import Document
from io import BytesIO
import time

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Robotmaster OLP Auditor", page_icon="🤖", layout="wide")

# CSS "Black & Red Professional" - Texto do corpo em Preto
st.markdown("""
    <style>
    .report-container {
        background-color: white;
        padding: 40px;
        border-radius: 15px;
        border: 1px solid #ddd;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.1);
        color: #000000 !important; /* Texto do corpo 100% Preto */
        line-height: 1.6;
    }
    .report-container h2 {
        color: #D32F2F !important; /* Títulos Vermelho Robotmaster */
        text-transform: uppercase;
        border-bottom: 3px solid #D32F2F;
        padding-bottom: 10px;
        font-weight: 800 !important;
        font-size: 24px;
        margin-top: 30px;
    }
    .report-container strong, .report-container b {
        color: #000000 !important; /* Negritos também em preto para sobriedade */
        font-weight: bold;
    }
    /* Tabela ROI Moderna 2026 */
    table { width: 100%; border-collapse: collapse; margin: 25px 0; font-size: 15px; }
    th { background-color: #f8f9fa !important; color: #D32F2F !important; padding: 12px; border: 1px solid #ddd; }
    td { padding: 12px; border: 1px solid #ddd; text-align: left; color: #000; }
    tr:nth-child(even) { background-color: #fafafa; }
    </style>
    """, unsafe_allow_html=True)

# Inicializar Session State
if "history" not in st.session_state: st.session_state.history = []
if "current_report" not in st.session_state: st.session_state.current_report = None

# --- 2. SIDEBAR ---
with st.sidebar:
    try: st.image("LOGO_Robotmaster_RGB.png", use_container_width=True)
    except: st.title("Robotmaster")
    st.markdown("---")
    st.title("🕒 Recent Audits")
    for idx, hist in enumerate(reversed(st.session_state.history)):
        if st.button(f"Report {hist['time']}", key=f"hist_{idx}", use_container_width=True):
            st.session_state.current_report = hist['content']

# --- 3. INTERFACE PRINCIPAL ---
st.markdown("<h1 style='text-align: center; color: #D32F2F;'>OLP Project Auditor</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload Client RFP (PDF)", type="pdf")

if st.button("🚀 Run Robotmaster Analysis", use_container_width=True):
    if uploaded_file:
        with st.spinner("Anbu Intelligence processing..."):
            try:
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                pdf_text = "".join([page.extract_text() or "" for page in pdf_reader.pages])
                client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
                
                system_instruction = """
                You are a Senior Robotmaster Sales Engineer. 
                Structure:
                ## 1. Machinery Summary
                ## 2. Recommended V7 Modules
                ## 3. Welding Management (MIG/MAG)
                ## 4. ROI Analysis Table
                ## 5. Post-Processor & Risks
                ## 6. Sales Pitch
                Important: Use '##' for titles. Use standard Markdown tables for ROI. 
                Language: English. Body text must be technical and clear.
                """
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=f"{system_instruction}\n\nDocument:\n{pdf_text}",
                )
                st.session_state.current_report = response.text
                st.session_state.history.append({"time": time.strftime("%H:%M:%S"), "content": response.text})
            except Exception as e: st.error(f"Error: {e}")

# --- 4. EXIBIÇÃO ---
if st.session_state.current_report:
    st.markdown('<div class="report-container">', unsafe_allow_html=True)
    st.markdown(st.session_state.current_report)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- 5. FUNÇÃO PDF LIMPA ---
    def create_pdf(text):
        pdf = FPDF()
        pdf.add_page()
        try: pdf.image("LOGO_Robotmaster_RGB.png", 10, 8, 35)
        except: pass
        
        pdf.set_font("Arial", 'B', 16)
        pdf.set_text_color(211, 47, 47)
        pdf.cell(0, 10, "Engineering & Integration Report", ln=True, align='R')
        pdf.line(10, 35, 200, 35)
        pdf.ln(15)
        
        pdf.set_font("Arial", size=11)
        pdf.set_text_color(0, 0, 0)
        
        for line in text.split('\n'):
            if "|" in line: continue # Ignora linhas de tabela para o PDF ficar limpo
            clean_line = line.replace('##', '').replace('**', '').strip()
            if not clean_line:
                pdf.ln(4)
                continue
            pdf.multi_cell(0, 7, clean_line.encode('latin-1', 'replace').decode('latin-1'))
        return pdf.output(dest='S').encode('latin-1')

    # --- 6. BOTÕES ---
    st.markdown("<br>", unsafe_allow_html=True)
    u_id = str(int(time.time()))
    c1, c2, c3 = st.columns(3)
    with c1: st.download_button("📄 PDF Report", create_pdf(st.session_state.current_report), f"Robotmaster_Audit_{u_id}.pdf", key=f"p_{u_id}", use_container_width=True)
    with c2: 
        doc = Document(); doc.add_paragraph(st.session_state.current_report); target = BytesIO(); doc.save(target)
        st.download_button("📝 Word Doc", target.getvalue(), f"Robotmaster_Audit_{u_id}.docx", key=f"w_{u_id}", use_container_width=True)
    with c3: st.link_button("📧 Email Report", "mailto:sales@robotmaster.com", use_container_width=True)