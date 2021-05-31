from models import Room, User, Result
from database import SessionClass
from contextlib import contextmanager
import schema
from fastapi import HTTPException

@contextmanager
def session_manager(session):
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise

# Turn User.is_host to True
def user_to_host(db: SessionClass, user: User):
    with session_manager(db) as session:
        user = session.query(User).filter(User.id == user.id)
        user.is_host = True

# set User's room
def set_user_to_room(user: User, room: Room):
        user.room = room

# create User (just like a session)
def create_user(db: SessionClass, name):
    with session_manager(db) as session:
        user = User(name=name)
        session.new(user)
        return user

# create Room
def create_room(db: SessionClass, user_name, room_name):
    with session_manager(db) as session:
        room = Room(name=room_name)
        session.add(room)
        session.commit()
        user = User(name=user_name, room_id=room.id)
        session.add(user)
        session.commit()
        room.host_user_id = user.id
        session.commit()
        return {
            'user': user,
            'room': room
        }

def join_room(db: SessionClass, user_name, room_id):
    with session_manager(db) as session:
        if session.query(Room).filter(Room.id == room_id).count() == 0:
            raise HTTPException(status_code=404)
        room = session.query(Room).filter(Room.id == room_id).first()
        user = User(name=user_name, room_id=room.id)
        session.add(user)
        return {
            'user': user,
            'room': room
        }

def start_game(db: SessionClass, room_id, user_id):
    with session_manager(db) as session:
        if session.query(Room).filter(Room.id == room_id).count() == 0:
            raise HTTPException(status_code=404)
        room = session.query(Room).filter(Room.id == room_id).first()
        host_users = session.query(User).filter(User.id == user_id, User.room_id == room.id)
        if host_users.count() == 0:
            raise HTTPException(status_code=404)
        elif host_users.first() != room.host_user:
            raise HTTPException(status_code=400)
        room.latest_stage += 1
        return {
            'stage': room.latest_stage
        }

def make_result_list(db: SessionClass, room_id):
    with session_manager(db) as session:
        if session.query(Room).filter(Room.id == room_id).count() == 0:
            raise HTTPException(status_code=404)
        room = session.query(Room).filter(Room.id == room_id).first()
        result_list = []
        users_result = session.query(Result).filter(Result.room_id == room_id, Result.stage == room.latest_stage).all()
        for user_result in users_result:
            result_list.append(user_result)
        return result_list

def result_checker(db: SessionClass, room_id):
    with session_manager(db) as session:
        if session.query(Room).filter(Room.id == room_id).count() == 0:
            raise HTTPException(status_code=404)
        room = session.query(Room).filter(Room.id == room_id).first()
        result_counter = session.query(Result).filter(Result.room_id == room.id, Result.stage == room.latest_stage).count()
        return result_counter == len(room.users)

def post_result(db: SessionClass, room_id, user_id, user_hand):
    with session_manager(db) as session:
        if session.query(Room).filter(Room.id == room_id).count() == 0:
            raise HTTPException(status_code=404)
        room = session.query(Room).filter(Room.id == room_id).first()
        if user_id == room.host_user_id:
            result = Result(room_id=room.id, user_id=user_id, stage=room.latest_stage, hand=user_hand)
            session.add(result)
            client_users_result = session.query(Result).filter(Result.room_id == room_id, Result.stage == room.latest_stage).all()
            for client_user_result in client_users_result:
                if (client_user_result.hand - user_hand) % 3 == 1:
                    client_user_result.is_win = True
                else:
                    client_user_result.is_win = False
            session.commit()
        else:
            host_results = session.query(Result).filter(Result.user_id == room.host_user_id, Result.room_id == room.id, Result.stage == room.latest_stage)
            if host_results.count() == 0:
                result = Result(room_id=room.id, user_id=user_id, stage=room.latest_stage, hand=user_hand)
                session.add(result)
            else:
                host_result = host_results.first()
                if (user_hand - host_result.hand) % 3 == 1:
                    result = Result(room_id=room.id, user_id=user_id, is_win=True, stage=room.latest_stage, hand=user_hand)
                    session.add(result)
                else:
                    result = Result(room_id=room.id, user_id=user_id, is_win=False, stage=room.latest_stage, hand=user_hand)
                    session.add(result)
        return result