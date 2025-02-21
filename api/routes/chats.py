from fastapi import APIRouter
from ..classes import GetAllChatReq, GetAllChatRes, Chat


router = APIRouter()

@router.post("/get-all-chats")
async def get_all_chat(request: GetAllChatReq) -> GetAllChatRes:
    response: GetAllChatRes = GetAllChatRes(
            chats=[Chat(
                chat_id="this asdfdsaf",
                title="this",
                date_added="no"
                )]
            )
    return response
