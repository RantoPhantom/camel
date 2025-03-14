from fastapi import APIRouter, HTTPException
from ..db import GetUserDb, CreateUserDb, CheckBanned
from ..classes import UserInfo
from pydantic import BaseModel
import bcrypt
import datetime
import time

router = APIRouter()

class LoginReq(BaseModel):
    username: str
    password: str

class LoginRes(BaseModel):
    username: str
    role: str

class RegisterReq(BaseModel):
    username: str
    icon_file: str
    role: str
    password: str

class RegisterRes(BaseModel):
    username: str
    role: str

@router.post("/login")
async def login(request: LoginReq) -> LoginRes:
    response: LoginRes
    username = request.username
    if CheckBanned(username):
        raise HTTPException(status_code=400, detail="the username contains banned characters")

    password = request.password
    if username == "" or password == "":
        raise HTTPException(status_code=400, detail="the username and or passwrd is empty")

    user_db_connection = GetUserDb(username)

    if user_db_connection == None:
        # sleeping to prevent heuristics attacks
        time.sleep(0.1)
        raise HTTPException(status_code=404, detail="username or password is wrong")

    user_info = user_db_connection.get_info()

    if bcrypt.checkpw(password.encode('utf-8'), user_info.password_hash.encode('utf-8')):
        response = LoginRes(
                username=user_info.username,
                role=user_info.role
                )
        user_db_connection.close()
        return response
    else:
        raise HTTPException(status_code=404, detail="username or password is wrong")

@router.put("/signup")
async def signup(request: RegisterReq) -> RegisterRes:
    response: RegisterRes
    username = request.username

    if CheckBanned(username):
        raise HTTPException(status_code=400, detail="the username contains banned characters")

    password = request.password
    role = request.role
    icon_file = request.icon_file

    user_db = GetUserDb(username)

    if user_db != None:
        raise HTTPException(status_code=409, detail="this user is already registered")

    user_db = CreateUserDb(UserInfo(
        username=username,
        password_hash=bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8'),
        role=role,
        icon_file=icon_file,
        date_added=datetime.datetime.now().isoformat()
        ))

    user = user_db.get_info()
    response = RegisterRes(
            username=user.username,
            role=user.role
            )
    user_db.close()

    return response
