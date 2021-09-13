from schemas.user import User
from cruds.communities import create_community
from schemas.community import BaseCommunity, Community
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session
from cruds.users.auth import GetCurrentUser
from db import get_db

community_router = APIRouter()

@community_router.post('', response_model=Community, dependencies=[Depends(GetCurrentUser())])
async def post_community(payload: BaseCommunity, db: Session = Depends(get_db)):
    community = create_community(db, payload.name, payload.description)
    return community
