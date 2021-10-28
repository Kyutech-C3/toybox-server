from fastapi import HTTPException
from sqlalchemy.sql.functions import user
from db import models
from sqlalchemy.orm.session import Session
from schemas.user import User as UserSchema


def get_user(db: Session, email: str) -> UserSchema:
	user_orm = db.query(models.User).filter(models.User.email == email).first()
	user = UserSchema.from_orm(user_orm)
	return user

def get_user_by_id(db: Session, user_id: str) -> UserSchema:
	user_orm = db.query(models.User).filter(models.User.id == user_id).first()
	if user_orm is None:
		raise HTTPException(
            status_code=404,
            detail="The tag is not exist"
        )
	user = UserSchema.from_orm(user_orm)
	return user

def get_users(db: Session, limit: int, offset_id: str) -> list[UserSchema]:
	user_list = []
	users = db.query(models.User)

	if users is None:
		raise HTTPException(
            status_code=404,
            detail="User is not exist"
        )
	
	if offset_id is not None:
		limit_users = db.query(models.User).filter(models.User.id == offset_id).first()
		if limit_users is None:
			raise HTTPException(
				status_code=404,
				detail="Users are not exist"
			)
		limit_created_at = limit_users.created_at
		users = users.filter(models.User.created_at > limit_created_at)
	users = users.limit(limit)
	users = users.all()
	
	for user_orm in users:
		user = UserSchema.from_orm(user_orm)
		user_list.append(user)

	return user_list

def create_user(db: Session, user: UserSchema):
	db.add(user)
	db.commit()

	return get_user(db, user.email)

def change_usre_info(db: Session, user_id, display_name, profile, avatar_url) -> UserSchema:
	user_orm = db.query(models.User).filter(models.User.id == user_id).first()
	if user_orm is None:
		raise HTTPException(status_code=404, detail="The user specified by id is not exist")

	user_orm.display_name = user_orm.display_name if display_name is None else display_name
	user_orm.profile = user_orm.profile if profile is None else profile
	user_orm.avatar_url = user_orm.avatar_url if avatar_url is None else avatar_url

	db.commit()
	db.refresh(user_orm)
	user = UserSchema.from_orm(user_orm)

	return user
