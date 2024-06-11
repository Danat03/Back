from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from envparse import Env

load_dotenv()
env = Env()

ekb_timezone = ZoneInfo("Asia/Yekaterinburg")

DATABASE_URL: str = env.str("DATABASE_URL", default="postgresql+asyncpg://postgres:postgres@localhost:5432/postgres")
REDIS_URL: str  = env.str("REDIS_URL", default="redis://localhost:6379")

SECRET_KEY: str  = env.str("SECRET_KEY", default="secret_key")
ALGORITHM: str = env.str("ALGORITHM", default="HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int  = env.int("ACCESS_TOKEN_EXPIRE_MINUTES", default=30)