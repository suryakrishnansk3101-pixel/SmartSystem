from pydantic import BaseModel, Field
from datetime import datetime

class UserRegister(BaseModel):
    name: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class FAQCreate(BaseModel):
    department: str
    question: str
    answer: str
    category: str


class FAQUpdate(BaseModel):
    department: str
    question: str
    answer: str
    category: str

class FeedbackCreate(BaseModel):
    ticket_id: int
    user_id: int
    content: str = Field(..., min_length=1)
    rating: int = Field(..., ge=1, le=5)


class FeedbackResponse(BaseModel):
    id: int
    ticket_id: int
    user_id: int
    content: str
    rating: int
    created_at: datetime

    class Config:
        from_attributes = True


class TicketCreate(BaseModel):
    user_id: int
    subject: str
    description: str

class TicketResponse(BaseModel):
    ticket_id: int
    user_id: int
    subject: str
    description: str
    priority: str
    status: str

    class Config:
        from_attributes = True


class KnowledgeBaseCreate(BaseModel):
    file_name: str
    file_path: str

class ChatRequest(BaseModel):
    question: str

class AgentCreate(BaseModel):
    name: str
    email: str
    department: str


class AgentUpdate(BaseModel):
    name: str
    email: str
    department: str
    status: str

class AssignTicket(BaseModel):

    agent_id: int
