from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from database import SessionClass
from crud import *
import schema

import json

router = APIRouter()

def get_db():
  try:
    session = SessionClass()
    yield session
  except:
    session.rollback()
    raise
  finally:
    session.close()


@router.get('/')
async def root(request: Request, db: SessionClass = Depends(get_db)):
  await request.state.sio.emit('message', {}, namespace='/event', room='')
  return JSONResponse({"message": "OK"})

@router.post('/room', response_model=schema.CreateRoomResponse)
async def create_room_handler(req: schema.CreateRoomRequest, db: SessionClass = Depends(get_db)):
  res = create_room(db, req.user_name, req.room_name)
  response = schema.CreateRoomResponse(user=res['user'], room=res['room'])
  return response

@router.post('/room/{room_id}', response_model=schema.JoinRoomResponse)
async def join_room_handler(request: Request, req: schema.JoinRoomRequest, room_id: str, db: SessionClass = Depends(get_db)):
  res = join_room(db, req.user_name, room_id)
  response = schema.JoinRoomResponse(user=res['user'], room=res['room'])
  new_user_data = schema.NewUserResponse(id=response.user.id, name=response.user.name, room_id=response.user.room_id)
  await request.state.sio.emit('new_user', new_user_data, namespace='/event', room=response.room.id)
  return response

@router.post('/room/{room_id}/start_game')
async def start_game_handler(request: Request, req: schema.StartGameRequest, room_id: str, db: SessionClass = Depends(get_db)):
  stage = start_game(db, room_id, req.user_id)
  await request.state.sio.emit('start_game', stage, namespace='/event', room=room_id)
  return stage

@router.post('/room/{room_id}/result', response_model=schema.Result)
async def post_result_handler(request: Request, req: schema.PostResult, room_id: str, db: SessionClass = Depends(get_db)):
  if result_checker(db, room_id):
    response = schema.GameResultData(data=make_result_list(db, room_id))
    await request.state.sio.emit('game_result', response, namespace='/event', room=room_id)
  posted_result = post_result(db, room_id, req.user_id, req.hand)
  response = schema.Result(
    room_id=posted_result.room_id, 
    user_id=posted_result.user_id, 
    is_win=posted_result.is_win,
    stage=posted_result.stage,
    hand=posted_result.hand,
    )
  return response