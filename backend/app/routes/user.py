from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi import Header
from app.auth import verify_token
from app.database import SessionLocal
from app.models import User
from app.schemas import UserLogin, UserRegister
from app.auth import hash_password
from app.auth import verify_password
from app.auth import create_access_token

router = APIRouter()


# Database Connection Dependency
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):

    # Check if email already exists
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        return {
            "message": "Email already registered"
        }

    hashed = hash_password(user.password)

    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed,
        role="user"
    )

    db.add(new_user)
    db.commit()

    return {
        "message": "User Registered"
    }

@router.post("/login")
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):

    db_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    
    valid = verify_password(
        user.password,
        db_user.password
    )

    if not valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token(
        {"sub": db_user.email}
    )

    return {
    "access_token": token,
    "token_type": "bearer",
    "user_id": db_user.user_id,
    "name": db_user.name,
    "role": db_user.role
}

@router.get("/profile")
def profile(
    authorization: str = Header(...)
):

    token = authorization.replace(
        "Bearer ",
        ""
    )

    data = verify_token(token)

    return {
        "user": data
    }

@router.get("/test-token")
def test_token(token: str):
    data = verify_token(token)
    return data
