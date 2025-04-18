from multimodal_rag import DiabetesKnowledgeBase
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import torch

print("Torch version:", torch.__version__)
print("Is ROCm available?:", torch.version.hip)
print("CUDA available?:", torch.cuda.is_available())
print("MPS available (for macOS)?:", torch.backends.mps.is_available())
print("Torch device:", torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"))

class AnswerReq(BaseModel):
    message: str

class AnswerRes(BaseModel):
    message: str

load_dotenv("./.env")
app = FastAPI()

origins = [
        "*"
        ]

app.add_middleware(
        CORSMiddleware,
        allow_origins = origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
        )

kb = DiabetesKnowledgeBase()

#kb.process_all_pdfs()
#print(kb.get_processed_files_status())

@app.post("/answer")
async def answer(request: AnswerReq) -> AnswerRes:
    message: str = request.message
    response: AnswerRes = AnswerRes(message="")
    try: 
        response = AnswerRes(message=kb.answer_question(message))
    except Exception as e:
        raise e
        raise HTTPException(status_code=500, detail=f"sumthin aint right {str(e)}")
    return response

@app.get("/healthcheck", status_code=200)
async def healthcheck() -> None:
    return

uvicorn.run(app, host="0.0.0.0", port=4242)
