from celery import Task
from app.celery_app import app
from app.models import User
from sqlalchemy.orm import Session
from app.models.database import SessionLocal
import logging

logger = logging.getLogger(__name__)


@app.task(bind=True, name='execute_scheduled_draw_task')
def execute_scheduled_draw_task(self):
    """
    """
    logger.info('execute_scheduled_draw_task')
    return {"status": "success", "message": "Test task completed"}


@app.task(bind=True, name='process_manual_draw_task')
def process_manual_draw_task(self, draw_id: int):
    """
    Processes manual draw operation.
    
    Args:
        draw_id: The draw ID
        
    Returns:
        Dict with status and message
        
    TODO: Draw algorithm will be implemented here
    - Fetch draw and participants from database
    - Apply Secret Santa draw algorithm
    - Create DrawResult records
    - Send emails
    - Update status (IN_PROGRESS → COMPLETED)
    """
    logger.info(f'process_manual_draw_task started for draw_id={draw_id}')

    # For now, just a log message
    # In the future, draw algorithm and email sending will be here

    return {"status": "success", "message": f"Task executed for draw_id={draw_id}"}
