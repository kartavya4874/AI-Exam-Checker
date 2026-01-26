"""
Streamlit Home Page - Main entry point for the Exam Checker System
"""
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Exam Checker System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .feature-box {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🎓 Exam Checker System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Universal Automated Exam Evaluation for Universities</div>', unsafe_allow_html=True)

# Main content
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📝 Upload Documents")
    st.info("""
    **Setup Phase:**
    - Upload Question Papers
    - Upload Answer Keys
    - Review extracted questions
    """)

with col2:
    st.markdown("### 🤖 AI Evaluation")
    st.success("""
    **Automated Grading:**
    - Text answers
    - Math equations
    - Code solutions
    - Diagrams & MCQs
    """)

with col3:
    st.markdown("### ✅ Faculty Review")
    st.warning("""
    **Final Approval:**
    - Review all marks
    - Override decisions
    - Add comments
    - Export results
    """)

# Features section
st.markdown("---")
st.markdown("## 🌟 Key Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### ✅ Multi-Format OCR
    - Handwritten text recognition
    - Math equation extraction
    - Code block detection
    - Diagram label extraction
    
    #### ✅ Smart Question Mapping
    - Handles out-of-order answers
    - Detects unattempted questions
    - Sub-question support (Q1a, Q1b)
    """)

with col2:
    st.markdown("""
    #### ✅ Content-Aware Evaluation
    - Theory: Concept coverage & accuracy
    - Math: Step-wise partial credit
    - Code: Logic-based (no execution)
    - Diagrams: Label matching + review
    
    #### ✅ Faculty Control
    - Override any auto-grade
    - Add detailed comments
    - Approve before release
    - Export to Excel/PDF
    """)

# System status
st.markdown("---")
st.markdown("## 🔧 System Status")

# Check backend connection
backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")

try:
    import requests
    response = requests.get(f"{backend_url}/health", timeout=5)
    if response.status_code == 200:
        data = response.json()
        st.success("✅ Backend connected")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Database", "✅ Connected" if data.get("database") == "connected" else "❌ Disconnected")
        with col2:
            st.metric("Gemini API", "✅ Configured" if data.get("gemini_api") == "configured" else "⚠️ Not configured")
        with col3:
            st.metric("OCR API", "✅ Configured" if data.get("ocr_api") == "configured" else "⚠️ Not configured")
    else:
        st.error("❌ Backend connection failed")
except Exception as e:
    st.warning(f"⚠️ Backend not reachable at {backend_url}")
    st.info("Make sure the backend is running: `uvicorn app.main:app --reload`")

# Quick start guide
st.markdown("---")
st.markdown("## 🚀 Quick Start Guide")

with st.expander("📖 How to use this system"):
    st.markdown("""
    ### Setup Phase (One-time per exam)
    
    1. **Upload Question Paper**
       - Navigate to Dashboard page
       - Upload question paper PDF
       - Review extracted questions and marks
    
    2. **Upload Answer Key**
       - Upload answer key PDF
       - Review model answers
       - Approve keywords and marking scheme
    
    ### Evaluation Phase (Per student batch)
    
    3. **Upload Student Answer Sheets**
       - Batch upload all student PDFs
       - System automatically processes each sheet
       - AI evaluates all answers
    
    4. **Review & Approve**
       - Go to Review Answers page
       - Check flagged answers
       - Override marks if needed
       - Add faculty comments
       - Approve final marks
    
    5. **Export Results**
       - Go to Export Results page
       - Download Excel or PDF reports
       - Share with students
    """)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>Built with ❤️ for universities worldwide</p>
        <p>Powered by FastAPI, Streamlit, and Gemini AI</p>
    </div>
""", unsafe_allow_html=True)
