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

# Inicializar Estados
if "history" not in st.session_state:
    st.session_state.history = []
if "current_report" not in st.session_state:
    st.session_state.current_report = None

# --- 2. SIDEBAR (Histórico) ---
with st.sidebar:
    st.image("LOGO_Robotmaster_RGB.png", use_container_width=True)
    st.title("🕒 Recent Audits")
    if not st.session_state.history:
        st.write("No history yet.")
    else:
        for idx, hist in enumerate(reversed(st.session_state.history)):
            if st.button(f"Report {hist['time']}", key=f"hist_{idx}"):
                st.session_state.current_report = hist['content']

# --- 3. HEADER ---
st.markdown("<h1 style='text-align: center; color: #D32F2F;'>OLP Project Auditor</h1>", unsafe_allow_html=True)
st.write("---")

# --- 4. CONFIGURAÇÃO DE ACESSO ---
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("⚠️ API Key missing.")
    st.stop()

# --- 5. INTERFACE ---
uploaded_file = st.file_uploader("Upload Client RFP (PDF)", type="pdf")

if st.button("🚀 Run AI Analysis", use_container_width=True):
    if uploaded_file:
        with st.spinner("Anbu Intelligence processing..."):
            try:
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                pdf_text = "".join([page.extract_text() or "" for page in pdf_reader.pages])
                
                client = genai.Client(api_key=api_key)
                system_instruction = """
                You are a Senior Robotmaster Sales Engineer. 
                Structure:
                1. Machinery Summary
                2. Recommended V7 Modules
                3. Welding Management (MIG/MAG)
                4. ROI Analysis Table (Comparing: Manual Teach vs Robotmaster V7)
                5. Post-Processor & Risks
                6. Sales Pitch
                Respond in English. No emojis. Important: Use standard Markdown tables for ROI.
                """
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=f"{system_instruction}\n\nDocument:\n{pdf_text}",
                )
                
                report_data = response.text
                st.session_state.current_report = report_data
                st.session_state.history.append({"time": time.strftime("%H:%M:%S"), "content": report_data})
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Upload a file first.")

# --- 6. FUNÇÃO PDF REAL (Corrigida) ---
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    try:
        pdf.image("LOGO_Robotmaster_RGB.png", 10, 8, 35)
    except: pass
    
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(211, 47, 47)
    pdf.cell(0, 10, "Engineering & Integration Report", ln=True, align='R')
    pdf.line(10, 35, 200, 35)
    pdf.ln(15)
    
    pdf.set_font("Arial", size=11)
    pdf.set_text_color(40, 40, 40)
    
    # Limpeza básica para o PDF não quebrar
    clean_text = text.replace('**', '').replace('#', '')
    for line in clean_text.split('\n'):
        if "|" in line: continue # Ignora tabelas no PDF por enquanto para evitar bugs de alinhamento
        pdf.multi_cell(0, 7, line.encode('latin-1', 'replace').decode('latin-1'))
    return pdf.output(dest='S').encode('latin-1')

# --- 7. EXIBIÇÃO ---
if st.session_state.current_report:
    report_text = st.session_state.current_report
    
    # 1. Limpar caracteres que causam "bugs" de fonte
    display_text = report_text.replace('###', '').replace('#', '')

    # 2. Formatar Títulos (Só linhas que começam com "1. ", "2. ", etc)
    display_text = re.sub(r'^([1-9]\.\s.*)$', r'<h2 style="color:#D32F2F; font-size:26px; border-bottom: 2px solid #D32F2F; margin-top:30px;">\1</h2>', display_text, flags=re.MULTILINE)
    
    # 3. Formatar Subtítulos (**)
    display_text = re.sub(r'\*\*(.*?)\*\*', r'<b style="color:#005a9c; font-size:18px;">\1</b>', display_text)
    
    # 4. TRATAMENTO DA TABELA ROI (O "Gráfico" que bugou)
    # Convertemos a tabela Markdown para HTML estilizado
    if "|" in display_text:
        display_text = display_text.replace('\n|', '<br>|') # Garante que a tabela não quebre a linha errado
    
    display_text = display_text.replace('\n', '<br>')

    st.markdown(f"""
    <style>
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; font-family: sans-serif; }}
        th {{ background-color: #005a9c; color: white; padding: 12px; border: 1px solid #ddd; }}
        td {{ padding: 10px; border: 1px solid #ddd; text-align: left; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
    </style>
    <div style="background-color: white; padding: 40px; border-radius: 15px; border: 1px solid #ddd; box-shadow: 0px 10px 30px rgba(0,0,0,0.1); color: #222;">
        {display_text}
    </div>
    """, unsafe_allow_html=True)

    # --- 8. BOTÕES ---
    st.markdown("<br>", unsafe_allow_html=True)
    u_id = str(int(time.time()))
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.download_button("📄 PDF Report", create_pdf(report_text), f"Audit_{u_id}.pdf", key=f"pdf_{u_id}", use_container_width=True)
    with c2:
        doc = Document(); doc.add_paragraph(report_text); target = BytesIO(); doc.save(target)
        st.download_button("📝 Word Doc", target.getvalue(), f"Audit_{u_id}.docx", key=f"word_{u_id}", use_container_width=True)
    with c3:
        mailto = f"mailto:sales@robotmaster.com?subject=Audit&body=Report%20Ready."
        st.link_button("📧 Email Report", mailto, use_container_width=True)