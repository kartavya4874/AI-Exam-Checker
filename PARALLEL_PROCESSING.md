# Parallel Processing System - Quick Reference

## Overview

The system now supports **parallel processing** for evaluating multiple courses simultaneously, significantly improving performance.

## Key Features

### 1. **Multiprocessing Support**
- Uses Python's `multiprocessing` for CPU-intensive tasks (OCR, evaluation)
- Automatically uses all available CPU cores
- Configurable worker count

### 2. **Dual Execution Modes**

**ProcessPoolExecutor** (Default - for CPU-bound tasks):
- OCR processing
- AI evaluation
- Image processing

**ThreadPoolExecutor** (for I/O-bound tasks):
- API calls
- Database operations
- File I/O

### 3. **Celery Integration**
- Distributed task processing
- Redis-backed task queue
- Progress tracking
- Task monitoring with Flower

## Usage Examples

### Evaluate Multiple Courses in Parallel

```python
from app.services.batch.parallel_processor import evaluate_courses_parallel

courses = [
    {"course_code": "CS101"},
    {"course_code": "CS102"},
    {"course_code": "MATH201"},
]

def process_course(course):
    # Your course processing logic
    return {"status": "completed"}

results = evaluate_courses_parallel(
    courses=courses,
    evaluation_function=process_course,
    max_workers=4  # 4 parallel workers
)

# Output:
# {
#   "total_courses": 3,
#   "successful": 3,
#   "failed": 0,
#   "elapsed_time": 45.2,
#   "avg_time_per_course": 15.1
# }
```

### Evaluate Students in Parallel

```python
from app.services.batch.parallel_processor import evaluate_students_parallel

students = [...]  # List of student data

results = evaluate_students_parallel(
    students=students,
    evaluation_function=evaluate_student,
    max_workers=8,
    batch_size=10
)
```

### Using Celery for Background Processing

```python
from app.services.batch.tasks import evaluate_course_parallel_task

# Submit task to Celery
task = evaluate_course_parallel_task.delay([1, 2, 3, 4, 5])

# Get task ID
task_id = task.id

# Check progress
from app.services.batch.tasks import get_task_progress
progress = get_task_progress(task_id)
```

## Performance Benefits

**Example Scenario:**
- 5 courses
- 50 students per course
- 10 questions per student

**Sequential Processing:**
- Time: ~250 minutes (5 courses × 50 students × 1 min/student)

**Parallel Processing (4 cores):**
- Time: ~65 minutes (4x speedup)

**Parallel Processing (8 cores):**
- Time: ~35 minutes (7x speedup)

## Configuration

### Environment Variables

```env
# Celery/Redis
REDIS_URL=redis://localhost:6379/0

# Parallel Processing
MAX_WORKERS=8  # Number of parallel workers
BATCH_SIZE=10  # Students per batch
```

### Starting Celery Worker

```bash
# Start Celery worker
celery -A celery_worker.celery_app worker --loglevel=info --concurrency=4

# Start Flower monitoring (optional)
celery -A celery_worker.celery_app flower
# Access at http://localhost:5555
```

## Architecture

```
Multiple Courses (Parallel)
├── Course 1 (Worker 1)
│   ├── Student 1 (Parallel)
│   ├── Student 2 (Parallel)
│   └── Student N (Parallel)
├── Course 2 (Worker 2)
│   └── Students (Parallel)
├── Course 3 (Worker 3)
│   └── Students (Parallel)
└── Course 4 (Worker 4)
    └── Students (Parallel)
```

## Files Created

1. `parallel_processor.py` - Core parallel processing engine
2. `tasks.py` - Celery task definitions
3. `celery_worker.py` - Celery configuration
4. `examples.py` - Usage examples

## Next Steps

- Faculty review interface
- Real-time progress tracking UI
- Deployment configuration
