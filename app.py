import streamlit as st
import PyPDF2
import os
from google import genai

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Robotmaster OLP Auditor", page_icon="🤖", layout="centered")

# --- HEADER REFINADO (Design Robotmaster) ---
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.image("LOGO_Robotmaster_RGB.png", use_container_width=True)

st.markdown("<h2 style='text-align: center; color: #D32F2F;'>OLP Project Auditor</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555555;'>Upload the client's technical scope (PDF) for instant feasibility analysis and V7 licensing recommendations.</p>", unsafe_allow_html=True)
st.write("---")

# --- API KEY SETUP (Invisível para o Usuário) ---
api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    st.error("⚠️ Configuração de API não encontrada nos Secrets do Streamlit.")
    st.stop()

# --- ACCESS CONFIGURATION (Behind the scenes) ---
api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    st.error("⚠️ Configuration Error: API Key not found in Secrets.")
    st.stop()

# --- 2. CLEAN INTERFACE (No Redundancy) ---
# Adiciona apenas um espaço e o campo de upload
st.markdown("<br>", unsafe_allow_html=True) 

uploaded_file = st.file_uploader("Upload Client RFP / Machinery Scope (PDF)", type="pdf")

if not uploaded_file:
    st.info("💡 Please upload the technical scope to start the analysis.")
    st.stop()

# Campo único de upload - sem caixas extras
uploaded_file = st.file_uploader("Upload Client RFP / Machinery Scope (PDF)", type="pdf")

if not uploaded_file:
    st.info("💡 Please upload a PDF file to start the audit.")
    st.stop() # Isso "limpa" o resto da tela até que o arquivo seja enviado

# The field where the user drops the file
uploaded_file = st.file_uploader("Upload Client RFP / Machinery Scope (PDF)", type="pdf")

if not uploaded_file:
    st.info("💡 Please upload a PDF file to start the automated auditing process.")
if uploaded_file:
    # O restante do seu código de análise continua aqui...
    # --- FILE UPLOADER ---
    uploaded_file = st.file_uploader("Upload Client RFP / Machinery Scope (PDF)", type="pdf")
    
    if uploaded_file is not None:
        with st.spinner("Extracting technical data..."):
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            pdf_text = ""
            for page in pdf_reader.pages:
                pdf_text += page.extract_text()
                
        st.success("Document read successfully!")
        
        if st.button("Analyze Project & Generate Proposal"):
            with st.spinner("AI Engineering Team is analyzing the scope..."):
                try:
                    system_instruction = """
                    You are the Senior Integration and Sales Engineer at Robotmaster. 
                    Your mission is to read the client's machinery scope and define the best Off-Line Programming (OLP) software architecture using Robotmaster V7.
                    
                    Based on the provided document, you MUST generate a report with the following structure:
                    1. 📋 Machinery Summary
                    2. 🛒 Recommended V7 Modules
                    3. ⚙️ Post-Processor
                    4. 🚨 Technical Risk Alerts
                    5. 💡 Sales Pitch
                    
                    Respond strictly in English, using professional industrial robotics terminology.
                    """
                    
                    # Motor 2026 (google-genai)
                    client = genai.Client(api_key=api_key)
                    
                    prompt = f"{system_instruction}\n\nHere is the client's document:\n{pdf_text}"
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                    )
                    
                    st.markdown("### 📊 Engineering & Integration Report")
                    st.write(response.text)
                    
                except Exception as e:
                    st.error(f"An error occurred: {e}")
else:
    st.info("Please enter your Gemini API Key to proceed.")