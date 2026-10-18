"""ex10: 텍스트 인덱스와 $text 검색으로 전문(full-text) 검색을 한다."""
import asyncio

from pymongo import TEXT

from common import DB_NAME, get_client

COLLECTION = "ex10_articles"


async def main():
    async with get_client() as client:
        col = client[DB_NAME][COLLECTION]
        await col.delete_many({})
        await col.drop_indexes()

        # 1. 텍스트 인덱스 생성 - content 필드에 대한 전문 검색 인덱스
        await col.create_index([("content", TEXT)])

        await col.insert_many([
            {"title": "pymongo 소개", "content": "pymongo는 MongoDB aggregation pipeline을 다룬다"},
            {"title": "비동기 입문", "content": "python asyncio의 기본 개념을 설명한다"},
            {"title": "집계 심화", "content": "MongoDB aggregation의 고급 연산자를 살펴본다"},
        ])

        # 2. $text + $search - "aggregation"이 포함된 문서를 검색하고 관련도(textScore)순 정렬
        cursor = col.find(
            {"$text": {"$search": "aggregation"}},
            {"_id": 0, "title": 1, "score": {"$meta": "textScore"}},
        ).sort([("score", {"$meta": "textScore"})])
        print("'aggregation' 검색 결과:", await cursor.to_list())


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_pymongo --eval "db.ex10_articles.find({\$text:{\$search:'aggregation'}})"
