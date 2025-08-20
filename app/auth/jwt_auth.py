from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.auth.jwt_handler import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_curent_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return payload
