"""예제 전체가 공유하는 MongoDB 비동기 연결 헬퍼."""
from pymongo import AsyncMongoClient

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "example_pymongo"


def get_client() -> AsyncMongoClient:
    """`async with get_client() as client:` 형태로 사용한다."""
    return AsyncMongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
