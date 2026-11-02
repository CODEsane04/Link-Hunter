from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timezone
from bson import ObjectId

#Import database colletion
from database import users_collection

#Import schemas
from schemas.user_schema import UserCreate, UserInDB, UserLogin, UserResponse, TokenData, Token

#import all the security helpers
from utils.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ==========================================
# 1. SIGNUP ROUTE
# ==========================================

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data : UserCreate) :
    user_email = user_data["email"]
    user_pass = user_data["password"]

    #1. check if the user id already present in mogodb
    existing_user = await users_collection.find_one({"email" : user_email})
    if existing_user :
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email alrady exists"
        )

    # else this means that he/she is a new user

    #2. hash the raw password
    hashed_user_pass = hash_password(user_pass)

    #3 create new entry in mongodb
    new_user = {
        "email" : user_email,
        "hashed_password" : hashed_user_pass,
        "created_at" : datetime.now(timezone.utc)
    }

    #4 insert the new user in Db
    result = await users_collection.insert_one(new_user)

    #5. return safe user respomse
    return UserResponse(
        id=str(result.inserted_id),
        email=new_user["email"],
        created_at=new_user["created_at"]
    )

# ==========================================
# 2. LOGIN ROUTE
# ==========================================

@router.post("/login", response_model=Token)
async def login(credentials : UserLogin) :

    #find the user
    user = await users_collection.find_one({"email" : credentials["email"]})

    #2 if the user does not exist, or the pass word does not match, return 401
    # (Security tip: Never reveal whether it was the email or password that was wrong)

    if not user or not verify_password(credentials["password"], user["hashed_password"]) :
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    #if no exception is raised, means the user is valid, assign him/her a jwt token

    #3 create a jwt access token
    access_token = create_access_token(user_data={"sub" : user["email"]})

    #4 return the token matching Token schema
    return Token(access_token=access_token, token_type="bearer")

