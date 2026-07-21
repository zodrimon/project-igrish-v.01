from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.core.db import Base

class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    status = Column(String, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    status = Column(String, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Preference(Base):
    __tablename__ = "preferences"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Habit(Base):
    __tablename__ = "habits"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    frequency = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class NudgeLog(Base):
    __tablename__ = "nudge_log"
    id = Column(Integer, primary_key=True, index=True)
    nudge_type = Column(String)
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    cooldown_until = Column(DateTime(timezone=True))

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)

class Turn(Base):
    __tablename__ = "turns"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String)
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
