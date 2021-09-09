from fastapi import HTTPException
from db.models import User
from sqlalchemy.orm.session import Session


def get_user(db: Session, email: str) -> User:
	u = db.query(User).filter(User.email == email).first()

	return u

def create_user(db: Session, user: User):
	db.add(user)
	db.commit()

	return get_user(db, user.email)