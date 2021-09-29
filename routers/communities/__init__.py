from cruds.communities import create_community, delete_community_by_id, get_community_by_id, get_community_list, put_community_by_id
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
    community_list = get_community_list(db, limit, oldest_id)
    return community_list

@community_router.get('/{community_id}', response_model=Community)
async def get_community(community_id: str, db: Session = Depends(get_db)):
    community = get_community_by_id(db, community_id)
    return community

@community_router.put('/{community_id}', response_model=Community, dependencies=[Depends(GetCurrentUser())])
async def put_community(payload: BaseCommunity, community_id: str, db: Session = Depends(get_db)):
    community_put = put_community_by_id(db, payload.name, payload.description, community_id)
    return community_put

@community_router.delete('/{community_id}', response_model=Community, dependencies=[Depends(GetCurrentUser())])
async def delete_community(community_id: str, db: Session = Depends(get_db)):
    delete_community_by_id(db, community_id)