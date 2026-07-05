import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)

from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    username = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    email = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = Column(
        String,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # Relationship to uploaded files
    uploaded_files = relationship(
        "UploadedFile",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(username='{self.username}')>"


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    user_id = Column(
        String,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    original_name = Column(
        String,
        nullable=False
    )

    stored_name = Column(
        String,
        nullable=False,
        unique=True
    )

    sha256 = Column(
        String,
        nullable=False,
        index=True
    )

    file_type = Column(
        String,
        nullable=False
    )
    file_size = Column(
        Integer,
        nullable=False
    )

    uploaded_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    indexed = Column(
        Boolean,
        default=False
    )

    chunk_count = Column(
        Integer,
        default=0
    )

    # Relationship back to user
    user = relationship(
        "User",
        back_populates="uploaded_files"
    )

    def __repr__(self):
        return (
            f"<UploadedFile("
            f"original_name='{self.original_name}', "
            f"user_id='{self.user_id}')>"
        )