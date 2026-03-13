from typing import Optional
from sqlalchemy.orm import Session
import models
from repositories.base import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(models.User, db)

    def get_by_username(self, username: str) -> Optional[models.User]:
        return self.db.query(models.User).filter(models.User.username == username).first()

    def create_user(self, username: str, hashed_password: str, role: str) -> models.User:
        user = models.User(username=username, hashed_password=hashed_password, role=role)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
