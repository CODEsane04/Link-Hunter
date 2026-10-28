from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

#1. shcema for user registration

class UserCreate(BaseModel) :
    email: EmailStr
    password: str = Field(min_length=6, description="Password must be atleast 6 characters")

#2 schema for user login

class UserLogin(BaseModel) :
    email : EmailStr
    password: str

#schema for returning user data safely
class UserResponse(BaseModel) :
    id : str
    email : EmailStr

    class Config:
        # Allows Pydantic to read MongoDB dictionary data smoothly
        from_attributes= True

#schema for JWT token response
class Token(BaseModel) :
    access_token : str
    token_type: str = "bearer"

# Schema for data stored inside the JWT token payload
class TokenData(BaseModel) :
    email : Optional[str] = None

#schem to store user info in the mongoDB
class UserInDB(BaseModel):
    id: Optional[str] = None
    email: EmailStr
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)