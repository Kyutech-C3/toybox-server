from fastapi import HTTPException
from db.models import User
from sqlalchemy.orm.session import Session


def get_user(db: Session, email: str):
	user = db.query(User).filter(User.email == email).first()

	return user

def create_user(db: Session, user: User):
	db.add(user)
	db.commit()

	return get_user(db, user.email)