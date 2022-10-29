from fastapi import HTTPException
from sqlalchemy import desc
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

def get_users(db: Session, limit: int = 30, oldest_user_id: str = None, newest_user_id: str = None) -> list[UserSchema]:
	user_list = []
	users = db.query(models.User).order_by(desc(models.User.updated_at))

	if users is None:
		raise HTTPException(
            status_code=404,
            detail="User is not exist"
        )
	
	if oldest_user_id:
		oldest_user = db.query(models.User).filter(models.User.id == oldest_user_id).first()
		if oldest_user is None:
			raise HTTPException(
				status_code=400,
				detail="oldest user are not exist"
			)
		users = users.filter(models.User.updated_at > oldest_user.updated_at)
	if newest_user_id:
		newest_user = db.query(models.User).filter(models.User.id == newest_user_id).first()
		if newest_user is None:
			raise HTTPException(
				status_code=400,
				detail="newest user are not exist"
			)
		users = users.filter(models.User.updated_at < newest_user.updated_at)
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

def change_user_info(db: Session, user_id: str, display_name: str, profile: str, avatar_url: str, twitter_id: str, github_id: str) -> UserSchema:
	user_orm = db.query(models.User).filter(models.User.id == user_id).first()
	if user_orm is None:
		raise HTTPException(status_code=404, detail="The user specified by id is not exist")

	user_orm.display_name = user_orm.display_name if display_name is None else display_name
	user_orm.profile = user_orm.profile if profile is None else profile
	user_orm.avatar_url = user_orm.avatar_url if avatar_url is None else avatar_url
	user_orm.twitter_id = user_orm.twitter_id if twitter_id is None else twitter_id
	user_orm.github_id = user_orm.github_id if github_id is None else github_id

	db.commit()
	db.refresh(user_orm)
	user = UserSchema.from_orm(user_orm)

	return user
