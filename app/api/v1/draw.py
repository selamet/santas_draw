import logging
from typing import Optional
from app.models import get_db, User
from sqlalchemy.orm import Session
from app.api.deps import get_current_user_optional
from app.schemas.draw import ManualDrawCreate, ManualDrawResponse
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.draw import Draw, DrawStatus, DrawType, Participant

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/draws/manual", response_model=ManualDrawResponse, status_code=status.HTTP_201_CREATED)
async def create_manual_draw(
        draw_data: ManualDrawCreate,
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Create a manual draw with specified participants.
    This endpoint allows the creation of a manual draw by providing participant details.
    The draw will be processed asynchronously.
    Parameters:
    - draw_data: ManualDrawCreate - The data required to create the manual draw, including
        participant details and requirements for address and phone number.
    - db: Session - The database session dependency.
    - current_user: Optional[User] - The currently authenticated user, if any.
    Returns:
    - ManualDrawResponse: The response containing the draw ID and success message.
    Raises:
    - HTTPException: If there is an error during draw creation or processing.
    """
    try:
        new_draw = Draw(
            creator_id=current_user.id if current_user else None,
            draw_type=DrawType.MANUAL.value,
            status=DrawStatus.IN_PROGRESS.value,
            require_address=draw_data.address_required,
            require_phone=draw_data.phone_number_required,
            draw_date=None
        )
        db.add(new_draw)
        db.flush()

        participants_data = [
            Participant(
                draw_id=new_draw.id,
                first_name=p.first_name,
                last_name=p.last_name,
                email=p.email,
                address=p.address,
                phone=p.phone
            )
            for p in draw_data.participants
        ]
        db.bulk_save_objects(participants_data)
        db.commit()

        # from app.tasks.draw import process_manual_draw_task
        # process_manual_draw_task.delay(new_draw.id)

        logger.info(f"Manual draw created: draw_id={new_draw.id}, creator_id={new_draw.creator_id}")

        return ManualDrawResponse(
            success=True,
            message="Draw created successfully and is being processed.",
            draw_id=new_draw.id
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Error while creating draw {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error while creating draw: {str(e)}"
        )
