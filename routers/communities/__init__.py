from cruds.communities import create_community, get_community_by_id, get_community_by_limit
from schemas.community import BaseCommunity, Community
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session
from cruds.users.auth import GetCurrentUser
from db import get_db
from typing import List

community_router = APIRouter()

@community_router.post('', response_model=Community, dependencies=[Depends(GetCurrentUser())])
async def post_community(payload: BaseCommunity, db: Session = Depends(get_db)):
    community = create_community(db, payload.name, payload.description)
    return community

@community_router.get('',response_model=List[Community])
async def get_communities(limit: int = 30, oldest_id: str = None, db: Session = Depends(get_db)):
    community_list = get_community_by_limit(db, limit, oldest_id)
    return community_list

@community_router.get('/{community_id}', response_model=Community)
async def get_community(community_id: str, db: Session = Depends(get_db)):
    community = get_community_by_id(db, community_id)
    return community