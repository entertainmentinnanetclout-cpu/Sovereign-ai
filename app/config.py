from pydantic import BaseModel
import os

class Settings(BaseModel):
    internal_key: str = os.getenv("SOVEREIGN_INTERNAL_KEY", "")
    timezone: str = os.getenv("TZ", "Africa/Johannesburg")

settings = Settings()
