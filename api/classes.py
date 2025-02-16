from pydantic import BaseModel

class UserInfo(BaseModel):
    username: str
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

class GenerateMessageRequest(BaseModel):
    username: str
    content: str
    chat: Chat

class GenerateMessageResponse(BaseModel):
    message: Message

class GetAllChatRequest(BaseModel):
    username: str

class GetAllChatResponse(BaseModel):
    chats: list[Chat]

class GetChatRequest(BaseModel):
    username: str
    chat: Chat

class GetChatResponse(BaseModel):
    messages: list[Message]

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    username: str
    role: str
