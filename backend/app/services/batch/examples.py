"""
Example usage of parallel processing system
"""
from app.services.batch.parallel_processor import (
    ParallelProcessor,
    CourseEvaluationManager,
    evaluate_courses_parallel,
    evaluate_students_parallel
)


# Example 1: Evaluate multiple courses in parallel
def example_parallel_courses():
    """Example of evaluating multiple courses simultaneously"""
    
    # Sample course data
    courses = [
        {"course_code": "CS101", "name": "Data Structures"},
        {"course_code": "CS102", "name": "Algorithms"},
        {"course_code": "MATH201", "name": "Calculus"},
        {"course_code": "PHY101", "name": "Physics"},
    ]
    
    # Define evaluation function for one course
    def evaluate_single_course(course_data):
        """Process all students in one course"""
        course_code = course_data["course_code"]
        
        # Simulate processing
        print(f"Processing course: {course_code}")
        
        # In real implementation:
        # 1. Get all students for this course
        # 2. Process each student's answer sheet
        # 3. Evaluate all answers
        # 4. Generate feedback
        # 5. Store results
        
        return {
            "course_code": course_code,
            "students_processed": 50,
            "avg_marks": 72.5,
            "status": "completed"
        }
    
    # Evaluate all courses in parallel
    results = evaluate_courses_parallel(
        courses=courses,
        evaluation_function=evaluate_single_course,
        max_workers=4  # Use 4 parallel workers
    )
    
    print(f"\nResults:")
    print(f"Total courses: {results['total_courses']}")
    print(f"Successful: {results['successful']}")
    print(f"Failed: {results['failed']}")
    print(f"Total time: {results['elapsed_time']}s")
    print(f"Avg time per course: {results['avg_time_per_course']}s")


# Example 2: Evaluate students within a course in parallel
def example_parallel_students():
    """Example of evaluating students in parallel"""
    
    # Sample student data
    students = [
        {"roll_number": "CS2021001", "name": "Student 1"},
        {"roll_number": "CS2021002", "name": "Student 2"},
        {"roll_number": "CS2021003", "name": "Student 3"},
        # ... more students
    ]
    
    # Define evaluation function for one student
    def evaluate_single_student(student_data):
        """Evaluate one student's answer sheet"""
        roll_number = student_data["roll_number"]
        
        print(f"Evaluating student: {roll_number}")
        
        # In real implementation:
        # 1. OCR the answer sheet
        # 2. Extract answers
        # 3. Evaluate each answer
        # 4. Generate feedback
        # 5. Calculate total marks
        
        return {
            "roll_number": roll_number,
            "total_marks": 75.5,
            "status": "completed"
        }
    
    # Evaluate all students in parallel
    results = evaluate_students_parallel(
        students=students,
        evaluation_function=evaluate_single_student,
        max_workers=8,  # Use 8 parallel workers
        batch_size=10   # Process in batches of 10
    )
    
    print(f"\nResults:")
    print(f"Total students: {results['total_students']}")
    print(f"Successful: {results['successful']}")
    print(f"Failed: {results['failed']}")


# Example 3: Using CourseEvaluationManager
def example_course_manager():
    """Example using CourseEvaluationManager"""
    
    manager = CourseEvaluationManager(max_workers=4)
    
    courses = [
        {"course_code": "CS101"},
        {"course_code": "CS102"},
        {"course_code": "MATH201"},
    ]
    
    def full_course_pipeline(course_data):
        """Complete evaluation pipeline for one course"""
        # This would include:
        # - Loading question paper
        # - Loading answer key
        # - Processing all students
        # - Generating reports
        return {"course_code": course_data["course_code"], "status": "done"}
    
    results = manager.evaluate_multiple_courses(
        courses_data=courses,
        evaluation_pipeline=full_course_pipeline
    )
    
    return results


# Example 4: Celery-based parallel processing
def example_celery_parallel():
    """Example using Celery for distributed processing"""
    
    from app.services.batch.tasks import evaluate_course_parallel_task
    
    # Submit multiple courses for parallel evaluation
    course_ids = [1, 2, 3, 4, 5]
    
    # This will be processed by Celery workers
    task = evaluate_course_parallel_task.delay(course_ids)
    
    print(f"Task submitted: {task.id}")
    print("Celery workers will process courses in parallel")
    
    # Check task status
    # result = task.get(timeout=3600)  # Wait up to 1 hour
    
    return task.id


if __name__ == "__main__":
    print("Example 1: Parallel Course Evaluation")
    print("=" * 50)
    example_parallel_courses()
    
    print("\n\nExample 2: Parallel Student Evaluation")
    print("=" * 50)
    example_parallel_students()
