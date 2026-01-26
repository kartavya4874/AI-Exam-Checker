"""
Streamlit Review Page - Faculty review and approval of automated grades
"""
import streamlit as st
import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Review Answers - Exam Checker",
    page_icon="✅",
    layout="wide"
)

st.markdown("# ✅ Review Answers")
st.markdown("Review automated grades, override marks, and add faculty comments")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Selection section
col1, col2, col3 = st.columns(3)

with col1:
    exam_id = st.number_input("Exam ID", min_value=1, value=1)

with col2:
    student_filter = st.selectbox(
        "Filter by Status",
        ["All", "Pending Review", "Flagged for Review", "Approved"]
    )

with col3:
    sort_by = st.selectbox(
        "Sort By",
        ["Student ID", "Marks", "Confidence"]
    )

# Tabs for different review modes
tab1, tab2, tab3 = st.tabs(["👥 Student-wise", "📋 Question-wise", "🚩 Flagged Answers"])

with tab1:
    st.markdown("### Review Student Marks")
    
    # Sample student data
    sample_students = [
        {"student_id": "STU001", "name": "John Doe", "total_marks": 65, "auto_marks": 60, "status": "Pending"},
        {"student_id": "STU002", "name": "Jane Smith", "total_marks": 78, "auto_marks": 75, "status": "Approved"},
        {"student_id": "STU003", "name": "Bob Wilson", "total_marks": 45, "auto_marks": 42, "status": "Flagged"},
    ]
    
    selected_student = st.selectbox(
        "Select Student",
        [s["student_id"] + " - " + s["name"] for s in sample_students]
    )
    
    if selected_student:
        student_id = selected_student.split(" - ")[0]
        
        # Create two columns for marks display
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Automated Marks", "60/100", delta="0")
        
        with col2:
            st.metric("Your Override", "65/100", delta="5")
        
        with col3:
            st.metric("Status", "Pending Review")
        
        st.markdown("---")
        
        # Question-wise marks table
        st.markdown("#### Question-wise Breakdown")
        
        questions_data = {
            "Question": ["Q1", "Q2a", "Q2b", "Q3"],
            "Marks": [15, 10, 15, 20],
            "Auto Grade": [12, 8, 14, 18],
            "Your Grade": [12, 8, 14, 18],
            "Confidence": ["95%", "85%", "90%", "98%"],
            "Action": ["✓", "✓", "✓", "✓"]
        }
        
        df = pd.DataFrame(questions_data)
        st.dataframe(df, use_container_width=True)
        
        st.markdown("---")
        
        # Review form
        st.markdown("#### Add Comments")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            comment = st.text_area(
                "Faculty Comment",
                placeholder="Add any comments or reasons for marks override",
                height=100
            )
        
        with col2:
            st.write("")
            st.write("")
            if st.button("Save Comment"):
                st.success("✅ Comment saved")
        
        # Override section
        st.markdown("#### Override Marks (if needed)")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            override_question = st.selectbox("Question", ["Q1", "Q2a", "Q2b", "Q3"])
        
        with col2:
            override_marks = st.number_input("New Marks", min_value=0, max_value=20, value=12)
        
        with col3:
            st.write("")
            st.write("")
            if st.button("Override Marks"):
                st.success(f"✅ Marks updated to {override_marks}")


with tab2:
    st.markdown("### Review Question-wise Answers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        question_select = st.selectbox(
            "Select Question",
            ["Q1", "Q2a", "Q2b", "Q3"]
        )
    
    with col2:
        review_type = st.selectbox(
            "Review Type",
            ["All Answers", "Flagged Only", "Low Confidence"]
        )
    
    st.markdown(f"#### Question {question_select} - Student Answers")
    
    # Sample answers
    answers = [
        {
            "student": "STU001",
            "answer": "The Renaissance was a cultural movement that originated in Italy during the 14th century...",
            "model_answer": "Renaissance was a period of European cultural transformation...",
            "auto_marks": 12,
            "confidence": 0.92,
            "status": "Approved"
        },
        {
            "student": "STU002",
            "answer": "Renaissance happened in Europe",
            "model_answer": "Renaissance was a period of European cultural transformation...",
            "auto_marks": 8,
            "confidence": 0.65,
            "status": "Flagged"
        }
    ]
    
    for idx, answer in enumerate(answers):
        with st.expander(f"👤 {answer['student']} - Marks: {answer['auto_marks']} (Confidence: {answer['confidence']:.0%})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Student Answer:**")
                st.text(answer["answer"])
                st.metric("Awarded Marks", answer["auto_marks"])
            
            with col2:
                st.markdown("**Model Answer:**")
                st.text(answer["model_answer"])
                st.metric("Confidence", f"{answer['confidence']:.0%}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                new_marks = st.number_input(
                    "Override Marks",
                    min_value=0,
                    max_value=15,
                    value=answer["auto_marks"],
                    key=f"marks_{idx}"
                )
            
            with col2:
                reason = st.text_input(
                    "Reason for change",
                    key=f"reason_{idx}"
                )
            
            with col3:
                st.write("")
                st.write("")
                if st.button("Update", key=f"btn_{idx}"):
                    st.success(f"✅ Marks updated to {new_marks}")


with tab3:
    st.markdown("### 🚩 Answers Flagged for Review")
    
    confidence_threshold = st.slider(
        "Show answers below confidence",
        min_value=0.0,
        max_value=1.0,
        value=0.75,
        step=0.05
    )
    
    st.markdown(f"#### Showing answers with confidence < {confidence_threshold:.0%}")
    
    # Flagged answers table
    flagged_data = {
        "Student": ["STU002", "STU005", "STU007"],
        "Question": ["Q2a", "Q3", "Q1"],
        "Confidence": ["65%", "70%", "68%"],
        "Auto Marks": [8, 15, 10],
        "Review Status": ["⏳ Pending", "⏳ Pending", "⏳ Pending"]
    }
    
    df_flagged = pd.DataFrame(flagged_data)
    st.dataframe(df_flagged, use_container_width=True)
    
    st.info(f"📊 Total flagged answers: {len(df_flagged)}")


# Approval section
st.markdown("---")
st.markdown("### 🔒 Approve All Marks")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Reviewed Answers", "12/15", delta="-3")

with col2:
    st.metric("Pending Approvals", "3", delta="-")

with col3:
    if st.button("Approve & Release Marks", key="btn_approve_all"):
        st.success("✅ All marks approved and ready for release to students!")
        st.balloons()

# Statistics
st.markdown("---")
st.markdown("### 📊 Review Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Students", 45)

with col2:
    st.metric("Reviewed", 43, delta="+2")

with col3:
    st.metric("Avg Marks", "68.5", delta="-2.3")

with col4:
    st.metric("Pass Rate", "78%", delta="+5%")
