from fastapi import APIRouter, Depends
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from difflib import SequenceMatcher
import re
from sqlalchemy.orm import Session
from app.schemas import TicketCreate, ChatRequest
from app.database import SessionLocal
from app.classifier import classify_ticket
from app.priority import predict_priority
from app.rag.query import search_knowledge_base
from app.models import Ticket, TicketReply, Agent, FAQ

router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def normalize_question(text):
    return re.sub(
        r"[^a-z0-9 ]",
        " ",
        (text or "").lower()
    ).strip()


def faq_match_score(user_question, faq_question):
    user_text = normalize_question(user_question)
    faq_text = normalize_question(faq_question)

    if not user_text or not faq_text:
        return 0

    if (
        user_text == faq_text
        or user_text in faq_text
        or faq_text in user_text
    ):
        return 1

    user_words = set(user_text.split())
    faq_words = set(faq_text.split())

    overlap = len(
        user_words.intersection(faq_words)
    ) / max(
        len(user_words.union(faq_words)),
        1
    )

    text_similarity = SequenceMatcher(
        None,
        user_text,
        faq_text
    ).ratio()

    return max(overlap, text_similarity)


def search_direct_faq(db, question):
    best_faq = None
    best_score = 0

    for faq in db.query(FAQ).all():
        score = faq_match_score(
            question,
            faq.question
        )

        if score > best_score:
            best_score = score
            best_faq = faq

    print("AI Retrieval Debug - Direct FAQ Score:", best_score)

    if best_faq and best_score >= 0.45:
        return best_faq

    return None


def timed_knowledge_search(question):
    def run_search():
        search_db = SessionLocal()

        try:
            return search_knowledge_base(
                question,
                search_db
            )
        finally:
            search_db.close()

    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(run_search)

    try:
        return future.result(timeout=8)
    finally:
        executor.shutdown(
            wait=False,
            cancel_futures=True
        )


@router.post("/")
def create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db)
):  
    request_type = classify_ticket(
    ticket.description
    )

    priority = predict_priority(
    ticket.description
    )

    new_ticket = Ticket(
        user_id=ticket.user_id,
        subject=ticket.subject,
        description=ticket.description,
        request_type=request_type,
        priority=priority
    )

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    return {
        "message": "Ticket Created Successfully",
        "data": new_ticket
    }


@router.get("/")
def get_tickets(
    db: Session = Depends(get_db)
):
    return db.query(Ticket).all()

# @router.post("/tickets")
# def create_ticket(ticket: TicketCreate):

#     return {
#         "message": "Ticket Created Successfully"
#     }

@router.post("/chat")
def chat(request: ChatRequest):

    db = SessionLocal()

    def create_ai_ticket():

        new_ticket = Ticket(
            user_id=1,
            subject=request.question,
            description=request.question,
            status="Open"
        )

        db.add(new_ticket)
        db.commit()
        db.refresh(new_ticket)

        return {
            "found": False,
            "answer": f"No answer found. Ticket #{new_ticket.ticket_id} created automatically.",
            "ticket_id": new_ticket.ticket_id
        }

    faq = search_direct_faq(
        db,
        request.question
    )

    if faq:
        return {
            "found": True,
            "answer": faq.answer,
            "source": "FAQ"
        }

    try:

        knowledge_result = timed_knowledge_search(
            request.question
        )

    except TimeoutError:

        print("AI Retrieval Debug - RAG TIMEOUT")

        return create_ai_ticket()

    except Exception as e:

        print("AI Retrieval Debug - RAG ERROR:", e)

        return create_ai_ticket()

    if knowledge_result.get("found"):

        return {
            "found": True,
            "answer": knowledge_result.get("answer")
        }

    return create_ai_ticket()

@router.get("/escalated")
def get_escalated_tickets(
    db: Session = Depends(get_db)
):

    return db.query(Ticket).filter(
        Ticket.status == "Escalated"
    ).all()

@router.get("/agent-stats")
def agent_stats(db: Session = Depends(get_db)):

    agents = db.query(Agent).all()

    result = []

    for agent in agents:

        assigned = db.query(Ticket).filter(
            Ticket.agent_name == agent.name
        ).count()

        closed = db.query(Ticket).filter(
            Ticket.agent_name == agent.name,
            Ticket.status == "Closed"
        ).count()

        result.append({
            "agent": agent.name,
            "assigned": assigned,
            "closed": closed
        })

    return result

@router.get("/agent/{agent_name}")
def get_agent_tickets(
    agent_name: str,
    db: Session = Depends(get_db)
):
    return db.query(Ticket).filter(
        Ticket.agent_name == agent_name
    ).all()

@router.get("/user/{user_id}")
def get_user_tickets(
    user_id: int,
    db: Session = Depends(get_db)
):

    tickets = db.query(Ticket).filter(
        Ticket.user_id == user_id
    ).all()

    return tickets

@router.get("/{ticket_id}")
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db)
):

    ticket = db.query(Ticket).filter(
        Ticket.ticket_id == ticket_id
    ).first()

    if not ticket:
        return {
            "message": "Ticket not found"
        }

    return ticket

@router.post("/{ticket_id}/reply")
def add_reply(
    ticket_id: int,
    agent_name: str,
    message: str,
    db: Session = Depends(get_db)
):

    reply = TicketReply(
        ticket_id=ticket_id,
        agent_name=agent_name,
        message=message
    )

    db.add(reply)
    db.commit()

    return {"message": "Reply Added"}

@router.get("/{ticket_id}/replies")
def get_replies(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    return db.query(TicketReply).filter(
        TicketReply.ticket_id == ticket_id
    ).all()

@router.put("/{ticket_id}/assign/{agent_id}")
def assign_agent(
    ticket_id: int,
    agent_id: int,
    db: Session = Depends(get_db)
):

    ticket = db.query(Ticket).filter(
        Ticket.ticket_id == ticket_id
    ).first()

    if not ticket:
        return {"message": "Ticket Not Found"}

    agent = db.query(Agent).filter(
        Agent.agent_id == agent_id
    ).first()

    if not agent:
        return {"message": "Agent Not Found"}

    ticket.agent_name = agent.name
    ticket.status = "Assigned"

    db.commit()
    db.refresh(ticket)
    return {
        "message": "Agent Assigned Successfully"
    }


@router.put("/{ticket_id}/close")
def close_ticket(
    ticket_id: int,
    db: Session = Depends(get_db)
):

    ticket = db.query(Ticket).filter(
        Ticket.ticket_id == ticket_id
    ).first()

    if not ticket:
        return {
            "message": "Ticket Not Found"
        }

    ticket.status = "Closed"

    db.commit()

    return {
        "message": "Ticket Closed"
    }

@router.put("/{ticket_id}/escalate")
def escalate_ticket(
    ticket_id: int,
    db: Session = Depends(get_db)
):

    ticket = db.query(Ticket).filter(
        Ticket.ticket_id == ticket_id
    ).first()

    if not ticket:
        return {
            "message": "Ticket Not Found"
        }

    ticket.status = "Escalated"

    db.commit()

    return {
        "message": "Ticket Escalated To Admin"
    }

@router.post("/{ticket_id}/admin-reply")
def admin_reply(
    ticket_id: int,
    message: str,
    db: Session = Depends(get_db)
):

    reply = TicketReply(
        ticket_id=ticket_id,
        agent_name="Admin",
        message=message
    )

    db.add(reply)
    db.commit()

    return {
        "message": "Admin Reply Added"
    }

@router.get("/agent-stats")
def agent_stats(
    db: Session = Depends(get_db)
):

    agents = db.query(Agent).all()

    result = []

    for agent in agents:

        assigned = db.query(Ticket).filter(
            Ticket.agent_name == agent.name
        ).count()

        closed = db.query(Ticket).filter(
            Ticket.agent_name == agent.name,
            Ticket.status == "Closed"
        ).count()

        result.append({
            "agent": agent.name,
            "assigned": assigned,
            "closed": closed
        })

    return result

