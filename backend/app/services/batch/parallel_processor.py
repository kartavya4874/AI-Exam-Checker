"""
Parallel Processing System
Enables concurrent evaluation of multiple courses using multiprocessing
"""
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import Dict, List, Callable, Any, Optional
import time
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ParallelProcessor:
    """Manages parallel processing of multiple courses/batches"""
    
    def __init__(self, max_workers: Optional[int] = None, use_processes: bool = True):
        """
        Initialize parallel processor
        
        Args:
            max_workers: Maximum number of parallel workers (default: CPU count)
            use_processes: If True, use ProcessPoolExecutor (CPU-bound tasks)
                          If False, use ThreadPoolExecutor (I/O-bound tasks)
        """
        self.max_workers = max_workers or mp.cpu_count()
        self.use_processes = use_processes
        self.results = {}
        self.errors = {}
        
        logger.info(f"Initialized ParallelProcessor with {self.max_workers} workers")
        logger.info(f"Using {'ProcessPoolExecutor' if use_processes else 'ThreadPoolExecutor'}")
    
    def process_courses_parallel(
        self,
        courses: List[Dict],
        processing_function: Callable,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process multiple courses in parallel
        
        Args:
            courses: List of course dictionaries
            processing_function: Function to process each course
            **kwargs: Additional arguments to pass to processing function
            
        Returns:
            Dictionary with results for each course
        """
        start_time = time.time()
        
        # Choose executor based on task type
        ExecutorClass = ProcessPoolExecutor if self.use_processes else ThreadPoolExecutor
        
        with ExecutorClass(max_workers=self.max_workers) as executor:
            # Submit all courses for processing
            future_to_course = {
                executor.submit(processing_function, course, **kwargs): course
                for course in courses
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_course):
                course = future_to_course[future]
                course_code = course.get("course_code", "UNKNOWN")
                
                try:
                    result = future.result()
                    self.results[course_code] = result
                    logger.info(f"✓ Completed processing for course: {course_code}")
                except Exception as e:
                    self.errors[course_code] = str(e)
                    logger.error(f"✗ Error processing course {course_code}: {e}")
        
        elapsed_time = time.time() - start_time
        
        return {
            "results": self.results,
            "errors": self.errors,
            "total_courses": len(courses),
            "successful": len(self.results),
            "failed": len(self.errors),
            "elapsed_time": round(elapsed_time, 2),
            "avg_time_per_course": round(elapsed_time / len(courses), 2) if courses else 0
        }
    
    def process_students_parallel(
        self,
        students: List[Dict],
        processing_function: Callable,
        batch_size: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process multiple student answer sheets in parallel
        
        Args:
            students: List of student dictionaries
            processing_function: Function to process each student
            batch_size: Optional batch size for chunking
            **kwargs: Additional arguments
            
        Returns:
            Processing results
        """
        start_time = time.time()
        
        # If batch_size specified, process in chunks
        if batch_size:
            return self._process_in_batches(students, processing_function, batch_size, **kwargs)
        
        ExecutorClass = ProcessPoolExecutor if self.use_processes else ThreadPoolExecutor
        
        with ExecutorClass(max_workers=self.max_workers) as executor:
            future_to_student = {
                executor.submit(processing_function, student, **kwargs): student
                for student in students
            }
            
            for future in as_completed(future_to_student):
                student = future_to_student[future]
                student_id = student.get("roll_number", "UNKNOWN")
                
                try:
                    result = future.result()
                    self.results[student_id] = result
                    logger.info(f"✓ Processed student: {student_id}")
                except Exception as e:
                    self.errors[student_id] = str(e)
                    logger.error(f"✗ Error processing student {student_id}: {e}")
        
        elapsed_time = time.time() - start_time
        
        return {
            "results": self.results,
            "errors": self.errors,
            "total_students": len(students),
            "successful": len(self.results),
            "failed": len(self.errors),
            "elapsed_time": round(elapsed_time, 2),
            "avg_time_per_student": round(elapsed_time / len(students), 2) if students else 0
        }
    
    def _process_in_batches(
        self,
        items: List[Dict],
        processing_function: Callable,
        batch_size: int,
        **kwargs
    ) -> Dict[str, Any]:
        """Process items in batches"""
        
        batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
        logger.info(f"Processing {len(items)} items in {len(batches)} batches of {batch_size}")
        
        for batch_num, batch in enumerate(batches, 1):
            logger.info(f"Processing batch {batch_num}/{len(batches)}")
            
            ExecutorClass = ProcessPoolExecutor if self.use_processes else ThreadPoolExecutor
            
            with ExecutorClass(max_workers=self.max_workers) as executor:
                future_to_item = {
                    executor.submit(processing_function, item, **kwargs): item
                    for item in batch
                }
                
                for future in as_completed(future_to_item):
                    item = future_to_item[future]
                    item_id = item.get("id", "UNKNOWN")
                    
                    try:
                        result = future.result()
                        self.results[item_id] = result
                    except Exception as e:
                        self.errors[item_id] = str(e)
        
        return {
            "results": self.results,
            "errors": self.errors,
            "total_items": len(items),
            "successful": len(self.results),
            "failed": len(self.errors)
        }
    
    def get_progress(self) -> Dict:
        """Get current processing progress"""
        total_processed = len(self.results) + len(self.errors)
        
        return {
            "processed": total_processed,
            "successful": len(self.results),
            "failed": len(self.errors),
            "success_rate": round(len(self.results) / total_processed * 100, 1) if total_processed > 0 else 0
        }


class CourseEvaluationManager:
    """Manages parallel evaluation of multiple courses"""
    
    def __init__(self, max_workers: Optional[int] = None):
        """
        Initialize course evaluation manager
        
        Args:
            max_workers: Maximum parallel workers
        """
        self.processor = ParallelProcessor(max_workers=max_workers, use_processes=True)
    
    def evaluate_multiple_courses(
        self,
        courses_data: List[Dict],
        evaluation_pipeline: Callable
    ) -> Dict:
        """
        Evaluate multiple courses in parallel
        
        Args:
            courses_data: List of course data dictionaries
            evaluation_pipeline: Function that processes one course
            
        Returns:
            Evaluation results for all courses
        """
        logger.info(f"Starting parallel evaluation of {len(courses_data)} courses")
        
        results = self.processor.process_courses_parallel(
            courses=courses_data,
            processing_function=evaluation_pipeline
        )
        
        logger.info(f"Completed evaluation: {results['successful']}/{results['total_courses']} successful")
        logger.info(f"Total time: {results['elapsed_time']}s, Avg: {results['avg_time_per_course']}s per course")
        
        return results
    
    def evaluate_course_students_parallel(
        self,
        course_code: str,
        students_data: List[Dict],
        student_evaluation_function: Callable,
        batch_size: int = 10
    ) -> Dict:
        """
        Evaluate all students in a course in parallel
        
        Args:
            course_code: Course code
            students_data: List of student data
            student_evaluation_function: Function to evaluate one student
            batch_size: Batch size for processing
            
        Returns:
            Evaluation results
        """
        logger.info(f"Evaluating {len(students_data)} students for course {course_code}")
        
        results = self.processor.process_students_parallel(
            students=students_data,
            processing_function=student_evaluation_function,
            batch_size=batch_size,
            course_code=course_code
        )
        
        return results


class AsyncTaskQueue:
    """Manages asynchronous task queue for background processing"""
    
    def __init__(self):
        """Initialize task queue"""
        self.queue = mp.Queue()
        self.results_queue = mp.Queue()
        self.active_tasks = {}
    
    def add_task(self, task_id: str, task_function: Callable, *args, **kwargs):
        """Add task to queue"""
        task = {
            "id": task_id,
            "function": task_function,
            "args": args,
            "kwargs": kwargs,
            "submitted_at": datetime.now().isoformat()
        }
        self.queue.put(task)
        self.active_tasks[task_id] = "queued"
        logger.info(f"Task {task_id} added to queue")
    
    def process_queue(self, num_workers: int = 4):
        """Process tasks in queue with multiple workers"""
        
        def worker():
            while True:
                try:
                    task = self.queue.get(timeout=1)
                    if task is None:
                        break
                    
                    task_id = task["id"]
                    self.active_tasks[task_id] = "processing"
                    
                    try:
                        result = task["function"](*task["args"], **task["kwargs"])
                        self.results_queue.put({
                            "id": task_id,
                            "status": "success",
                            "result": result
                        })
                        self.active_tasks[task_id] = "completed"
                    except Exception as e:
                        self.results_queue.put({
                            "id": task_id,
                            "status": "error",
                            "error": str(e)
                        })
                        self.active_tasks[task_id] = "failed"
                
                except:
                    continue
        
        # Start worker processes
        processes = []
        for _ in range(num_workers):
            p = mp.Process(target=worker)
            p.start()
            processes.append(p)
        
        # Wait for all processes to complete
        for p in processes:
            p.join()
    
    def get_task_status(self, task_id: str) -> str:
        """Get status of a task"""
        return self.active_tasks.get(task_id, "not_found")


# Convenience functions
def evaluate_courses_parallel(
    courses: List[Dict],
    evaluation_function: Callable,
    max_workers: Optional[int] = None
) -> Dict:
    """
    Quick parallel course evaluation
    
    Args:
        courses: List of courses to evaluate
        evaluation_function: Function to evaluate each course
        max_workers: Maximum parallel workers
        
    Returns:
        Evaluation results
    """
    manager = CourseEvaluationManager(max_workers)
    return manager.evaluate_multiple_courses(courses, evaluation_function)


def evaluate_students_parallel(
    students: List[Dict],
    evaluation_function: Callable,
    max_workers: Optional[int] = None,
    batch_size: int = 10
) -> Dict:
    """
    Quick parallel student evaluation
    
    Args:
        students: List of students to evaluate
        evaluation_function: Function to evaluate each student
        max_workers: Maximum parallel workers
        batch_size: Batch size
        
    Returns:
        Evaluation results
    """
    processor = ParallelProcessor(max_workers, use_processes=True)
    return processor.process_students_parallel(
        students, evaluation_function, batch_size
    )
