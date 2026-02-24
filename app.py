import streamlit as st
import PyPDF2
import re
from google import genai
from fpdf import FPDF
from docx import Document
from io import BytesIO
import time

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Robotmaster OLP Auditor", page_icon="🤖", layout="centered")

# --- 2. HEADER ---
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    try:
        st.image("LOGO_Robotmaster_RGB.png", use_container_width=True)
    except:
        st.subheader("Robotmaster")

st.markdown("<h2 style='text-align: center; color: #D32F2F;'>OLP Project Auditor</h2>", unsafe_allow_html=True)
st.write("---")

# --- 3. CONFIGURAÇÃO DE ACESSO ---
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("⚠️ API Key not found in Streamlit Secrets.")
    st.stop()

# --- 4. INTERFACE ---
uploaded_file = st.file_uploader("Upload Client RFP (PDF)", type="pdf")

if not uploaded_file:
    st.info("💡 Please upload the technical scope to start.")
    st.stop()

# --- 5. PROCESSAMENTO & AI ---
try:
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    pdf_text = ""
    for page in pdf_reader.pages:
        pdf_text += page.extract_text() or ""
    
    if st.button("Analyze Project & Generate Proposal"):
        with st.spinner("Analyzing with Gemini 2.5 Flash..."):
            client = genai.Client(api_key=api_key)
            
            system_instruction = "You are the Senior Engineer at Robotmaster. Structure: 1. Machinery Summary, 2. Recommended V7 Modules, 3. Post-Processor, 4. Technical Risk Alerts, 5. Sales Pitch. Respond in English. No emojis."
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f"{system_instruction}\n\nDocument:\n{pdf_text}",
            )
            
            raw_text = response.text

            # --- 6. EXIBIÇÃO NA TELA (Design Premium Corrigido) ---
            st.markdown("---")
            
            # Títulos em Vermelho Robotmaster (32px)
            processed_html = re.sub(
                r'^(\d+\..*?)$', 
                r'<h2 style="color:#D32F2F; font-size:32px; margin-top:40px; border-bottom: 3px solid #D32F2F; font-weight: 900; text-transform: uppercase;">\1</h2>', 
                raw_text, flags=re.MULTILINE
            )
            
            # Subtítulos em Azul Robotmaster (20px)
            processed_html = re.sub(r'\*\*(.*?)\*\*', r'<b style="color:#005a9c; font-size:20px;">\1</b>', processed_html)
            processed_html = processed_html.replace('\n', '<br>')

            st.markdown(f"""
            <div style="background-color: white; padding: 40px; border-radius: 15px; border: 1px solid #ddd; box-shadow: 0px 10px 30px rgba(0,0,0,0.1); color: #222;">
                <div style="text-align: right; color: #ccc; font-size: 10px; font-weight: bold;">OFFICIAL AUDIT</div>
                {processed_html}
            </div>
            """, unsafe_allow_html=True)

            # --- 7. FUNÇÃO PDF ---
            def create_pdf(text):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.set_text_color(211, 47, 47) # Vermelho
                pdf.cell(0, 10, "Engineering Report", ln=True, align='R')
                pdf.ln(10)
                
                for line in text.split('\n'):
                    line = line.replace('**', '').strip()
                    if not line: continue
                    if re.match(r'^\d+\.', line):
                        pdf.set_font("Arial", 'B', 14)
                        pdf.set_text_color(211, 47, 47)
                    else:
                        pdf.set_font("Arial", size=11)
                        pdf.set_text_color(40, 40, 40)
                    pdf.multi_cell(0, 7, line.encode('latin-1', 'replace').decode('latin-1'))
                return pdf.output(dest='S').encode('latin-1')

            # --- 8. BOTÕES (Sem Erro de Duplicação) ---
            st.markdown("<br>", unsafe_allow_html=True)
            u_id = str(int(time.time()))
            c1, c2, c3 = st.columns(3)

            with c1:
                st.download_button("📄 PDF Report", create_pdf(raw_text), f"Audit_{u_id}.pdf", key=f"pdf_{u_id}", use_container_width=True)
            with c2:
                doc = Document()
                doc.add_paragraph(raw_text)
                target = BytesIO()
                doc.save(target)
                st.download_button("📝 Word Doc", target.getvalue(), f"Audit_{u_id}.docx", key=f"word_{u_id}", use_container_width=True)
            with c3:
                mailto = f"mailto:sales@robotmaster.com?subject=Audit&body=Report ready."
                st.markdown(f'<a href="{mailto}" style="text-decoration:none;"><div style="background-color:#D32F2F; color:white; padding:10px; text-align:center; border-radius:5px; font-weight:bold;">📧 Email</div></a>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error: {e}")