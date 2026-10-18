"""ex2: 문서를 하나/여러 개 삽입한다 (insert_one, insert_many)."""
import asyncio

from common import DB_NAME, get_client

COLLECTION = "ex02_users"


async def main():
    async with get_client() as client:
        col = client[DB_NAME][COLLECTION]
        await col.delete_many({})  # 이전 실행 결과 초기화 (다시 실행해도 같은 상태로 시작)

        # 1. 문서 하나 삽입 - inserted_id로 생성된 _id 확인
        result = await col.insert_one({"name": "Alice", "age": 30})
        print("inserted_id:", result.inserted_id)

        # 2. 문서 여러 개 삽입 - inserted_ids 개수로 확인
        result = await col.insert_many([
            {"name": "Bob", "age": 25},
            {"name": "Carol", "age": 35},
        ])
        print("inserted_ids:", result.inserted_ids)

        print(f"{COLLECTION} 문서 수:", await col.count_documents({}))


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_pymongo --eval "db.ex02_users.find().pretty()"
