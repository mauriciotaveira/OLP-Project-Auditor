import streamlit as st
import PyPDF2
import re
from google import genai

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Robotmaster OLP Auditor", page_icon="🤖", layout="centered")

# --- 2. HEADER (Design Robotmaster) ---
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.image("LOGO_Robotmaster_RGB.png", use_container_width=True)

st.markdown("<h2 style='text-align: center; color: #D32F2F;'>OLP Project Auditor</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555555;'>Instant technical viability analysis and V7 licensing recommendations.</p>", unsafe_allow_html=True)
st.write("---")

# --- 3. ACCESS CONFIGURATION ---
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
                Your mission is to read the client's machinery scope and define the best OLP software architecture using Robotmaster V7.
                
                Structure your report as follows:
                1. 📋 Machinery Summary
                2. 🛒 Recommended V7 Modules
                3. ⚙️ Post-Processor
                4. 🚨 Technical Risk Alerts
                5. 💡 Sales Pitch
                
                Respond strictly in English, using professional industrial robotics terminology.
                """
                
                prompt = f"{system_instruction}\n\nDocument Content:\n{pdf_text}"
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                
                # --- 6. EXIBIÇÃO DO RELATÓRIO (Design Premium) ---
                st.markdown("---")
                st.markdown("### 📊 Engineering & Integration Report")
                
                # Tratamento de texto para legibilidade máxima
                raw_text = response.text
                # Remove asteriscos e coloca títulos em Vermelho Robotmaster
                processed_text = re.sub(r'\*\*(.*?)\*\*', r'<b style="color:#D32F2F; font-size:1.15em; display:inline-block; margin-top:15px;">\1</b>', raw_text)
                processed_text = processed_text.replace('* ', '• ')
                processed_text = processed_text.replace('\n', '<br>')

                report_html = f"""
                <div style="
                    background-color: #ffffff; 
                    padding: 40px; 
                    border-radius: 15px; 
                    border: 1px solid #d1d1d1; 
                    box-shadow: 0px 10px 30px rgba(0,0,0,0.1);
                    font-family: 'Segoe UI', Helvetica, Arial, sans-serif;
                    color: #222222;
                    line-height: 1.8;
                    font-size: 17px;
                    max-width: 850px;
                    margin: auto;
                ">
                    <div style="text-align: right; color: #bbb; font-size: 10px; letter-spacing: 1px; font-weight: bold;">ROBOTMASTER V7 OFFICIAL AUDIT</div>
                    <br>
                    {processed_text}
                </div>
                """
                st.markdown(report_html, unsafe_allow_html=True)
                
                # --- 7. EXPORTAÇÃO (PDF e DOCX) ---
                st.markdown("<br>", unsafe_allow_html=True)
                
                from fpdf import FPDF
                from docx import Document
                from io import BytesIO

                # Prepara os containers de download
                col_down1, col_down2 = st.columns(2)

                # --- Gerador de PDF "Designer" (Azul Robotmaster & Títulos Destacados) ---
                def create_pdf(text):
                    pdf = FPDF()
                    pdf.add_page()
                    
                    # Definição do Azul Robotmaster Oficial
                    rm_blue = (0, 90, 156) 
                    
                    # 1. CABEÇALHO COM LOGO E TÍTULO
                    try:
                        # Tenta colocar o logo no canto superior esquerdo
                        pdf.image("LOGO_Robotmaster_RGB.png", 10, 8, 33)
                    except:
                        pass # Se o arquivo não existir no GitHub, ele segue sem o logo
                    
                    pdf.set_font("Arial", 'B', 16)
                    pdf.set_text_color(*rm_blue)
                    pdf.cell(0, 10, "Engineering & Integration Report", ln=True, align='R')
                    
                    pdf.set_font("Arial", 'I', 10)
                    pdf.set_text_color(120, 120, 120)
                    pdf.cell(0, 8, "Robotmaster V7 OLP Audit", ln=True, align='R')
                    
                    # Linha Azul Decorativa
                    pdf.set_draw_color(*rm_blue)
                    pdf.line(10, 35, 200, 35)
                    pdf.ln(15)

                    # 2. PROCESSAMENTO DO TEXTO
                    pdf.set_font("Arial", size=11)
                    pdf.set_text_color(40, 40, 40) # Cinza escuro profissional

                    for line in text.split('\n'):
                        line = line.strip()
                        if not line:
                            pdf.ln(4)
                            continue
                        
                        # LOGICA DE TÍTULOS: Se a linha começar com "1.", "2." ou "###"
                        if re.match(r'^(\d+\.|###)', line):
                            pdf.ln(4)
                            pdf.set_font("Arial", 'B', 14)
                            pdf.set_text_color(*rm_blue)
                            # Limpa os símbolos de Markdown para o PDF ficar limpo
                            clean_title = line.replace('###', '').replace('**', '').strip()
                            pdf.multi_cell(0, 10, clean_title)
                            pdf.set_font("Arial", size=11)
                            pdf.set_text_color(40, 40, 40) # Volta para o texto normal
                        else:
                            # Texto normal e Bullets
                            pdf.set_font("Arial", size=11)
                            # Limpeza de caracteres especiais para evitar erro no FPDF 1.7
                            clean_line = line.replace('\u2022', '-').replace('\u2013', '-').replace('**', '')
                            pdf.multi_cell(0, 7, clean_line.encode('latin-1', 'replace').decode('latin-1'))

                    return pdf.output(dest='S').encode('latin-1')

                # --- Gerador de DOCX ---
                def create_docx(text):
                    doc = Document()
                    doc.add_heading('Robotmaster V7 - Engineering Report', 0)
                    p = doc.add_paragraph(text)
                    target = BytesIO()
                    doc.save(target)
                    return target.getvalue()

                with col_down1:
                    try:
                        pdf_data = create_pdf(raw_text)
                        st.download_button(
                            label="📄 Download Report (PDF)",
                            data=pdf_data,
                            file_name="Robotmaster_V7_Audit.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error("Error generating PDF")

                with col_down2:
                    try:
                        docx_data = create_docx(raw_text)
                        st.download_button(
                            label="📝 Download Report (Word)",
                            data=docx_data,
                            file_name="Robotmaster_V7_Audit.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error("Error generating Word doc")
                
            except Exception as e:
                if "429" in str(e):
                    st.warning("🚀 Model is warming up. Please wait 30 seconds and click again.")
                else:
                    st.error(f"AI Error: {e}")

except Exception as e:
    st.error(f"File Error: {e}")