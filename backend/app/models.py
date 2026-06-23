from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Boolean,
    UniqueConstraint
)

from app.database import Base


# =========================
# USERS TABLE
# =========================

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    email = Column(
        String(255),
        unique=True,
        nullable=False
    )

    password = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(20),
        default="user"
    )

    is_active = Column(Boolean, default=True)

# =========================
# FAQ TABLE
# =========================

class FAQ(Base):
    __tablename__ = "faqs"

    faq_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    department = Column(String(100))

    question = Column(
        Text,
        nullable=False
    )

    answer = Column(
        Text,
        nullable=False
    )

    category = Column(
        String(100)
    )


# =========================
# FEEDBACK TABLE
# =========================

class Feedback(Base):
    __tablename__ = "feedback"
    __table_args__ = (
        UniqueConstraint(
            "ticket_id",
            "user_id",
            name="uq_feedback_ticket_user"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    ticket_id = Column(
        Integer,
        ForeignKey("tickets.ticket_id"),
        nullable=True
    )

    user_id = Column(
        Integer,
        nullable=False
    )

    content = Column(
        Text,
        nullable=False
    )

    rating = Column(
        Integer,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# =========================
# TICKET TABLE
# =========================

class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        nullable=False
    )

    subject = Column(
        String(255),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    request_type = Column(
        String(50)
    )

    priority = Column(
        String(50),
        default="Medium"
    )

    status = Column(
        String(50),
        default="Open"
    )

    agent_name = Column(
        String(100),
        default="Not Assigned"
    )

    # assigned_agent_id = Column(
    # Integer,
    # nullable=True
    # )

# =========================
# KNOWLEDGE BASE TABLE
# =========================

class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    document_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    file_name = Column(
        String(255),
        nullable=False
    )

    file_path = Column(
        String(500),
        nullable=False
    )

class TicketReply(Base):
    __tablename__ = "ticket_replies"

    reply_id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("tickets.ticket_id"))
    agent_name = Column(String(100))
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Admin(Base):
    __tablename__ = "admins"

    admin_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), default="admin")
    is_active = Column(Boolean, default=True)

class Agent(Base):

    __tablename__ = "agents"

    agent_id = Column(
        Integer,
        primary_key=True
    )

    name = Column(String)

    email = Column(String)

    department = Column(String)

    status = Column(
        String,
        default="Active"
    )

    assigned_agent_id = Column(
    Integer,
    ForeignKey("agents.agent_id"),
    nullable=True
    )

    assigned_agent_name = Column(
        String(100),
        default="Not Assigned"
    )
    
