from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    documents = relationship("Document", back_populates="owner")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    status = Column(String, nullable=False, default="uploaded")
    upload_time = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    owner = relationship("User", back_populates="documents")
    precedents = relationship("Precedent", back_populates="source_document")

class Precedent(Base):
    __tablename__ = "precedents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    court = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    summary = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Text)  # Store as JSON string for now
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    source_document = relationship("Document", back_populates="precedents")