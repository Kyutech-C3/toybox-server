from os import access
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from starlette import status
from cruds.users.auth import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token, get_password_hash
from fastapi.exceptions import HTTPException
from cruds.users import create_user, get_user
from schemas.user import UserCreateRequest, UserWithPlainPassword
from fastapi.params import Depends
from db.models import User as UserModel
from schemas.user import User
from db import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta

auth_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@auth_router.post('/sign_up', response_model=User)
def sign_up(user_request: UserCreateRequest, db: Session = Depends(get_db)):
	existing_user = get_user(db, user_request.email)
	if existing_user:
		raise HTTPException(status_code=400, detail="User has already exists")

	hashed_password = get_password_hash(user_request.password)
	user = UserModel(
		name=user_request.name,
		email=user_request.email,
		password_hash=hashed_password,
		display_name=user_request.display_name,
		avatar_url=user_request.avatar_url,
	)

	created_user = create_user(db, user)

	if not created_user:
		raise HTTPException(status_code=500, detail="Couldn't create user")	

	return User.from_orm(created_user)

@auth_router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
	user = authenticate_user(db, form_data.username, form_data.password)
	if not user:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect email or password",
		)
	access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
	access_token = create_access_token(
		data={"sub": user.email, "token_type": "bearer"},
		expires_delta=access_token_expires
	)
	return {"access_token": access_token, "token_type": "bearer"}