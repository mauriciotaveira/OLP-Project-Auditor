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
                1. Machinery Summary
                2. Recommended V7 Modules
                3. Post-Processor
                4. Technical Risk Alerts
                5. Sales Pitch
                
                Respond strictly in English, using professional industrial robotics terminology. Do not use emojis in the content.
                """
                
                prompt = f"{system_instruction}\n\nDocument Content:\n{pdf_text}"
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                
                raw_text = response.text

                # --- 6. EXIBIÇÃO NA TELA (Design Premium Corrigido) ---
                st.markdown("---")
                
                raw_text = response.text
                
                # 1. Ajuste dos Títulos Principais (1., 2., 3., etc.)
                # Colocamos fonte 24px (maior), Azul Robotmaster (#005a9c) e um traço fino embaixo
                processed_html = re.sub(
                    r'^(\d+\..*?)$', 
                    r'<h3 style="color:#005a9c; font-size:24px; margin-top:30px; margin-bottom:10px; border-bottom: 1px solid #f0f0f0; font-weight: bold;">\1</h3>', 
                    raw_text, flags=re.MULTILINE
                )
                
                # 2. Ajuste de títulos estilo Markdown ### (se a IA usar)
                processed_html = re.sub(
                    r'^### (.*?)$', 
                    r'<h3 style="color:#005a9c; font-size:24px; margin-top:30px; margin-bottom:10px; font-weight: bold;">\1</h3>', 
                    processed_html, flags=re.MULTILINE
                )

                # 3. Ajuste dos Subtítulos (texto entre **)
                # Mantemos o negrito, mas com fonte 17px (menor que o título azul) e cor grafite
                processed_html = re.sub(
                    r'\*\*(.*?)\*\*', 
                    r'<b style="color:#444444; font-size:17px; font-weight: bold;">\1</b>', 
                    processed_html
                )

                # 4. Ajustes de quebras e bullets
                processed_html = processed_html.replace('\n', '<br>')

                st.markdown(f"""
                <div style="
                    background-color: #ffffff; 
                    padding: 45px; 
                    border-radius: 15px; 
                    border: 1px solid #d1d1d1; 
                    box-shadow: 0px 10px 40px rgba(0,0,0,0.1);
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    color: #333333;
                    line-height: 1.8;
                ">
                    <div style="text-align: right; color: #ccc; font-size: 11px; font-weight: bold; letter-spacing: 2px;">OFFICIAL ENGINEERING AUDIT</div>
                    <div style="font-size: 16px;">
                        {processed_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # --- 7. FUNÇÃO GERADORA DE PDF (Design com Títulos Destacados) ---
                def create_pdf(text):
                    pdf = FPDF()
                    pdf.add_page()
                    rm_blue = (0, 90, 156) # Azul Robotmaster Oficial
                    
                    # 1. CABEÇALHO COM LOGO
                    try:
                        pdf.image("LOGO_Robotmaster_RGB.png", 10, 8, 33)
                    except:
                        pass
                    
                    pdf.set_font("Arial", 'B', 16)
                    pdf.set_text_color(*rm_blue)
                    pdf.cell(0, 10, "Engineering & Integration Report", ln=True, align='R')
                    pdf.set_font("Arial", 'I', 10)
                    pdf.set_text_color(120, 120, 120)
                    pdf.cell(0, 8, "Robotmaster V7 OLP Audit", ln=True, align='R')
                    pdf.line(10, 35, 200, 35)
                    pdf.ln(15)

                    # 2. LIMPEZA E FORMATAÇÃO
                    pdf.set_text_color(40, 40, 40) # Cinza escuro para o corpo

                    # Dicionário de limpeza para evitar erros de caractere
                    chars_to_replace = {
                        '\u2022': '-', '\u2013': '-', '\u2014': '-', '\u201c': '"', 
                        '\u201d': '"', '\u2018': "'", '\u2019': "'", '📋': '', 
                        '🛒': '', '⚙️': '', '🚨': '', '💡': '', '📊': ''
                    }
                    
                    for line in text.split('\n'):
                        line = line.strip()
                        for char, rep in chars_to_replace.items():
                            line = line.replace(char, rep)
                        
                        # Guardamos se a linha original tinha negrito (**) antes de limpar
                        is_bold_sub = '**' in line
                        line = line.replace('**', '')

                        if not line:
                            pdf.ln(4)
                            continue

                        # --- LÓGICA DE TAMANHOS ---
                        # Títulos Principais (1., 2., ###, Subject, Dear)
                        if re.match(r'^(\d+\.|###|Subject:|Dear)', line):
                            pdf.set_font("Arial", 'B', 12) # Tamanho 12
                            pdf.set_text_color(*rm_blue)   # Azul Robotmaster
                            pdf.multi_cell(0, 8, line.encode('latin-1', 'replace').decode('latin-1'))
                            pdf.ln(2)
                        
                        # Subtítulos ou destaques no meio do texto
                        elif is_bold_sub:
                            pdf.set_font("Arial", 'B', 11) # Mesmo tamanho do corpo, mas Negrito
                            pdf.set_text_color(40, 40, 40) # Cinza escuro
                            pdf.multi_cell(0, 7, line.encode('latin-1', 'replace').decode('latin-1'))
                        
                        # Texto Normal
                        else:
                            pdf.set_font("Arial", size=11)
                            pdf.set_text_color(40, 40, 40)
                            pdf.multi_cell(0, 7, line.encode('latin-1', 'replace').decode('latin-1'))
                    
                    return pdf.output(dest='S').encode('latin-1')

                    # Limpeza de caracteres para o PDF não quebrar
                    chars_to_replace = {
                        '\u2022': '-', '\u2013': '-', '\u2014': '-', '\u201c': '"', 
                        '\u201d': '"', '\u2018': "'", '\u2019': "'", '📋': '', 
                        '🛒': '', '⚙️': '', '🚨': '', '💡': '', '📊': ''
                    }
                    
                    for line in text.split('\n'):
                        line = line.strip()
                        for char, rep in chars_to_replace.items():
                            line = line.replace(char, rep)
                        line = line.replace('**', '')

                        if not line:
                            pdf.ln(4)
                            continue

                        # Títulos em Azul
                        if re.match(r'^(\d+\.|###|Subject:|Dear)', line):
                            pdf.set_font("Arial", 'B', 12)
                            pdf.set_text_color(*rm_blue)
                            pdf.multi_cell(0, 8, line.encode('latin-1', 'replace').decode('latin-1'))
                            pdf.ln(2)
                        else:
                            pdf.set_font("Arial", size=11)
                            pdf.set_text_color(40, 40, 40)
                            pdf.multi_cell(0, 7, line.encode('latin-1', 'replace').decode('latin-1'))
                    
                    return pdf.output(dest='S').encode('latin-1')

                # --- 8. BOTÕES DE DOWNLOAD ---
                st.markdown("<br>", unsafe_allow_html=True)
                col_down1, col_down2 = st.columns(2)

                with col_down1:
                    try:
                        pdf_bytes = create_pdf(raw_text)
                        st.download_button(
                            label="📄 Download PDF Report",
                            data=pdf_bytes,
                            file_name="Robotmaster_V7_Report.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"PDF Error: {e}")

                with col_down2:
                    try:
                        doc = Document()
                        doc.add_heading('Robotmaster V7 Audit', 0)
                        doc.add_paragraph(raw_text)
                        target = BytesIO()
                        doc.save(target)
                        st.download_button(
                            label="📝 Download Word Doc",
                            data=target.getvalue(),
                            file_name="Robotmaster_V7_Report.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Word Error: {e}")

            except Exception as e:
                st.error(f"AI Error: {e}")

except Exception as e:
    st.error(f"File Error: {e}")