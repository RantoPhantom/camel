from fastapi import HTTPException

class UserNotInDbError(HTTPException):
    def __init__(self):
        super().__init__(
                status_code=404,
                detail="user not found in db"
                )
