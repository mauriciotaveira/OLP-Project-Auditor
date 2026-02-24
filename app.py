import streamlit as st
import PyPDF2
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
# Se chegou aqui, é porque o arquivo foi carregado
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
                
                # Container elegante: Fundo branco, texto grafite, sem azul.
                report_html = f"""
                <div style="
                    background-color: #ffffff; 
                    padding: 30px; 
                    border-radius: 12px; 
                    border: 1px solid #d1d1d1; 
                    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
                    font-family: 'Segoe UI', Helvetica, Arial, sans-serif;
                    color: #1a1a1a;
                    line-height: 1.6;
                    font-size: 16px;
                ">
                    {response.text.replace('\n', '<br>')}
                </div>
                """
                # --- 6. EXIBIÇÃO DO RELATÓRIO (Design Premium & Legibilidade) ---
                st.markdown("---")
                
                # Tratamento do texto para remover excesso de asteriscos e formatar seções
                import re
                processed_text = response.text
                processed_text = processed_text.replace('---', '<hr style="border:0; height:1px; background:#e0e0e0; margin:20px 0;">')
                processed_text = re.sub(r'\*\*(.*?)\*\*', r'<b style="color:#D32F2F; font-size:18px;">\1</b>', processed_text) # Títulos em Vermelho Robotmaster
                processed_text = processed_text.replace('* ', '• ') # Bullet points mais limpos
                processed_text = processed_text.replace('\n', '<br>')

                report_html = f"""
                <div style="
                    background-color: #ffffff; 
                    padding: 40px; 
                    border-radius: 15px; 
                    border: 1px solid #d1d1d1; 
                    box-shadow: 0px 10px 30px rgba(0,0,0,0.1);
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    color: #333333;
                    line-height: 1.8;
                    font-size: 17px;
                    max-width: 900px;
                    margin: auto;
                ">
                    <div style="text-align: right; color: #999; font-size: 12px;">OFFICIAL TECHNICAL REPORT V7</div>
                    <br>
                    {processed_text}
                </div>
                """
                st.markdown(report_html, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.download_button(
                    label="📥 Download Official Proposal (.txt)",
                    data=response.text,
                    file_name="Robotmaster_V7_Proposal.txt",
                    mime="text/plain"
                )