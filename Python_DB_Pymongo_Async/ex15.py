"""ex15: aggregate()로 $match/$group/$sort 파이프라인을 실행한다."""
import asyncio

from common import DB_NAME, get_client

COLLECTION = "ex15_orders"


async def main():
    async with get_client() as client:
        col = client[DB_NAME][COLLECTION]
        await col.delete_many({})
        await col.insert_many([
            {"customer": "alice", "category": "food", "amount": 12},
            {"customer": "alice", "category": "book", "amount": 30},
            {"customer": "bob", "category": "food", "amount": 8},
            {"customer": "bob", "category": "food", "amount": 20},
            {"customer": "bob", "category": "book", "amount": 15},
        ])

        # 1. $match - food 카테고리만 필터링
        cursor = await col.aggregate([{"$match": {"category": "food"}}])
        print("food만:", await cursor.to_list())

        # 2. $group + $sort - 고객별 총액/평균/건수 집계 후 총액 내림차순 정렬
        cursor = await col.aggregate([
            {"$group": {
                "_id": "$customer",
                "total": {"$sum": "$amount"},
                "avg": {"$avg": "$amount"},
                "count": {"$sum": 1},
            }},
            {"$sort": {"total": -1}},
        ])
        print("고객별 집계(총액 내림차순):", await cursor.to_list())

        # 3. $match + $group 조합 - food 카테고리만 고객별로 합산
        cursor = await col.aggregate([
            {"$match": {"category": "food"}},
            {"$group": {"_id": "$customer", "food_total": {"$sum": "$amount"}}},
        ])
        print("고객별 food 합계:", await cursor.to_list())


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_pymongo --eval "db.ex15_orders.aggregate([{\$group:{_id:'\$customer',total:{\$sum:'\$amount'}}}])"
