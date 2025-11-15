from celery import Task
from app.celery_app import app
from app.models import User, Draw, Participant, DrawResult, DrawStatus
from sqlalchemy.orm import Session
from app.models.database import SessionLocal
import random
import logging

from typing import List, Tuple
from datetime import datetime, timezone

from app.utils.email import send_draw_result_email

logger = logging.getLogger(__name__)


def perform_secret_santa_draw(participants: List[Participant]) -> List[Tuple[Participant, Participant]]:
    """
    Perform Secret Santa draw algorithm.
    Each participant gives a gift to another participant (not themselves).
    
    Args:
        participants: List of participants in the draw
        
    Returns:
        List of tuples (giver, receiver) representing the draw results
        
    Raises:
        ValueError: If less than 2 participants
    """
    if len(participants) < 2:
        raise ValueError("At least 2 participants required for draw")
    
    if len(participants) == 2:
        return [(participants[0], participants[1]), (participants[1], participants[0])]

    participant_ids = [p.id for p in participants]
    shuffled_ids = participant_ids.copy()
    
    max_attempts = 100
    attempt = 0

    while attempt < max_attempts:
        random.shuffle(shuffled_ids)
        if all(giver_id != receiver_id for giver_id, receiver_id in zip(participant_ids, shuffled_ids)):
            break
        attempt += 1
    
    if attempt >= max_attempts:
        # Fallback: use circular assignment with offset of 1
        logger.warning("Random shuffle failed after max attempts, using circular assignment")
        shuffled_ids = participant_ids[1:] + [participant_ids[0]]
    
    participant_map = {p.id: p for p in participants}
    
    results = []

    for giver_id, receiver_id in zip(participant_ids, shuffled_ids):
        results.append((participant_map[giver_id], participant_map[receiver_id]))
    
    return results


@app.task(bind=True, name='execute_scheduled_draw_task')
def execute_scheduled_draw_task(self):
    """
    Execute scheduled draws that are due.
    This task runs every hour and checks for draws with draw_date matching current hour.
    
    Returns:
        Dict with status and message
    """
    logger.info('execute_scheduled_draw_task started')
    
    db: Session = SessionLocal()
    try:
        now = datetime.now(timezone.utc)

        draws_to_execute = db.query(Draw).filter(
            Draw.status == DrawStatus.ACTIVE.value,
            Draw.draw_date.isnot(None),
            Draw.draw_date <= now
        ).all()
        
        if not draws_to_execute:
            logger.info('No scheduled draws to execute')
            return {"status": "success", "message": "No scheduled draws found"}
        
        executed_count = 0

        for draw in draws_to_execute:
            try:
                result = _process_draw(db, draw.id)

                if result["success"]:
                    executed_count += 1
                    logger.info(f'Scheduled draw executed: draw_id={draw.id}')
            except Exception as e:
                logger.error(f'Error executing scheduled draw {draw.id}: {e}')
                continue
        
        return {
            "status": "success",
            "message": f"Executed {executed_count} scheduled draw(s)"
        }
        
    except Exception as e:
        logger.error(f'Error in execute_scheduled_draw_task: {e}')
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


def _process_draw(db: Session, draw_id: int) -> dict:
    """
    Internal function to process a draw.
    Fetches participants, performs draw, creates results, sends emails, and updates status.
    
    Args:
        db: Database session
        draw_id: The draw ID
        
    Returns:
        Dict with status and success message
    """
    draw = db.query(Draw).filter(Draw.id == draw_id).first()

    if not draw:
        raise ValueError(f"Draw not found: draw_id={draw_id}")
    
    if draw.status == DrawStatus.COMPLETED.value:
        logger.warning(f"Draw {draw_id} is already completed")
        return {"status": "success", "message": "Draw already completed"}
    
    participants = db.query(Participant).filter(
        Participant.draw_id == draw_id
    ).all()
    
    if len(participants) < 2:
        raise ValueError(f"Not enough participants for draw {draw_id}: {len(participants)}")
    
    logger.info(f'Performing draw for draw_id={draw_id} with {len(participants)} participants')
    draw_results = perform_secret_santa_draw(participants)
    
    draw_result_objects = []

    for giver, receiver in draw_results:
        draw_result = DrawResult(
            draw_id=draw_id,
            giver_participant_id=giver.id,
            receiver_participant_id=receiver.id
        )
        draw_result_objects.append(draw_result)
    
    db.bulk_save_objects(draw_result_objects)
    db.flush()
    

    email_success_count = 0
    email_fail_count = 0
    
    for giver, receiver in draw_results:
        giver_name = f"{giver.first_name} {giver.last_name}"
        receiver_name = f"{receiver.first_name} {receiver.last_name}"
        
        success = send_draw_result_email(
            participant_name=giver_name,
            participant_email=giver.email,
            receiver_name=receiver_name,
            receiver_address=receiver.address if draw.require_address else None,
            receiver_phone=receiver.phone if draw.require_phone else None
        )
        
        if success:
            email_success_count += 1
        else:
            email_fail_count += 1
            logger.warning(f"Failed to send email to {giver.email} for draw {draw_id}")
    
    # Update draw status to COMPLETED
    draw.status = DrawStatus.COMPLETED.value
    db.commit()
    
    logger.info(
        f'Draw {draw_id} completed: '
        f'{len(draw_results)} results created, '
        f'{email_success_count} emails sent, '
        f'{email_fail_count} emails failed'
    )
    
    return {
        "status": "success",
        "message": f"Draw completed: {email_success_count} emails sent, {email_fail_count} failed"
    }


@app.task(bind=True, name='process_manual_draw_task')
def process_manual_draw_task(self, draw_id: int):
    """
    Processes manual draw operation.
    
    Args:
        draw_id: The draw ID
        
    Returns:
        Dict with status and message
    """
    logger.info(f'process_manual_draw_task started for draw_id={draw_id}')

    db: Session = SessionLocal()
    try:
        result = _process_draw(db, draw_id)
        return result
    except Exception as e:
        logger.error(f'Error in process_manual_draw_task for draw_id={draw_id}: {e}')
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
