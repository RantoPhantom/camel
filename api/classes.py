from pydantic import BaseModel

class ChatRequest(BaseModel):
    content: str

class ChatResponse(BaseModel):
    content: str

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    username: str
    role: str
