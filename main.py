from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import schema
from fastapi_socketio import SocketManager
from socket_handlers import SocketHandlers

from routers import router

app = FastAPI()
socket_manager = SocketManager(app=app)

origins = [
    "http://localhost:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ['*'],
    allow_headers = ['*']
)

@app.middleware('http')
async def inject_user_id_into_request(request: Request, call_next):
    try:
        auth_header = request.headers['Authorization']
        if auth_header is not None:
            auth_header_array = auth_header.split(' ')
            if auth_header_array[0] == 'Bearer':
                request.state.user_id = auth_header_array[1]
            else:
                return HTTPException(400, "Type of Authorization Header is invalid.")

    except:
        pass
    response = await call_next(request)
    return response

@app.middleware('http')
async def inject_sio(request: Request, call_next):
    request.state.sio = socket_manager._sio
    response = await call_next(request)
    return response

socket_manager._sio.register_namespace(SocketHandlers('/'))

app.include_router(router)