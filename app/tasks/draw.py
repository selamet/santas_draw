"""
Celery Tasks for Draw Operations

Handles asynchronous draw processing.
"""

from celery import Task
from app.celery_app import app
from app.models import User
from sqlalchemy.orm import Session
from app.models.database import SessionLocal
from app.services.draw_service import DrawService
from app.core.exceptions import (
    DrawServiceException,
    InsufficientParticipantsError,
    DrawAlreadyCompletedError,
    DrawNotFoundError
)
import logging

logger = logging.getLogger(__name__)


@app.task(bind=True, name='execute_scheduled_draw_task')
def execute_scheduled_draw_task(self):
    """
    Execute scheduled draws (runs periodically via Celery Beat)
    
    TODO: Implement automatic execution of draws when their scheduled time arrives
    """
    logger.info('execute_scheduled_draw_task')
    return {"status": "success", "message": "Test task completed"}


@app.task(bind=True, name='process_manual_draw_task')
def process_manual_draw_task(self, draw_id: int):
    """
    Process manual draw execution
    
    Steps:
    1. Fetch draw and participants from database
    2. Apply Secret Santa algorithm
    3. Create DrawResult records
    4. Send emails to participants (TODO)
    5. Update draw status to COMPLETED
    
    Args:
        draw_id: ID of the draw to process
        
    Returns:
        Dict with status and message
    """
    logger.info(f'process_manual_draw_task started for draw_id={draw_id}')
    
    db = SessionLocal()
    
    try:
        service = DrawService(db)
        results = service.execute_draw(draw_id)
        db.commit()
        
        logger.info(f'Draw processed successfully: draw_id={draw_id}, matches_created={len(results)}')
        
        return {
            "status": "success",
            "message": f"Draw {draw_id} processed successfully",
            "matches_created": len(results)
        }
        
    except DrawNotFoundError as e:
        logger.error(f'Draw not found: draw_id={draw_id}, error={str(e)}')
        db.rollback()
        return {"status": "error", "error_type": "not_found", "message": str(e)}
        
    except InsufficientParticipantsError as e:
        logger.error(f'Insufficient participants: draw_id={draw_id}, error={str(e)}')
        db.rollback()
        return {"status": "error", "error_type": "insufficient_participants", "message": str(e)}
        
    except DrawAlreadyCompletedError as e:
        logger.warning(f'Draw already completed: draw_id={draw_id}, error={str(e)}')
        db.rollback()
        return {"status": "error", "error_type": "already_completed", "message": str(e)}
        
    except DrawServiceException as e:
        logger.error(f'Draw service error: draw_id={draw_id}, error={str(e)}')
        db.rollback()
        return {"status": "error", "error_type": "service_error", "message": str(e)}
        
    except Exception as e:
        logger.error(f'Unexpected error in draw task: draw_id={draw_id}, error={str(e)}', exc_info=True)
        db.rollback()
        return {"status": "error", "error_type": "unexpected", "message": f"Unexpected error: {str(e)}"}
        
    finally:
        db.close()
