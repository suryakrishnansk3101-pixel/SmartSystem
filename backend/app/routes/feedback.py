from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models import Feedback, Ticket, User
from app.schemas import FeedbackCreate

router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_feedback_schema():
    inspector = inspect(engine)

    if not inspector.has_table("feedback"):
        return

    columns = {
        column["name"]
        for column in inspector.get_columns("feedback")
    }

    with engine.begin() as connection:

        if "feedback_id" in columns and "id" not in columns:
            connection.execute(
                text(
                    "ALTER TABLE feedback "
                    "RENAME COLUMN feedback_id TO id"
                )
            )
            columns.remove("feedback_id")
            columns.add("id")

        if "timestamp" in columns and "created_at" not in columns:
            connection.execute(
                text(
                    "ALTER TABLE feedback "
                    "RENAME COLUMN timestamp TO created_at"
                )
            )
            columns.remove("timestamp")
            columns.add("created_at")

        if "ticket_id" not in columns:
            connection.execute(
                text(
                    "ALTER TABLE feedback "
                    "ADD COLUMN ticket_id INTEGER"
                )
            )

        if "created_at" not in columns:
            connection.execute(
                text(
                    "ALTER TABLE feedback "
                    "ADD COLUMN created_at TIMESTAMP "
                    "DEFAULT CURRENT_TIMESTAMP"
                )
            )

        connection.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS "
                "uq_feedback_ticket_user "
                "ON feedback (ticket_id, user_id) "
                "WHERE ticket_id IS NOT NULL"
            )
        )


@router.post("/")
def create_feedback(
    feedback: FeedbackCreate,
    db: Session = Depends(get_db)
):
    content = feedback.content.strip()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Feedback comment is required"
        )

    ticket = db.query(Ticket).filter(
        Ticket.ticket_id == feedback.ticket_id
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    if ticket.user_id != feedback.user_id:
        raise HTTPException(
            status_code=403,
            detail="Feedback is not allowed for this ticket"
        )

    if ticket.status != "Closed":
        raise HTTPException(
            status_code=400,
            detail="Feedback can be submitted only for closed tickets"
        )

    existing_feedback = db.query(Feedback).filter(
        Feedback.ticket_id == feedback.ticket_id,
        Feedback.user_id == feedback.user_id
    ).first()

    if existing_feedback:
        raise HTTPException(
            status_code=409,
            detail="Feedback already submitted for this ticket"
        )

    new_feedback = Feedback(
        ticket_id=feedback.ticket_id,
        user_id=feedback.user_id,
        content=content,
        rating=feedback.rating
    )

    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)

    return {
        "message": "Feedback submitted successfully",
        "data": new_feedback
    }


@router.get("/")
def get_feedbacks(
    db: Session = Depends(get_db)
):
    feedbacks = (
        db.query(Feedback, User)
        .join(User, User.user_id == Feedback.user_id)
        .order_by(Feedback.created_at.desc())
        .all()
    )

    return [
        {
            "id": feedback.id,
            "ticket_id": feedback.ticket_id,
            "user_id": feedback.user_id,
            "user_name": user.name,
            "rating": feedback.rating,
            "content": feedback.content,
            "created_at": feedback.created_at
        }
        for feedback, user in feedbacks
    ]


@router.get("/ticket/{ticket_id}/user/{user_id}")
def get_ticket_feedback(
    ticket_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    feedback = db.query(Feedback).filter(
        Feedback.ticket_id == ticket_id,
        Feedback.user_id == user_id
    ).first()

    if not feedback:
        return {
            "submitted": False
        }

    return {
        "submitted": True,
        "feedback": feedback
    }
