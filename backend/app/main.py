from fastapi import FastAPI
from app.routes import admin_faqs, user, faq, feedback, ticket, knowledge_base
from app.routes import agent, admin, ticket
from app.database import engine
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import FAQ, Base
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
Base.metadata.create_all(bind=engine)
feedback.ensure_feedback_schema()

app = FastAPI(
    title="Smart AI Service Desk"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(faq.router)
app.include_router(feedback.router)
app.include_router(ticket.router)
app.include_router(knowledge_base.router)
app.include_router(
    admin_faqs.router
)
app.include_router(
    admin.router
)
app.include_router(
    agent.router
)

@app.get("/")
def root():
    return {"message": "Smart AI Service Desk API Running"}

@app.get("/health")
def health():
    print("HEALTH CALLED")
    return {"status": "ok"}
