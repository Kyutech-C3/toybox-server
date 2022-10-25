from fastapi.params import Security
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from db.models import Token, User
from db import get_db
from os import stat, environ
from schemas.user import TokenData, TokenResponse
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, status
from cruds.users import get_user
from sqlalchemy.orm.session import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional
from datetime import datetime, timedelta
from schemas.user import Token as TokenSchema
from utils.discord import DiscordAccessTokenResponse, discord_fetch_user, discord_refresh_token, discord_verify_user_belongs_to_valid_guild

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

SECRET_KEY = environ.get("TOKEN_SECRET_KEY")
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

def authenticate_discord_user(discord_token: DiscordAccessTokenResponse, db: Session = Depends(get_db)) -> TokenResponse:
	discord_user = discord_fetch_user(discord_token.access_token)

	u = db.query(User).filter(User.discord_user_id == discord_user.id).first()

	discord_verify_user_belongs_to_valid_guild(access_token=discord_token.access_token)

	if u == None:
		# user's first login 
		u = User(
			name=discord_user.username,
			email=discord_user.email,
			display_name=discord_user.username,
			discord_token=discord_token.access_token,
			discord_refresh_token=discord_token.refresh_token,
			discord_user_id=discord_user.id,
			avatar_url="https://cdn.discordapp.com/avatars/{user_id}/{avatar_id}.png".format(user_id = discord_user.id, avatar_id = discord_user.avatar)
		)
		db.add(u)
		db.commit()
	else:
		u.avatar_url="https://cdn.discordapp.com/avatars/{user_id}/{avatar_id}.png".format(user_id = discord_user.id, avatar_id = discord_user.avatar)
		db.commit()

	token_response = create_tokens(u, db)
	return token_response

def create_tokens(user: User, db: Session = Depends(get_db)) -> TokenResponse:
	new_refresh_token = create_refresh_token(user, db)
	new_access_token = create_access_token(new_refresh_token.user)

	t = TokenResponse(
		refresh_token=new_refresh_token.refresh_token,
		access_token=new_access_token,
		expired_at=new_refresh_token.expired_at.isoformat()
	)
	return t

def renew_token(refresh_token_str: str, db: Session = Depends(get_db)) -> TokenResponse:
	token, old_t = verify_refresh_token(refresh_token_str, db)

	# force expire old refresh token
	old_t.expired_at = datetime.now().isoformat()
	db.commit()

	u = db.query(User).filter(User.id == token.user.id).first()

	return create_tokens(u, db)

def create_refresh_token(
	user: User,
	db: Session = Depends(get_db),
	expired_delta: timedelta = timedelta(days=15)
) -> TokenSchema:
	t = Token(refresh_token=None, user_id=user.id)
	if expired_delta:
		t.expired_at = datetime.now() + expired_delta
	db.add(t)
	db.commit()
	token = TokenSchema.from_orm(t)
	return token

def verify_refresh_token(refresh_token: str, db: Session = Depends(get_db)) -> tuple[TokenSchema, Token]:
	t = db.query(Token).filter(Token.refresh_token == refresh_token).first()
	if t == None:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Specified refresh token not found"
		)
	
	token = TokenSchema.from_orm(t)
	if token.has_expired():
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Specified refresh token has expired"
		)

	return [token, t]
	
def create_access_token(user: User, expires_delta: Optional[timedelta] = None):
	to_encode = {
		"sub": user.email,
		"token_type": "bearer"
	}
	if expires_delta:
		expire = datetime.utcnow() + expires_delta
	else:
		expire = datetime.utcnow() + timedelta(minutes=15)
	to_encode["exp"] = expire
	encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
	return encoded_jwt

security = HTTPBearer(auto_error=False)


class GetCurrentUser:
	def __init__(self, auto_error: bool = True) -> None:
		self.auto_error = auto_error
	
	def __call__(
		self,
		db: Session = Depends(get_db),
		credentials: HTTPAuthorizationCredentials = Security(security)
	):
		try:
			if credentials == None:
				return self.handle_error(detail="Credential is missing")
			if credentials.scheme != 'Bearer':
				return self.handle_error(detail="Invalid scheme")

			payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
			email: str = payload.get("sub")
			if email is None:
				return self.handle_error(detail="Email is missing")
			token_data = TokenData(email=email)
		except JWTError:
			return self.handle_error(detail="JWT error")
		user = get_user(db, token_data.email)
		if user is None:
			return self.handle_error(detail="User not found")
		return user

	def handle_error(self, detail: str = "Authorization error"):
		if self.auto_error:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail=detail,
				headers={"WWW-Authenticate": "Bearer"},
			)
		else:
			return None
