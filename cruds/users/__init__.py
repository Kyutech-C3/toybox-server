from fastapi import HTTPException
from sqlalchemy.sql.functions import user
from db.models import User
from sqlalchemy.orm.session import Session


def get_user(db: Session, email: str) -> User:
	u = db.query(User).filter(User.email == email).first()

	return u

def get_user_by_id(db: Session, user_id: str) -> User:
	user = db.query(User).filter(User.id == user_id).first()

	return user

def get_users(db: Session) -> list[User]:
	users = db.query(User).all()
	user_list = []
	for user in users:
		user_list.append(user)

	return user_list

def create_user(db: Session, user: User):
	db.add(user)
	db.commit()

	return get_user(db, user.email)

def change_usre_info(db: Session, user_id, display_name, profile, avatar_url) -> User:
	user_orm = db.query(User).filter(User.id == user_id).first()
	if user_orm is None:
		raise HTTPException(status_code=403, detail="The user specified by id is not exist")

	user_orm.display_name = user_orm.display_name if display_name is None else display_name
	user_orm.profile = user_orm.profile if profile is None else profile
	user_orm.avatar_url = user_orm.avatar_url if avatar_url is None else avatar_url

	db.commit()
	db.refresh(user_orm)

	return user_orm
