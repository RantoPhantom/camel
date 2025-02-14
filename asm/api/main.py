from fastapi import FastAPI
from .ai_model import pipe
from pydantic import BaseModel

class Request(BaseModel):
    content: str

class Response(BaseModel):
    content: str
    
app = FastAPI()

model_path = "./model"

@app.get("/")
def index(request: Request):
    response = pipe(request.content, max_length=100)
    print(response)
    return response
