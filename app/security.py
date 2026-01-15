from fastapi import Header, HTTPException
from .config import settings

def require_internal_key(x_internal_key: str | None = Header(default=None, alias="X-Internal-Key")) -> None:
    if settings.internal_key and x_internal_key != settings.internal_key:
        raise HTTPException(status_code=401, detail="Invalid internal key")
