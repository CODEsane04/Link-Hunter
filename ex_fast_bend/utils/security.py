import bcrypt
import os
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

def hash_password(password : str) -> str :

    '''takes a plain-text password, generated a salt & returns a secure bcrypt hash string'''

    #bcrypt requires bytes so we encode to utf-8
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(pwd_bytes, salt)

    #return as a string to store easily in mongoDB
    return hashed_bytes.decode('utf-8')

def verify_password(plain_password : str, hashed_password : str) -> bool :
    """
    Verifies a plain-text candidate password against the stored bcrypt hash.
    Returns True if valid, False otherwise.
    """
    verdict = bcrypt.checkpw(
        plain_password.ecode('utf-8'),
        hashed_password.encode('utf-8')
    )

    return verdict


#===============================
#          JWT
#===============================

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def create_access_token(user_data : dict, expires_delta: Optional[timedelta] = None) -> str :
    """
    Creates a signed JWT access token with an expiration timestamp.
    """
    data_to_encode = user_data.copy() #.copy() is used beacuse if we directly assign data_to_encode = user_data, then this does not makes a copy of the dictioary, rather this another variable points to the same memory, so if any changes are made to this new variable, it corrupts the original one


    #calculate expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else :
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # add expiry time to the copy of user data that has to be encoded
    data_to_encode.update({"exp": expire})

    #sign and encode the token
    encoded_jwt_token = jwt.encode(data_to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt_token

def decode_access_token(access_token : str) -> Optional[dict] :
    """
    Decodes and verifies a JWT token.
    Returns the payload dictionary if valid, or None if expired/tampered with.
    """

    try : 
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=ALGORITHM)
        return payload
    except jwt.PyJWTError :
        # Token is either expired (ExpiredSignatureError) or invalid (InvalidTokenError)
        return None