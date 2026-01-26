"""
SQLAlchemy database models for the exam checker system
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Course(Base):
    """Course information"""
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    department = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    question_papers = relationship("QuestionPaper", back_populates="course")


class QuestionPaper(Base):
    """Question paper metadata"""
    __tablename__ = "question_papers"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    pdf_path = Column(String(500), nullable=False)
    total_marks = Column(Integer, nullable=False)
    exam_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    
    # Relationships
    course = relationship("Course", back_populates="question_papers")
    questions = relationship("Question", back_populates="question_paper")
    answer_keys = relationship("AnswerKey", back_populates="question_paper")
    student_exams = relationship("StudentExam", back_populates="question_paper")


class Question(Base):
    """Individual questions with marks and Bloom's level"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    question_paper_id = Column(Integer, ForeignKey("question_papers.id"), nullable=False)
    number = Column(String(20), nullable=False)  # Q1, Q2a, etc.
    text = Column(Text, nullable=False)
    max_marks = Column(Integer, nullable=False)
    bloom_level = Column(String(50), nullable=True)  # Remember, Understand, Apply, etc.
    question_type = Column(String(50), nullable=True)  # text, math, code, diagram, mcq
    
    # Relationships
    question_paper = relationship("QuestionPaper", back_populates="questions")
    model_answers = relationship("ModelAnswer", back_populates="question")
    student_answers = relationship("StudentAnswer", back_populates="question")


class AnswerKey(Base):
    """Answer key metadata"""
    __tablename__ = "answer_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    question_paper_id = Column(Integer, ForeignKey("question_papers.id"), nullable=False)
    pdf_path = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    
    # Relationships
    question_paper = relationship("QuestionPaper", back_populates="answer_keys")
    model_answers = relationship("ModelAnswer", back_populates="answer_key")


class ModelAnswer(Base):
    """Model answers with keywords and marking scheme"""
    __tablename__ = "model_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    answer_key_id = Column(Integer, ForeignKey("answer_keys.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    text = Column(Text, nullable=False)
    keywords_json = Column(JSON, nullable=True)  # List of key concepts
    marking_scheme_json = Column(JSON, nullable=True)  # Detailed marking rubric
    
    # Relationships
    answer_key = relationship("AnswerKey", back_populates="model_answers")
    question = relationship("Question", back_populates="model_answers")


class StudentExam(Base):
    """Student exam metadata"""
    __tablename__ = "student_exams"
    
    id = Column(Integer, primary_key=True, index=True)
    question_paper_id = Column(Integer, ForeignKey("question_papers.id"), nullable=False)
    roll_number = Column(String(50), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    pdf_path = Column(String(500), nullable=False)
    status = Column(String(50), default="pending")  # pending, processing, completed, approved
    total_obtained = Column(Float, default=0.0)
    total_max = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(String(200), nullable=True)
    
    # Relationships
    question_paper = relationship("QuestionPaper", back_populates="student_exams")
    student_answers = relationship("StudentAnswer", back_populates="student_exam")


class StudentAnswer(Base):
    """Individual student answers with marks and feedback"""
    __tablename__ = "student_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    student_exam_id = Column(Integer, ForeignKey("student_exams.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    answer_text = Column(Text, nullable=True)  # Null if not attempted
    ocr_confidence = Column(Float, nullable=True)
    content_type = Column(String(50), nullable=True)  # text, math, code, diagram, mcq
    marks_awarded = Column(Float, default=0.0)
    max_marks = Column(Integer, nullable=False)
    feedback_json = Column(JSON, nullable=True)  # {feedback, strengths, improvements}
    needs_review = Column(Boolean, default=False)
    review_reason = Column(String(200), nullable=True)
    faculty_notes = Column(Text, nullable=True)
    is_attempted = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    evaluated_at = Column(DateTime, nullable=True)
    
    # Relationships
    student_exam = relationship("StudentExam", back_populates="student_answers")
    question = relationship("Question", back_populates="student_answers")
