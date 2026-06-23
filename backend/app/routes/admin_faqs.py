from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import FAQ
from app.schemas import FAQCreate, FAQUpdate

router = APIRouter(
    prefix="/admin/faqs",
    tags=["Admin FAQ"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.get("/")
def get_all_faqs(
    db: Session = Depends(get_db)
):
    return db.query(FAQ).all()


@router.post("/")
def create_faq(
    faq: FAQCreate,
    db: Session = Depends(get_db)
):

    new_faq = FAQ(
        department=faq.department,
        question=faq.question,
        answer=faq.answer,
        category=faq.category
    )

    db.add(new_faq)
    db.commit()

    return {
        "message": "FAQ Added"
    }


@router.put("/{faq_id}")
def update_faq(
    faq_id: int,
    faq: FAQUpdate,
    db: Session = Depends(get_db)
):

    db_faq = db.query(FAQ).filter(
        FAQ.faq_id == faq_id
    ).first()

    if not db_faq:
        return {
            "message": "FAQ Not Found"
        }

    db_faq.department = faq.department
    db_faq.question = faq.question
    db_faq.answer = faq.answer
    db_faq.category = faq.category

    db.commit()

    return {
        "message": "FAQ Updated"
    }


@router.delete("/{faq_id}")
def delete_faq(
    faq_id: int,
    db: Session = Depends(get_db)
):

    faq = db.query(FAQ).filter(
        FAQ.faq_id == faq_id
    ).first()

    if not faq:
        return {
            "message": "FAQ Not Found"
        }

    db.delete(faq)
    db.commit()

    return {
        "message": "FAQ Deleted"
    }