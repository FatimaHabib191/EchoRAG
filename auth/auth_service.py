from pathlib import Path

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from config import STORAGE_DIR

from .models import User


pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

class AuthService:

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(
        plain_password: str,
        hashed_password: str
    ) -> bool:
        return pwd_context.verify(
            plain_password,
            hashed_password
        )

    @staticmethod
    def create_user(
        db: Session,
        username: str,
        email: str,
        password: str
    ):

        existing = db.query(User).filter(
            (User.username == username) |
            (User.email == email)
        ).first()

        if existing:
            raise ValueError(
                "Username or email already exists."
            )

        hashed = AuthService.hash_password(password)

        user = User(
            username=username,
            email=email,
            password_hash=hashed
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        AuthService.create_user_storage(user.id)

        return user

    @staticmethod
    def authenticate(
        db: Session,
        username: str,
        password: str
    ):

        user = db.query(User).filter(
            User.username == username
        ).first()

        if not user:
            return None

        if not AuthService.verify_password(
            password,
            user.password_hash
        ):
            return None

        return user

    @staticmethod
    def create_user_storage(user_id: str):

        user_folder = STORAGE_DIR / user_id

        folders = [
            "uploads",
            "chroma",
            "cache"
        ]

        user_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        for folder in folders:
            (user_folder / folder).mkdir(
                exist_ok=True
            )