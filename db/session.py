from typing import Generator
import asyncpg
import ssl
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from settings import DATABASE_URL

##############################################
# BLOCK FOR COMMON INTERACTION WITH DATABASE #
##############################################

# Create SSL context for client connections
ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
ssl_context.load_verify_locations(cafile="certs/rootCA.crt")
ssl_context.load_cert_chain(certfile="certs/client.crt", keyfile="certs/client.key")

# Allow self-signed certificate
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_OPTIONAL

async def connect():
    return await asyncpg.connect(
        user="postgres",
        password="postgres",
        database="postgres",
        host="127.0.0.1",
        port=5432,
        ssl=ssl_context
    )

engine = create_async_engine(
    DATABASE_URL,
    future=True,
    execution_options={"isolation_level": "AUTOCOMMIT"},
    connect_args={
        "ssl": ssl_context
    }
)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession) # noqa

async def get_db() -> Generator:
    async with async_session() as session:
        yield session
