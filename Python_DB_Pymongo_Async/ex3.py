"""ex3: find/find_one으로 조건에 맞는 문서를 조회한다."""
import asyncio

from common import DB_NAME, get_client

COLLECTION = "ex03_products"


async def main():
    async with get_client() as client:
        col = client[DB_NAME][COLLECTION]
        await col.delete_many({})
        await col.insert_many([
            {"name": "Keyboard", "price": 50, "category": "accessory"},
            {"name": "Monitor", "price": 300, "category": "display"},
            {"name": "Mouse", "price": 20, "category": "accessory"},
        ])

        # 1. find_one - 조건에 맞는 문서 하나만 조회
        print("find_one:", await col.find_one({"name": "Monitor"}))

        # 2. find + 필터 - category가 accessory인 것만 (async for로 순회)
        async for doc in col.find({"category": "accessory"}):
            print("accessory:", doc)

        # 3. 비교 연산자($gt) + 정렬 + projection(_id 제외, name/price만 반환)
        cursor = col.find(
            {"price": {"$gt": 25}},
            {"_id": 0, "name": 1, "price": 1},
        ).sort("price", -1)
        print("price > 25, 내림차순:", await cursor.to_list())


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_pymongo --eval "db.ex03_products.find({category:'accessory'})"
