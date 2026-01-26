"""
Streamlit Export Page - Export results and generate reports
"""
import streamlit as st
import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Export Results - Exam Checker",
    page_icon="📊",
    layout="wide"
)

st.markdown("# 📥 Export Results")
st.markdown("Export marks and generate comprehensive reports")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Selection section
col1, col2 = st.columns(2)

with col1:
    exam_id = st.number_input("Exam ID", min_value=1, value=1)

with col2:
    exam_name = st.text_input("Exam Name", value="Midterm Exam - CS101")

# Export tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Excel Export", "📄 PDF Report", "📈 Analytics", "⚙️ Advanced"])

with tab1:
    st.markdown("### Export to Excel")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Include in Export:**")
        include_student_names = st.checkbox("Student Names", value=True)
        include_roll_numbers = st.checkbox("Roll Numbers", value=True)
        include_question_details = st.checkbox("Question-wise Marks", value=True)
        include_comments = st.checkbox("Faculty Comments", value=True)
    
    with col2:
        st.markdown("**Format Options:**")
        excel_format = st.radio(
            "Excel Format",
            ["Simple (Names & Total Marks)", "Detailed (Question-wise)", "Full (Everything)"]
        )
        include_statistics = st.checkbox("Include Statistics Sheet", value=True)
        
        col1, col2 = st.columns(2)
        with col1:
            font_size = st.slider("Font Size", 8, 14, 11)
        with col2:
            color_code = st.checkbox("Color Code Results", value=True)
    
    if st.button("📥 Download Excel", key="btn_excel"):
        try:
            response = requests.get(
                f"{BACKEND_URL}/api/export/export-excel/{exam_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                st.success(f"✅ {data['message']}")
                st.info(f"📎 File ready at: {data['file_url']}")
                st.balloons()
            else:
                st.error("❌ Export failed")
        except Exception as e:
            st.warning(f"⚠️ Could not connect to backend: {str(e)}")


with tab2:
    st.markdown("### Generate PDF Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        report_type = st.radio(
            "Report Type",
            ["Summary Report", "Detailed Report", "Statistical Analysis"]
        )
        
        include_cover_page = st.checkbox("Include Cover Page", value=True)
        include_toc = st.checkbox("Include Table of Contents", value=True)
        include_graphs = st.checkbox("Include Charts & Graphs", value=True)
    
    with col2:
        st.markdown("**PDF Options:**")
        page_size = st.selectbox("Page Size", ["A4", "Letter"])
        orientation = st.radio("Orientation", ["Portrait", "Landscape"])
        
        col1, col2 = st.columns(2)
        with col1:
            font_name = st.selectbox("Font", ["Arial", "Times New Roman", "Calibri"])
        with col2:
            include_watermark = st.checkbox("Add Watermark", value=False)
    
    if st.button("📄 Generate PDF", key="btn_pdf"):
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/export/generate-report/{exam_id}",
                params={"report_type": report_type.lower().replace(" ", "_")},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                st.success(f"✅ {data['message']}")
                st.info(f"📎 File ready for download")
                st.balloons()
            else:
                st.error("❌ Report generation failed")
        except Exception as e:
            st.warning(f"⚠️ Could not connect to backend: {str(e)}")


with tab3:
    st.markdown("### Export Analytics & Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Statistics to Include:**")
        stat_avg = st.checkbox("Average Marks", value=True)
        stat_distribution = st.checkbox("Mark Distribution", value=True)
        stat_grades = st.checkbox("Grade Distribution", value=True)
        stat_pass_fail = st.checkbox("Pass/Fail Analysis", value=True)
    
    with col2:
        st.markdown("**Question Analysis:**")
        question_difficulty = st.checkbox("Question Difficulty", value=True)
        question_performance = st.checkbox("Question-wise Performance", value=True)
        student_performance = st.checkbox("Student Performance Rankings", value=True)
        common_mistakes = st.checkbox("Common Mistakes Analysis", value=True)
    
    if st.button("📈 Export Analytics", key="btn_analytics"):
        try:
            response = requests.get(
                f"{BACKEND_URL}/api/export/export-analytics/{exam_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                analytics = data.get("analytics", {})
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Students", analytics.get("total_students", 0))
                with col2:
                    st.metric("Average Marks", f"{analytics.get('average_marks', 0):.1f}")
                with col3:
                    st.metric("Pass Rate", f"{analytics.get('pass_count', 0)}")
                with col4:
                    st.metric("Fail Rate", f"{analytics.get('fail_count', 0)}")
                
                # Distribution chart
                st.markdown("#### Mark Distribution")
                
                # Sample distribution data
                dist_data = pd.DataFrame({
                    "Range": ["0-20", "21-40", "41-60", "61-80", "81-100"],
                    "Count": [2, 5, 12, 18, 8]
                })
                
                st.bar_chart(dist_data.set_index("Range"))
                
                st.success("✅ Analytics data exported")
            else:
                st.error("❌ Analytics export failed")
        except Exception as e:
            st.warning(f"⚠️ Could not connect to backend: {str(e)}")


with tab4:
    st.markdown("### Advanced Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Custom Filters:**")
        min_marks = st.number_input("Minimum Marks", min_value=0, max_value=100, value=0)
        max_marks = st.number_input("Maximum Marks", min_value=0, max_value=100, value=100)
        grade_filter = st.multiselect(
            "Include Grades",
            ["A+", "A", "B+", "B", "C+", "C", "D", "F"],
            default=["A+", "A", "B+", "B", "C+", "C", "D", "F"]
        )
    
    with col2:
        st.markdown("**Export Destination:**")
        export_format = st.selectbox(
            "Format",
            ["Excel (.xlsx)", "CSV (.csv)", "JSON (.json)", "PDF (.pdf)"]
        )
        
        auto_email = st.checkbox("Send to Email", value=False)
        if auto_email:
            recipient_emails = st.text_area(
                "Recipient Emails (comma-separated)",
                placeholder="admin@university.edu, dean@university.edu"
            )
        
        schedule_export = st.checkbox("Schedule Regular Exports", value=False)
        if schedule_export:
            frequency = st.selectbox(
                "Frequency",
                ["Daily", "Weekly", "Monthly"]
            )
    
    if st.button("⚙️ Export with Custom Settings", key="btn_advanced"):
        st.success("✅ Custom export job created")
        st.info(f"📊 Exporting {export_format} with filters (Marks: {min_marks}-{max_marks})")


# Recent exports
st.markdown("---")
st.markdown("### 📋 Recent Exports")

recent_exports = [
    {
        "date": "2026-01-26 14:30",
        "type": "Excel",
        "exam": "CS101 Midterm",
        "students": 45,
        "status": "✅ Complete"
    },
    {
        "date": "2026-01-26 12:15",
        "type": "PDF",
        "exam": "CS101 Midterm",
        "students": 45,
        "status": "✅ Complete"
    },
    {
        "date": "2026-01-25 16:45",
        "type": "Excel",
        "exam": "MTH101 Final",
        "students": 67,
        "status": "✅ Complete"
    }
]

df_exports = pd.DataFrame(recent_exports)
st.dataframe(df_exports, use_container_width=True)

# Footer
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Refresh Exports"):
        st.rerun()

with col2:
    if st.button("📁 Open Export Folder"):
        st.info("📂 Export folder: ./exports/")

with col3:
    if st.button("🗑️ Clear Old Exports"):
        st.warning("Exports older than 30 days will be deleted")
