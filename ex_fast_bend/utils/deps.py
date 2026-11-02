from utils.security import decode_access_token
import os
from dotenv import load_dotenv
from fastapi import HTTPException

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from database import users_collection

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# input = access_token
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
async def get_current_user(access_token : str = Depends(oauth2_scheme)) -> dict :

    decoded_payload = decode_access_token(access_token, SECRET_KEY)

    if not decoded_payload or "sub" not in decoded_payload:
        raise HTTPException(
            status_code=401,
            detail="could not validate crednetials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    current_user_email = decoded_payload["sub"]

    
    current_user = await users_collection.find_one({"email" : current_user_email})

    if not current_user :
        raise HTTPException(
                status_code=401,
                detail="user is unauthorized",
                headers={"WWW-Authenticate": "Bearer"}
            )
    else :
        return current_user

    
    

    
