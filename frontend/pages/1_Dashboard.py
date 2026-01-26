"""
Streamlit Dashboard - Upload and manage exam documents
"""
import streamlit as st
import os
import requests
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Dashboard - Exam Checker",
    page_icon="📊",
    layout="wide"
)

st.markdown("# 📊 Dashboard")
st.markdown("Upload question papers, answer keys, and student answer sheets")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Tabs for different uploads
tab1, tab2, tab3 = st.tabs(["📝 Question Paper", "🗝️ Answer Key", "📄 Student Answers"])

with tab1:
    st.markdown("### Upload Question Paper")
    
    col1, col2 = st.columns(2)
    
    with col1:
        course_code = st.text_input("Course Code", placeholder="e.g., CS101")
    
    with col2:
        total_marks = st.number_input("Total Marks", min_value=1, value=100)
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        key="question_paper"
    )
    
    if uploaded_file:
        st.info(f"📂 Selected file: {uploaded_file.name}")
        
        if st.button("Upload Question Paper", key="btn_upload_qp"):
            with st.spinner("Uploading..."):
                try:
                    files = {"file": uploaded_file}
                    params = {
                        "course_code": course_code or "UNKNOWN",
                    }
                    response = requests.post(
                        f"{BACKEND_URL}/api/documents/upload-question-paper",
                        files=files,
                        params=params,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"✅ {data['message']}")
                        st.json(data)
                    else:
                        st.error(f"❌ Upload failed: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")


with tab2:
    st.markdown("### Upload Answer Key")
    
    col1, col2 = st.columns(2)
    
    with col1:
        question_paper_id = st.number_input(
            "Question Paper ID",
            min_value=1,
            help="Select the corresponding question paper"
        )
    
    with col2:
        answer_type = st.selectbox(
            "Answer Type",
            ["Text", "Structured", "Mixed"]
        )
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        key="answer_key"
    )
    
    if uploaded_file:
        st.info(f"📂 Selected file: {uploaded_file.name}")
        
        if st.button("Upload Answer Key", key="btn_upload_ak"):
            with st.spinner("Uploading..."):
                try:
                    files = {"file": uploaded_file}
                    params = {
                        "question_paper_id": int(question_paper_id),
                    }
                    response = requests.post(
                        f"{BACKEND_URL}/api/documents/upload-answer-key",
                        files=files,
                        params=params,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"✅ {data['message']}")
                        st.json(data)
                    else:
                        st.error(f"❌ Upload failed: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")


with tab3:
    st.markdown("### Batch Upload Student Answer Sheets")
    
    col1, col2 = st.columns(2)
    
    with col1:
        question_paper_id = st.number_input(
            "Question Paper ID",
            min_value=1,
            key="qp_id_students",
            help="Select the corresponding question paper"
        )
    
    with col2:
        num_students = st.number_input(
            "Expected Number of Students",
            min_value=1,
            value=30
        )
    
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type="pdf",
        accept_multiple_files=True,
        key="student_answers"
    )
    
    if uploaded_files:
        st.info(f"📂 Selected {len(uploaded_files)} file(s)")
        
        for f in uploaded_files[:5]:  # Show first 5
            st.caption(f.name)
        
        if len(uploaded_files) > 5:
            st.caption(f"... and {len(uploaded_files) - 5} more")
        
        if st.button("Upload Student Answers", key="btn_upload_sa"):
            with st.spinner(f"Uploading {len(uploaded_files)} files..."):
                try:
                    files = [("files", f) for f in uploaded_files]
                    params = {
                        "question_paper_id": int(question_paper_id),
                    }
                    response = requests.post(
                        f"{BACKEND_URL}/api/documents/upload-student-answers",
                        files=files,
                        params=params,
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"✅ {data['message']}")
                        st.json(data)
                    else:
                        st.error(f"❌ Upload failed: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")


# Recent uploads section
st.markdown("---")
st.markdown("### 📋 Recent Uploads")

try:
    response = requests.get(f"{BACKEND_URL}/api/documents/documents/question_papers", timeout=10)
    if response.status_code == 200:
        data = response.json()
        docs = data.get("documents", [])
        
        if docs:
            for doc in docs[-5:]:  # Show last 5
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.caption(f"📚 {doc.get('course', 'Unknown')}")
                with col2:
                    st.caption(f"{'✅' if doc.get('processed') else '⏳'} {doc.get('created_at', 'N/A')}")
                with col3:
                    if st.button("View", key=f"view_{doc.get('id')}"):
                        st.json(doc)
        else:
            st.info("No documents uploaded yet")
    else:
        st.warning("Could not fetch documents from backend")
except Exception as e:
    st.warning(f"⚠️ Could not connect to backend: {str(e)}")
