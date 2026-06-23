from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.get("/users")
def get_users(
    db: Session = Depends(get_db)
):

    return db.query(User).all()


@router.put("/users/{user_id}/role")
def change_role(
    user_id: int,
    role: str,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.user_id == user_id
    ).first()

    if not user:

        return {
            "message": "User Not Found"
        }

    user.role = role

    db.commit()

    return {
        "message": "Role Updated"
    }


@router.put("/users/{user_id}/status")
def toggle_status(
    user_id: int,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.user_id == user_id
    ).first()

    if not user:

        return {
            "message": "User Not Found"
        }

    user.is_active = not user.is_active

    db.commit()

    return {
        "message": "Status Updated"
    }


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.user_id == user_id
    ).first()

    if not user:

        return {
            "message": "User Not Found"
        }

    db.delete(user)

    db.commit()

    return {
        "message": "User Deleted"
    }