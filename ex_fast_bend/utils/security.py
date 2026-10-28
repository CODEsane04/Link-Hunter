import bcrypt

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
