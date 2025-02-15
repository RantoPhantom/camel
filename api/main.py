from fastapi import FastAPI
#from .ai_model import pipe
from .classes import ChatRequest, ChatResponse
from .db import GetUserDb

app = FastAPI()
model_path = "./model"

test = GetUserDb("this is not a viable thing/")

@app.post("/")
def index(request: ChatRequest) -> ChatResponse:
    response: ChatResponse = ChatResponse(
            content=request.content
            )
    print(response)
    return response
