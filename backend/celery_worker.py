"""
Celery Worker Configuration
Handles asynchronous background tasks with Celery + Redis
"""
from celery import Celery
from ..app.config import settings

# Initialize Celery app
celery_app = Celery(
    'exam_checker',
    broker=settings.redis_url,
    backend=settings.redis_url
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    worker_prefetch_multiplier=1,  # Process one task at a time
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks
)

# Import tasks
from .tasks import (
    process_question_paper_task,
    process_answer_key_task,
    process_student_batch_task,
    process_single_student_task,
    evaluate_course_parallel_task
)

__all__ = [
    'celery_app',
    'process_question_paper_task',
    'process_answer_key_task',
    'process_student_batch_task',
    'process_single_student_task',
    'evaluate_course_parallel_task'
]
