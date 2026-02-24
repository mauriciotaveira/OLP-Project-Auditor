import streamlit as st
import PyPDF2
import re
from google import genai
from fpdf import FPDF
from docx import Document
from io import BytesIO

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Robotmaster OLP Auditor", page_icon="🤖", layout="centered")

# --- 2. HEADER (Design Robotmaster) ---
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.image("LOGO_Robotmaster_RGB.png", use_container_width=True)

st.markdown("<h2 style='text-align: center; color: #D32F2F;'>OLP Project Auditor</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555555;'>Instant technical viability analysis and V7 licensing recommendations.</p>", unsafe_allow_html=True)
st.write("---")

# --- 3. CONFIGURAÇÃO DE ACESSO ---
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("⚠️ API Key not found in Streamlit Secrets.")
    st.stop()

# --- 4. INTERFACE ---
st.markdown("<br>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload Client RFP / Machinery Scope (PDF)", type="pdf", key="main_v7_uploader")

if not uploaded_file:
    st.info("💡 Please upload the technical scope to start the analysis.")
    st.stop()

# --- 5. PROCESSAMENTO & AI ANALYSIS ---
try:
    with st.spinner("Extracting technical data from PDF..."):
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        pdf_text = ""
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                pdf_text += text
    
    st.success("Document read successfully!")

    if st.button("Analyze Project & Generate Proposal"):
        with st.spinner("AI Engineering Team (Gemini 2.5 Flash) is analyzing..."):
            try:
                client = genai.Client(api_key=api_key)
                
                system_instruction = """
                You are the Senior Integration and Sales Engineer at Robotmaster. 
                Structure your report as follows:
                1. Machinery Summary
                2. Recommended V7 Modules
                3. Post-Processor
                4. Technical Risk Alerts
                5. Sales Pitch
                Respond strictly in English. Do not use emojis in the content.
                """
                
                prompt = f"{system_instruction}\n\nDocument Content:\n{pdf_text}"
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                
                raw_text = response.text

                # --- 6. EXIBIÇÃO NA TELA (Design Premium - Hierarquia Corrigida) ---
                st.markdown("---")
                
                raw_text = response.text
                
                # 1. Títulos Principais (Ex: 1. Machinery) -> VERMELHO ROBOTMASTER (#D32F2F) e MAIOR (28px)
                processed_html = re.sub(
                    r'^(\d+\..*?)$', 
                    r'<h2 style="color:#D32F2F; font-size:28px; margin-top:35px; margin-bottom:10px; border-bottom: 2px solid #f0f0f0; font-weight: bold; text-transform: uppercase;">\1</h2>', 
                    raw_text, flags=re.MULTILINE
                )
                
                # 2. Subtítulos (Texto entre **) -> AZUL ROBOTMASTER (#005a9c) e MENOR (18px)
                processed_html = re.sub(
                    r'\*\*(.*?)\*\*', 
                    r'<b style="color:#005a9c; font-size:18px; font-weight: bold;">\1</b>', 
                    processed_html
                )

                processed_html = processed_html.replace('\n', '<br>')

                st.markdown(f"""
                <div style="background-color: #ffffff; padding: 45px; border-radius: 15px; border: 1px solid #d1d1d1; box-shadow: 0px 10px 40px rgba(0,0,0,0.1); font-family: 'Segoe UI', sans-serif; color: #333333; line-height: 1.8;">
                    <div style="text-align: right; color: #ccc; font-size: 11px; font-weight: bold; letter-spacing: 2px;">OFFICIAL ENGINEERING AUDIT</div>
                    <div style="font-size: 16px;">{processed_html}</div>
                </div>
                """, unsafe_allow_html=True)

                # --- 7. FUNÇÃO GERADORA DE PDF ---
                def create_pdf(text):
                    pdf = FPDF()
                    pdf.add_page()
                    rm_red, rm_blue = (211, 47, 47), (0, 90, 156)
                    try:
                        pdf.image("LOGO_Robotmaster_RGB.png", 10, 8, 33)
                    except:
                        pass
                    pdf.set_font("Arial", 'B', 16)
                    pdf.set_text_color(*rm_red)
                    pdf.cell(0, 10, "Engineering & Integration Report", ln=True, align='R')
                    pdf.line(10, 35, 200, 35)
                    pdf.ln(15)

                    chars_to_replace = {'\u2022': '-', '\u2013': '-', '\u201c': '"', '\u201d': '"'}
                    for line in text.split('\n'):
                        line = line.strip()
                        for char, rep in chars_to_replace.items():
                            line = line.replace(char, rep)
                        is_sub = '**' in line
                        line = line.replace('**', '')
                        if not line:
                            pdf.ln(4); continue
                        if re.match(r'^(\d+\.|###)', line):
                            pdf.set_font("Arial", 'B', 14); pdf.set_text_color(*rm_red)
                            pdf.multi_cell(0, 10, line.encode('latin-1', 'replace').decode('latin-1'))
                        elif is_sub:
                            pdf.set_font("Arial", 'B', 11); pdf.set_text_color(*rm_blue)
                            pdf.multi_cell(0, 7, line.encode('latin-1', 'replace').decode('latin-1'))
                        else:
                            pdf.set_font("Arial", size=11); pdf.set_text_color(40, 40, 40)
                            pdf.multi_cell(0, 7, line.encode('latin-1', 'replace').decode('latin-1'))
                    return pdf.output(dest='S').encode('latin-1')

                # --- 8. BOTÕES (CORREÇÃO DE DOWNLOAD ERROR) ---
                st.markdown("<br>", unsafe_allow_html=True)
                col_down1, col_down2, col_down3 = st.columns(3)

                with col_down1:
                    pdf_bytes = create_pdf(raw_text)
                    # Adicionado 'key' único para evitar Duplicate Widget ID
                    st.download_button("📄 PDF Report", pdf_bytes, "Robotmaster_Audit.pdf", "application/pdf", use_container_width=True, key="btn_pdf_final")

                with col_down2:
                    doc = Document()
                    doc.add_heading('Robotmaster V7 Audit', 0)
                    doc.add_paragraph(raw_text)
                    target = BytesIO()
                    doc.save(target)
                    # Adicionado 'key' único
                    st.download_button("📝 Word Doc", target.getvalue(), "Robotmaster_Audit.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True, key="btn_word_final")

                with col_down3:
                    email_receiver, email_subject = "sales@robotmaster.com", "Robotmaster V7 Audit Report"
                    short_body = "The Robotmaster V7 OLP Audit is ready. Please check the generated report."
                    mailto_link = f"mailto:{email_receiver}?subject={email_subject}&body={short_body}"
                    st.markdown(f'<a href="{mailto_link}" style="text-decoration:none;"><div style="background-color:#D32F2F; color:white; padding:10px; text-align:center; border-radius:5px; font-weight:bold; height:38px; line-height:18px;">📧 Email Report</div></a>', unsafe_allow_html=True)

                # --- 8. EXPORTAÇÃO E BOTÃO DE E-MAIL LIMPO ---
                st.markdown("<br>", unsafe_allow_html=True)
                col_down1, col_down2, col_down3 = st.columns(3)

                with col_down1:
                    pdf_bytes = create_pdf(raw_text)
                    st.download_button("📄 PDF Report", pdf_bytes, "Robotmaster_Audit.pdf", "application/pdf", use_container_width=True)

                with col_down2:
                    doc = Document()
                    doc.add_heading('Robotmaster V7 Audit', 0)
                    doc.add_paragraph(raw_text)
                    target = BytesIO()
                    doc.save(target)
                    st.download_button("📝 Word Doc", target.getvalue(), "Robotmaster_Audit.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)

                with col_down3:
                    # Geramos o link mailto de forma limpa
                    email_receiver = "sales@robotmaster.com"
                    email_subject = "Robotmaster V7 Audit Report"
                    # Limitamos o corpo do e-mail para não sobrecarregar o link
                    short_body = "Hello, please find the Robotmaster V7 Audit attached or generated in the app."
                    mailto_link = f"mailto:{email_receiver}?subject={email_subject}&body={short_body}"
                    
                    st.markdown(f'''
                        <a href="{mailto_link}" style="text-decoration:none;">
                            <div style="background-color:#D32F2F; color:white; padding:10px; text-align:center; border-radius:5px; font-weight:bold; height:38px; line-height:18px;">
                                📧 Email Report
                            </div>
                        </a>
                    ''', unsafe_allow_html=True)

                # --- 7. FUNÇÃO GERADORA DE PDF ---
                def create_pdf(text):
                    pdf = FPDF()
                    pdf.add_page()
                    rm_blue = (0, 90, 156)
                    try:
                        pdf.image("LOGO_Robotmaster_RGB.png", 10, 8, 33)
                    except:
                        pass
                    pdf.set_font("Arial", 'B', 16)
                    pdf.set_text_color(*rm_blue)
                    pdf.cell(0, 10, "Engineering & Integration Report", ln=True, align='R')
                    pdf.line(10, 35, 200, 35)
                    pdf.ln(15)

                    chars_to_replace = {'\u2022': '-', '\u2013': '-', '\u201c': '"', '\u201d': '"'}
                    for line in text.split('\n'):
                        line = line.strip()
                        for char, rep in chars_to_replace.items():
                            line = line.replace(char, rep)
                        line = line.replace('**', '')
                        if not line:
                            pdf.ln(4)
                            continue
                        if re.match(r'^(\d+\.|###)', line):
                            pdf.set_font("Arial", 'B', 12)
                            pdf.set_text_color(*rm_blue)
                            pdf.multi_cell(0, 8, line.encode('latin-1', 'replace').decode('latin-1'))
                        else:
                            pdf.set_font("Arial", size=11)
                            pdf.set_text_color(40, 40, 40)
                            pdf.multi_cell(0, 7, line.encode('latin-1', 'replace').decode('latin-1'))
                    return pdf.output(dest='S').encode('latin-1')

                # --- 8. EXPORTAÇÃO E ENVIO ---
                st.markdown("<br>", unsafe_allow_html=True)
                col_down1, col_down2, col_down3 = st.columns(3)

                with col_down1:
                    pdf_bytes = create_pdf(raw_text)
                    st.download_button("📄 PDF Report", pdf_bytes, "Robotmaster_Audit.pdf", "application/pdf", use_container_width=True)

                with col_down2:
                    doc = Document()
                    doc.add_heading('Robotmaster V7 Audit', 0)
                    doc.add_paragraph(raw_text)
                    target = BytesIO()
                    doc.save(target)
                    st.download_button("📝 Word Doc", target.getvalue(), "Robotmaster_Audit.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)

                with col_down3:
                    email_receiver = "sales@robotmaster.com"
                    email_subject = "Robotmaster V7 Audit Report"
                    email_body = raw_text.replace('\n', '%0D%0A')
                    mailto_link = f"mailto:{email_receiver}?subject={email_subject}&body={email_body}"
                    st.markdown(f'<a href="{mailto_link}" style="text-decoration:none;"><div style="background-color:#005a9c;color:white;padding:10px;text-align:center;border-radius:5px;font-weight:bold;height:38px;line-height:18px;">📧 Email</div></a>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"AI Error: {e}")

except Exception as e:
    st.error(f"File Error: {e}")