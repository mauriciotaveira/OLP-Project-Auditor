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
                
                st.markdown("---")
                st.markdown("### 📊 Engineering & Integration Report")
                st.write(response.text)
                
            except Exception as e:
                if "429" in str(e):
                    st.warning("🚀 Model is warming up. Please wait 30 seconds and click again.")
                else:
                    st.error(f"AI Error: {e}")

except Exception as e:
    st.error(f"File Error: {e}")