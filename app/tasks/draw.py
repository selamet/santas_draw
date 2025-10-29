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


@app.task(bind=True, name='get_user_info')
def get_user_info(self, user_email: str):
    """
    Fetches user information from database
    """
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            logger.warning(f"User not found: {user_email}")
            return {"status": "error", "message": "User not found"}
        
        user_data = {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }
        
        logger.info(f"User data fetched: {user_email}")
        return {"status": "success", "user": user_data}
    
    except Exception as e:
        logger.error(f"Error fetching user info: {str(e)}")
        return {"status": "error", "message": str(e)}
    
    finally:
        db.close()
