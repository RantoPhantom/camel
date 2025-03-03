from pydantic import BaseModel

class UserInfo(BaseModel):
    username: str
    password_hash: str
    role: str
    icon_file: str
    date_added: str

class Message(BaseModel):
    message_id: str
    message_content: str
    sender: str
    date_added: str

class Chat(BaseModel):
    chat_id: str
    title: str
    date_added: str

class GenerateMessageReq(BaseModel):
    username: str
    content: str
    chat: Chat

class GenerateMessageRes(BaseModel):
    message: Message

class GetAllChatReq(BaseModel):
    username: str

class GetAllChatRes(BaseModel):
    chats: list[Chat]

class GetChatReq(BaseModel):
    username: str
    chat: Chat

class GetChatRes(BaseModel):
    messages: list[Message]

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
