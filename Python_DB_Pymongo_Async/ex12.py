"""ex12: bulk_write로 insert/update/delete를 한 번에 실행한다."""
import asyncio

from pymongo import DeleteOne, InsertOne, UpdateOne

from common import DB_NAME, get_client

COLLECTION = "ex12_inventory"


async def main():
    async with get_client() as client:
        col = client[DB_NAME][COLLECTION]
        await col.delete_many({})
        await col.insert_many([
            {"sku": "A1", "stock": 10},
            {"sku": "A2", "stock": 0},
            {"sku": "A3", "stock": 5},
        ])

        # 여러 종류의 연산을 한 번의 요청으로 모아 실행
        result = await col.bulk_write([
            InsertOne({"sku": "A4", "stock": 20}),             # 1. 신규 재고 추가
            UpdateOne({"sku": "A1"}, {"$inc": {"stock": -3}}),  # 2. 재고 차감
            UpdateOne(                                          # 3. 없으면 생성(upsert)
                {"sku": "A5"}, {"$set": {"stock": 1}}, upsert=True
            ),
            DeleteOne({"sku": "A2"}),                           # 4. 재고 0인 품목 삭제
        ])

        print(
            "inserted/matched/modified/upserted/deleted:",
            result.inserted_count,
            result.matched_count,
            result.modified_count,
            result.upserted_count,
            result.deleted_count,
        )
        print("최종 재고:", await col.find({}, {"_id": 0}).sort("sku", 1).to_list())


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_pymongo --eval "db.ex12_inventory.find().sort({sku:1})"
