from fastapi import FastAPI
from fastapi.responses import RedirectResponse
#from .ai_model import pipe
from .classes import GenerateMessageRequest, GenerateMessageResponse, Message
from .db import GetUserDb

app = FastAPI()
model_path = "./model"

test = GetUserDb("test_user")

@app.get("/")
def index() -> RedirectResponse:
    return RedirectResponse("/docs")

@app.post("/generate-message")
def chat(request: GenerateMessageRequest) -> GenerateMessageResponse:
    response: GenerateMessageResponse = GenerateMessageResponse(
            message=Message(
                message_id="heehe",
                message_content=request.content,
                sender="bot",
                date_added="no"
                )
            )
    return response
