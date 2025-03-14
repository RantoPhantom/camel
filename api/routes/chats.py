from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from ..classes import Chat, Message
from ..db import GetUserDb
from pydantic import BaseModel
import datetime

router = APIRouter()

class NewMessageReq(BaseModel):
    username: str
    chat_id: int
    message_content: str

class GetMessageFromChatReq(BaseModel):
    username: str
    chat_id: int

class GetMessageFromChatRes(BaseModel):
    messages: list[Message]

class NewChatReq(BaseModel):
    username: str
    message: str

class GenerateMessageReq(BaseModel):
    username: str
    content: str
    chat: Chat

class GenerateMessageRes(BaseModel):
    message: Message

class GetChatReq(BaseModel):
    username: str
    chat: Chat

class GetChatRes(BaseModel):
    messages: list[Message]

@router.get("/get-history")
async def get_all_chat(username: str) -> list[Chat]:
    user_db = GetUserDb(username)

    chats: list[Chat] = []

    query: str = '''
    select * from chats;
    '''
    db_res = user_db.cursor.execute(query).fetchall()
    if db_res == None:
        return []

    for chat in db_res:
        chats.append(Chat(
            chat_id=chat[0],
            title=chat[1],
            date_added=chat[2]
            ))
    return chats

@router.put("/new-chat", status_code=200)
async def insert_chat(request: NewChatReq) -> None:
    username: str = request.username
    message: str = request.message
    chat_title: str = message[0:20]

    user_db = GetUserDb(username)

    query: str = '''
    insert into chats(title, date_added)
    values (?,?)
    returning chat_id
    '''

    chat_id = user_db.cursor.execute(query, (chat_title, datetime.datetime.now().isoformat())).fetchone()[0]

    query: str = '''
    insert into messages(chat_id, message_content, sender, date_added)
    values (?,?,?,?);
    '''
    user_db.cursor.execute(query, (
        chat_id, 
        message,
        "user",
        datetime.datetime.now().isoformat()
        )
                           )

    user_db.connection.commit()
    return

@router.put("/new-message", status_code=200)
async def new_message(request: NewMessageReq) -> None:
    username = request.username
    chat_id = request.chat_id
    message_content = request.message_content
    user_db = GetUserDb(username)

    query: str = '''
    select * from chats where
    chat_id=?
    '''
    res = user_db.cursor.execute(query, [chat_id]).fetchone()
    if res == None:
        raise HTTPException(status_code=404, detail="chat_id not found in db")

    query = '''
    insert into messages(chat_id,message_content,sender,date_added)
    values(?,?,?,?);
    '''
    user_db.cursor.execute(query,(
        chat_id,
        message_content,
        "user",
        datetime.datetime.now().isoformat()
        ))
    user_db.connection.commit()
    return

@router.get("/get-chat-detail")
async def get_message_from_chat(username: str, chat_id: int) -> list[Message]:
    user_db = GetUserDb(username)

    query: str = '''
    select * from messages 
    where chat_id=?;
    '''
    res = user_db.cursor.execute(query, [chat_id]).fetchall()
    if res == None:
        return []
    
    return res

@router.delete("/remove-chat")
async def remove_chat(username: str ,chat_id: int) -> None:
    user_db = GetUserDb(username)

    query: str = '''
    delete from chats 
    where chat_id=?
    returning chat_id;
    '''
    res = user_db.cursor.execute(query, [chat_id]).fetchone()[0]
    if res == None:
        raise HTTPException(status_code=404, detail="this chat does not exist")

    user_db.connection.commit()
    return

@router.get("/search")
async def search_chat(username: str, search_string: str) -> list[Chat]:
    user_db = GetUserDb(username)
    response: list[Chat] = []

    query: str = '''
    select * from chats
    where chat_id like ?%;
    '''
    res = user_db.cursor.execute(query, [search_string]).fetchall()

    if res == [] :
        return response

    for chat in res:
        response.append(
                Chat(
                    chat_id=chat[0],
                    title=chat[1],
                    date_added=chat[2],
                    )
                )
        return response

    return response
