from os import stat
from schemas.user import TokenData
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, status
from cruds.users import get_user
from sqlalchemy.orm.session import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password: str, hashed_password: str):
	return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
	return pwd_context.hash(password)

def authenticate_user(db: Session, email: str, password: str):
	user = get_user(db, email)

	if not user:
		raise HTTPException(status_code=403, detail="Authorization failed")
	
	if not verify_password(password, user.password_hash):
		raise HTTPException(status_code=403, detail="Password incorrect")
	
	return user
	
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
	to_encode = data.copy()
	if expires_delta:
		expire = datetime.utcnow() + expires_delta
	else:
		expire = datetime.utcnow() + timedelta(minutes=15)
	to_encode.update({"exp": expire})
	encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
	return encoded_jwt


async def get_current_user(db: Session, token: str = Depends(oauth2_scheme)):
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		email: str = payload.get("sub")
		if email is None:
			raise credentials_exception
		token_data = TokenData(email=email)
	except JWTError:
		raise credentials_exception
	user = get_user(db, token_data.email)
	if user is None:
		raise credentials_exception
	return user