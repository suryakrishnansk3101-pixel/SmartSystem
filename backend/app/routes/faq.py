from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
# from app.faq_search import search_faq
from app.database import SessionLocal
from app.models import FAQ
from app.schemas import FAQCreate

router = APIRouter(
    prefix="/faq",
    tags=["FAQ"]
)


# Database Connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Get All FAQs
@router.get("/")
def get_faqs(db: Session = Depends(get_db)):
    faqs = db.query(FAQ).all()
    return faqs


# Add New FAQ
@router.post("/")
def create_faq(
    faq: FAQCreate,
    db: Session = Depends(get_db)
):
    new_faq = FAQ(
        question=faq.question,
        answer=faq.answer,
        category=faq.category
    )

    db.add(new_faq)
    db.commit()
    db.refresh(new_faq)

    return {
        "message": "FAQ Added Successfully",
        "data": new_faq
    }

@router.get("/search")
def search_faq(question: str, db: Session = Depends(get_db)):
    faq = db.query(FAQ).filter(
        FAQ.question.ilike(f"%{question}%")
    ).first()

    if faq:
        return {
            "question": faq.question,
            "answer": faq.answer
        }

    return {
        "message": "No FAQ found"
    }
