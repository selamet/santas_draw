import secrets
import logging
from typing import Optional
from app.models import get_db, User
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from app.api.deps import get_current_user_optional
from app.schemas.draw import DrawCreate, DrawResponse
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.draw import Draw, DrawStatus, DrawType, Participant

logger = logging.getLogger(__name__)

router = APIRouter()


def generate_share_link() -> str:
    """Generate a unique share link for the draw"""
    return secrets.token_urlsafe(16)


@router.post("/draw/create", response_model=DrawResponse, status_code=status.HTTP_201_CREATED)
async def create_draw(
        draw_request: DrawCreate,
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Create a new draw with participants.

    Args:
        draw_request: Request containing draw details and participants
        db: Database session

    Returns:
        Created draw with participants
    """
    try:
        if len(draw_request.participants) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least 2 participants are required"
            )

        emails = [p.email.lower() for p in draw_request.participants]

        if len(emails) != len(set(emails)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate email addresses are not allowed"
            )

        if draw_request.require_address:
            missing_address = [p.email for p in draw_request.participants if not p.address]

            if missing_address:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Address is required for all participants. Missing for: {', '.join(missing_address)}"
                )

        if draw_request.require_phone:
            missing_phone = [p.email for p in draw_request.participants if not p.phone]

            if missing_phone:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Phone is required for all participants. Missing for: {', '.join(missing_phone)}"
                )

        if draw_request.draw_date:
            if not draw_request.draw_date.tzinfo:
                draw_date = draw_request.draw_date.replace(tzinfo=timezone.utc)
            else:
                draw_date = draw_request.draw_date

            now = datetime.now(timezone.utc)

            if draw_date <= now:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="draw_date must be in the future."
                )
        else:
            draw_date = None

        draw_type = DrawType.USER_CREATED.value if current_user else DrawType.ANONYMOUS.value

        draw = Draw(
            creator_id=current_user.id if current_user else None,
            status=DrawStatus.ACTIVE.value,
            draw_type=draw_type,
            draw_date=draw_date,
            require_address=draw_request.require_address,
            require_phone=draw_request.require_phone,
            share_link=generate_share_link()
        )

        db.add(draw)
        db.flush()  # Get draw.id without committing

        for participant_data in draw_request.participants:
            participant = Participant(
                draw_id=draw.id,
                first_name=participant_data.first_name,
                last_name=participant_data.last_name,
                email=participant_data.email,
                address=participant_data.address,
                phone=participant_data.phone
            )
            db.add(participant)

        db.commit()
        db.refresh(draw)

        draw = db.query(Draw).options(joinedload(Draw.participants)).filter(Draw.id == draw.id).first()

        logger.info(f"Draw created successfully. Draw ID: {draw.id}, Participants: {len(draw_request.participants)}")

        return draw

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating draw: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the draw: {str(e)}"
        )


@router.get("/draw/{draw_id}", response_model=DrawResponse)
async def get_draw(draw_id: int, db: Session = Depends(get_db)):
    """
    Get a draw by ID with all participants.

    Args:
        draw_id: Draw ID
        db: Database session

    Returns:
        Draw with participants
    """
    draw = db.query(Draw).options(joinedload(Draw.participants)).filter(Draw.id == draw_id).first()

    if not draw:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Draw with ID {draw_id} not found"
        )

    return draw
