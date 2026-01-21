from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.auth import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    if await blacklist_collection.find_one({"token": token}):
        raise HTTPException(status_code=401, detail="Token revoked")

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload

def require_role(required_role: str):
    def role_checker(user=Depends(get_current_user)):
        if user["role"] != required_role:
            raise HTTPException(status_code=403, detail="Access denied")
        return user
    return role_checker