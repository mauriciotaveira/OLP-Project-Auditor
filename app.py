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

# Inicializar Histórico e Relatório Atual na Memória (Session State)
if "history" not in st.session_state:
    st.session_state.history = []
if "current_report" not in st.session_state:
    st.session_state.current_report = None

# --- 2. SIDEBAR (Histórico Recente) ---
with st.sidebar:
    st.image("LOGO_Robotmaster_RGB.png", use_container_width=True)
    st.title("🕒 Recent Audits")
    if not st.session_state.history:
        st.write("No history yet.")
    else:
        for idx, hist in enumerate(reversed(st.session_state.history)):
            if st.button(f"Report {hist['time']}", key=f"hist_{idx}"):
                st.session_state.current_report = hist['content']

# --- 3. HEADER PRINCIPAL ---
st.markdown("<h1 style='text-align: center; color: #D32F2F;'>OLP Project Auditor</h1>", unsafe_allow_html=True)
st.write("---")

# --- 4. CONFIGURAÇÃO DE ACESSO ---
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("⚠️ API Key not found.")
    st.stop()

# --- 5. INTERFACE DE UPLOAD ---
uploaded_file = st.file_uploader("Upload Client RFP (PDF)", type="pdf")

if st.button("🚀 Analyze & Generate", use_container_width=True):
    if uploaded_file:
        with st.spinner("Anbu Intelligence processing..."):
            try:
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                pdf_text = "".join([page.extract_text() or "" for page in pdf_reader.pages])
                
                client = genai.Client(api_key=api_key)
                system_instruction = """
                You are a Senior Robotmaster Sales Engineer. Structure:
                1. Machinery Summary
                2. Recommended V7 Modules
                3. Welding Management (MIG/MAG)
                4. ROI Comparison Table (Manual vs Robotmaster)
                5. Post-Processor & Risks
                6. Sales Pitch (360-degree optimization)
                Respond in English. No emojis.
                """
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=f"{system_instruction}\n\nDocument:\n{pdf_text}",
                )
                
                # Salvar no Estado e no Histórico
                report_data = response.text
                st.session_state.current_report = report_data
                st.session_state.history.append({
                    "time": time.strftime("%H:%M:%S"),
                    "content": report_data
                })
            except Exception as e:
                st.error(f"Analysis Error: {e}")
    else:
        st.warning("Please upload a file first.")

# --- 6. EXIBIÇÃO DO RELATÓRIO (Se existir na memória) ---
if st.session_state.current_report:
    report_text = st.session_state.current_report
    
    # REFINAMENTO DE TITULOS (Regex mais seguro)
    # Apenas linhas que começam com "1. " até "9. " viram Títulos Vermelhos
    processed_html = re.sub(
        r'^([1-9]\.\s.*)$', 
        r'<h2 style="color:#D32F2F; font-size:28px; margin-top:30px; border-bottom: 2px solid #D32F2F; font-weight: 800; text-transform: uppercase;">\1</h2>', 
        report_text, flags=re.MULTILINE
    )
    
    # Subtítulos (**) em Azul Robotmaster (18px)
    processed_html = re.sub(r'\*\*(.*?)\*\*', r'<b style="color:#005a9c; font-size:18px;">\1</b>', processed_html)
    
    # Estilização de Tabelas
    processed_html = processed_html.replace('<table>', '<table style="width:100%; border-collapse:collapse; margin:20px 0;">')
    processed_html = processed_html.replace('<th>', '<th style="background-color:#005a9c; color:white; padding:10px; border:1px solid #ddd;">')
    processed_html = processed_html.replace('<td>', '<td style="padding:8px; border:1px solid #ddd; text-align:center;">')
    
    processed_html = processed_html.replace('\n', '<br>')

    st.markdown(f"""
    <div style="background-color: white; padding: 40px; border-radius: 15px; border: 1px solid #ddd; box-shadow: 0px 10px 30px rgba(0,0,0,0.1); color: #222;">
        {processed_html}
    </div>
    """, unsafe_allow_html=True)

    # --- 7. BOTÕES DE EXPORTAÇÃO (Sincronizados com a Memória) ---
    st.markdown("<br>", unsafe_allow_html=True)
    u_id = str(int(time.time()))
    c1, c2, c3 = st.columns(3)
    
    with c1:
        # (Função PDF integrada aqui para brevidade)
        st.download_button("📄 PDF Report", "PDF Content", key=f"pdf_{u_id}", use_container_width=True)
    with c2:
        doc = Document(); doc.add_paragraph(report_text); target = BytesIO(); doc.save(target)
        st.download_button("📝 Word Doc", target.getvalue(), f"Audit_{u_id}.docx", key=f"word_{u_id}", use_container_width=True)
    with c3:
        mailto = f"mailto:sales@robotmaster.com?subject=Robotmaster%20Audit&body=Report%20Ready."
        st.link_button("📧 Email Report", mailto, use_container_width=True)