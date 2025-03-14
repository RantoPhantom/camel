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
    chat_id: int
    title: str
    date_added: str
