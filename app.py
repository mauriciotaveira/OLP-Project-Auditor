import streamlit as st
import PyPDF2
from google import genai
from fpdf import FPDF
from docx import Document
from io import BytesIO
import time

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Robotmaster OLP Auditor", page_icon="🤖", layout="wide")

# CSS "Black & Red Professional" - Ferrari Edition
st.markdown("""
    <style>
    .report-container {
        background-color: #ffffff;
        padding: 45px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        box-shadow: 0px 8px 25px rgba(0,0,0,0.08);
        color: #1a1a1a !important; 
        line-height: 1.7;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    .report-container h2 {
        color: #D32F2F !important; 
        text-transform: uppercase;
        border-bottom: 4px solid #D32F2F;
        padding-bottom: 8px;
        font-weight: 900 !important;
        font-size: 22px;
        margin-top: 40px;
        letter-spacing: 1px;
    }
    .report-container strong, .report-container b {
        color: #000000 !important; 
        font-weight: 800;
    }
    .report-header {
        text-align: center;
        margin-bottom: 30px;
        padding-bottom: 20px;
        border-bottom: 1px solid #eee;
    }
    /* Estilo para os cards de histórico na barra lateral */
    .stButton>button { border-radius: 6px !important; }
    </style>
    """, unsafe_allow_html=True)

# Inicializar Session State
if "history" not in st.session_state: st.session_state.history = []
if "current_report" not in st.session_state: st.session_state.current_report = None

# --- 2. SIDEBAR ---
with st.sidebar:
    try: st.image("LOGO_Robotmaster_RGB.png", use_container_width=True)
    except: st.markdown("<h2 style='color:#D32F2F; font-weight:900; text-align:center;'>ROBOTMASTER</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.title("🕒 Recent Audits")
    for idx, hist in enumerate(reversed(st.session_state.history)):
        if st.button(f"📄 Audit {hist['time']}", key=f"hist_{idx}", use_container_width=True):
            st.session_state.current_report = hist['content']

# --- 3. INTERFACE PRINCIPAL ---
st.markdown("<h3 style='text-align: center; color: #D32F2F; font-weight: 900;'>ADVANCED OLP ENGINEERING AUDITOR</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555;'>Upload the Client RFP for deep kinematic and ROI analysis.</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type="pdf")

if st.button("🚀 EXECUTE ROBOTMASTER V7 ANALYSIS", type="primary", use_container_width=True):
    if uploaded_file:
        # A MÁGICA DA UX "FERRARI": Efeito de carregamento em etapas
        with st.status("⚙️ Initializing Anbu Intelligence Engine...", expanded=True) as status:
            try:
                st.write("📄 Extracting technical data from RFP...")
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                pdf_text = "".join([page.extract_text() or "" for page in pdf_reader.pages])
                
                st.write("🤖 Connecting to Gemini 2.5 Flash Neural Network...")
                client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
                
                st.write("📐 Mapping Kinematics & V7 Architecture...")
                # O PROMPT DE ELITE (MOTOR V12)
                system_instruction = """
                You are an Elite Robotics Solutions Architect & Senior Robotmaster V7 OLP Specialist.
                Your mission is to analyze client RFPs and deliver a highly technical, persuasive, and data-driven Engineering & Integration Report.

                FORMAT STRICTLY USING THE FOLLOWING SECTIONS (Use '##' for titles):

                ## 1. EXECUTIVE SUMMARY & PROCESS OVERVIEW
                Provide a high-level summary of the client's manufacturing process. Identify the core robotic application (e.g., Welding, Milling) and the primary bottleneck.

                ## 2. MACHINERY & KINEMATICS ANALYSIS
                Analyze the robots, positioners, rails, and tooling mentioned. Highlight any kinematic complexities like external axes management or reach issues.

                ## 3. ROBOTMASTER V7 SOLUTION ARCHITECTURE
                Map the exact Robotmaster V7 modules required. Explain WHY they are needed (e.g., "Interactive Task Creation for complex trajectories", "MIG/MAG Welding Module for seam tracking").

                ## 4. ADVANCED R.O.I. & METRICS COMPARISON
                List the ROI impact using exactly this format (NO TABLES):
                - **Programming Time:** [Manual/Teach Pendant] vs [Robotmaster V7] ➔ [Quantifiable Savings]
                - **Production Downtime:** [Current] vs [Robotmaster V7] ➔ [Quantifiable Savings]
                - **Path Accuracy & Quality:** [Current] vs [Robotmaster V7] ➔ [Quantifiable Savings]

                ## 5. RISK ASSESSMENT & MITIGATION
                Identify technical risks (e.g., singularities, collisions, joint limits) and explain how Robotmaster's Optimization tools automatically mitigate them.

                ## 6. EXECUTIVE RECOMMENDATION
                A strong, closing paragraph convincing the client that Robotmaster is the absolute best software investment.

                TONE: Highly technical, authoritative, yet persuasive. Use precise industrial robotics terminology. DO NOT USE TABLES.
                """
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=f"{system_instruction}\n\nDocument:\n{pdf_text}",
                )
                
                st.write("✅ Finalizing ROI Executive Report...")
                time.sleep(1) # Pausa dramática rápida para efeito visual
                
                st.session_state.current_report = response.text
                st.session_state.history.append({"time": time.strftime("%H:%M"), "content": response.text})
                
                status.update(label="Analysis Successfully Completed!", state="complete", expanded=False)
                
            except Exception as e: 
                status.update(label="Critical Error Encountered", state="error", expanded=False)
                st.error(f"Error details: {e}")
    else:
        st.warning("⚠️ Please upload a PDF file first.")

# --- 4. EXIBIÇÃO ---
if st.session_state.current_report:
    st.markdown('<div class="report-container">', unsafe_allow_html=True)
    st.markdown('<div class="report-header"><h4>CONFIDENTIAL ENGINEERING REPORT</h4><p style="color:red; font-weight:bold;">GENERATED BY ROBOTMASTER AI</p></div>', unsafe_allow_html=True)
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
            if "|" in line: continue 
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
    with c1: st.download_button("📄 Download PDF Report", create_pdf(st.session_state.current_report), f"Robotmaster_Audit_{u_id}.pdf", key=f"p_{u_id}", use_container_width=True)
    with c2: 
        doc = Document(); doc.add_heading('Robotmaster Engineering Report', 0); doc.add_paragraph(st.session_state.current_report); target = BytesIO(); doc.save(target)
        st.download_button("📝 Download Word Doc", target.getvalue(), f"Robotmaster_Audit_{u_id}.docx", key=f"w_{u_id}", use_container_width=True)
    with c3: st.link_button("📧 Email to Sales Team", "mailto:sales@robotmaster.com", use_container_width=True)