from fastapi import FastAPI
from .ai_model import pipe
from .classes import ChatRequest, ChatResponse

app = FastAPI()

model_path = "./model"

@app.get("/")
def index(request: ChatRequest) -> ChatResponse:
    response: ChatResponse = ChatResponse(
            content = str(pipe(request.content))
            )
    print(response)
    return response
