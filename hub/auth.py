from fastapi import Header, HTTPException
from config import settings


def require_key(x_api_key: str = Header(...)):
    if x_api_key != settings.ACCESS_KEY:
        raise HTTPException(status_code=401, detail="Access key invÃ¡lida")

