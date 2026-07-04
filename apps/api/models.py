from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class LearnerProfile(Base):
    __tablename__ = "learner_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    profile_data = Column(JSON) # e.g. goal, current_level, target_level
    updated_at = Column(DateTime, default=datetime.utcnow)

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    messages = Column(JSON) # List of message objects
    created_at = Column(DateTime, default=datetime.utcnow)

class Resource(Base):
    __tablename__ = "resources"
    id = Column(Integer, primary_key=True, index=True)
    resource_type = Column(String) # 'video', 'article'
    title = Column(String)
    url = Column(String)
    metadata_json = Column(JSON) # channel info, duration, upload date
    metrics_json = Column(JSON) # views, likes
    created_at = Column(DateTime, default=datetime.utcnow)

class Transcript(Base):
    __tablename__ = "transcripts"
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"))
    full_text = Column(String)
    language = Column(String)

class TranscriptChunk(Base):
    __tablename__ = "transcript_chunks"
    id = Column(Integer, primary_key=True, index=True)
    transcript_id = Column(Integer, ForeignKey("transcripts.id"))
    resource_id = Column(Integer, ForeignKey("resources.id"))
    start_timestamp = Column(Float)
    end_timestamp = Column(Float)
    content = Column(String)
    embedding = Column(Vector(1536)) # Assuming OpenAI embeddings (text-embedding-3-small)
