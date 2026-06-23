from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import KnowledgeBase
from app.schemas import KnowledgeBaseCreate
import subprocess
import os

router = APIRouter(
    prefix="/knowledge-base",
    tags=["Knowledge Base"]
)

UPLOAD_FOLDER = "data/uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.post("/")
def create_document(
    document: KnowledgeBaseCreate,
    db: Session = Depends(get_db)
):

    new_document = KnowledgeBase(
        file_name=document.file_name,
        file_path=document.file_path
    )

    db.add(new_document)
    db.commit()

    return {
        "message": "Document Added Successfully"
    }


@router.get("/")
def get_documents(
    db: Session = Depends(get_db)
):

    return db.query(
        KnowledgeBase
    ).all()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    import os

    upload_folder = "data/uploads"

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    path = os.path.join(
        upload_folder,
        file.filename
    )

    with open(path, "wb") as buffer:
        buffer.write(
            await file.read()
        )

    document = KnowledgeBase(
        file_name=file.filename,
        file_path=path
    )

    db.add(document)
    db.commit()

    # Auto rebuild ChromaDB
    subprocess.run(
        ["python", "-m", "app.rag.ingest_documents"]
    )

    return {
        "message": "Document Uploaded Successfully",
        "file": file.filename
    }


@router.delete("/{file_name}")
def delete_document(
    file_name: str,
    db: Session = Depends(get_db)
):

    document = db.query(
        KnowledgeBase
    ).filter(
        KnowledgeBase.file_name ==
        file_name
    ).first()

    if document:

        db.delete(document)
        db.commit()

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file_name
    )

    if os.path.exists(file_path):

        os.remove(file_path)

    return {
        "message":
        "Document Deleted Successfully"
    }
