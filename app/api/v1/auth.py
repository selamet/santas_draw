"""
Authentication endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models import get_db, User
from app.schemas import UserCreate, UserLogin, TokenResponse, TokenData, TaskResponse
from app.core.security import create_access_token
from app.tasks.draw import get_user_info
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user and return access token with user data
    
    Args:
        user_data: User creation data
        db: Database session
        
    Returns:
        Access token and user data
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = User.hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(data={"sub": new_user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user
    }


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login user and return access token with user data
    
    Args:
        user_data: User login credentials
        db: Database session
        
    Returns:
        Access token and user data
    """

    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user or not user.verify_password(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/get-user-async", response_model=TaskResponse)
async def get_user_async(user: User = Depends(get_current_user)):
    """
    Trigger a Celery task to fetch user information from database
    
    Args:
        user: Current authenticated user
        
    Returns:
        Celery task ID and status
    """
    # Trigger Celery task
    celery_task = get_user_info.delay(user.email)
    
    return {
        "task_id": celery_task.id,
        "status": "pending",
        "message": f"Task triggered to fetch user info for {user.email}"
    }
