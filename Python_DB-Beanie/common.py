"""예제 전체가 공유하는 MongoDB 연결 + Beanie 초기화 헬퍼."""
from contextlib import asynccontextmanager

from beanie import init_beanie
from pymongo import AsyncMongoClient

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "example_beanie"


@asynccontextmanager
async def init(*models):
    """`async with init(User, ...) as db:` 형태로 사용한다.

    Beanie 2.x는 motor 대신 pymongo의 AsyncMongoClient를 사용한다.
    init_beanie가 모델 ↔ 컬렉션을 연결하고, 모델에 선언된 인덱스도 이때 생성한다.
    """
    client = AsyncMongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    try:
        db = client[DB_NAME]
        await init_beanie(database=db, document_models=list(models))
        yield db
    finally:
        await client.close()
