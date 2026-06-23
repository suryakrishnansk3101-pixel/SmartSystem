from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Agent
from app.schemas import AgentCreate, AgentUpdate

router = APIRouter(
    prefix="/agents",
    tags=["Agents"]
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.get("/")
def get_agents(
    db: Session = Depends(get_db)
):

    return db.query(Agent).all()


@router.post("/")
def create_agent(
    agent: AgentCreate,
    db: Session = Depends(get_db)
):

    new_agent = Agent(
        name=agent.name,
        email=agent.email,
        department=agent.department,
        status="Active"
    )

    db.add(new_agent)
    db.commit()

    return {
        "message": "Agent Added"
    }


@router.put("/{agent_id}")
def update_agent(
    agent_id: int,
    agent: AgentUpdate,
    db: Session = Depends(get_db)
):

    db_agent = db.query(Agent).filter(
        Agent.agent_id == agent_id
    ).first()

    if not db_agent:

        return {
            "message": "Agent Not Found"
        }

    db_agent.name = agent.name
    db_agent.email = agent.email
    db_agent.department = agent.department
    db_agent.status = agent.status

    db.commit()

    return {
        "message": "Agent Updated"
    }


@router.delete("/{agent_id}")
def delete_agent(
    agent_id: int,
    db: Session = Depends(get_db)
):

    agent = db.query(Agent).filter(
        Agent.agent_id == agent_id
    ).first()

    if not agent:

        return {
            "message": "Agent Not Found"
        }

    db.delete(agent)

    db.commit()

    return {
        "message": "Agent Deleted"
    }