"""ex16: $lookup으로 다른 컬렉션을 조인하고 $unwind/$project로 결과를 정리한다."""
import asyncio

from common import DB_NAME, get_client

CUSTOMER_COLLECTION = "ex16_customers"
ORDER_COLLECTION = "ex16_orders"


async def main():
    async with get_client() as client:
        db = client[DB_NAME]
        customers = db[CUSTOMER_COLLECTION]
        orders = db[ORDER_COLLECTION]
        await customers.delete_many({})
        await orders.delete_many({})
        await customers.insert_many([
            {"_id": "c1", "name": "Alice"},
            {"_id": "c2", "name": "Bob"},
        ])
        await orders.insert_many([
            {"customer_id": "c1", "amount": 30},
            {"customer_id": "c1", "amount": 12},
            {"customer_id": "c2", "amount": 50},
        ])

        # 1. $lookup - orders.customer_id를 customers._id와 조인 (SQL의 JOIN에 대응)
        #    결과는 "customer" 필드에 배열로 들어온다 (여러 건이 매칭될 수 있어서)
        # 2. $unwind - 매칭이 항상 1건이라는 걸 알 때, 배열을 펼쳐서 단일 객체로 만든다
        # 3. $project - 필요한 필드만 추려서 깔끔하게 정리한다
        cursor = await orders.aggregate([
            {
                "$lookup": {
                    "from": CUSTOMER_COLLECTION,
                    "localField": "customer_id",
                    "foreignField": "_id",
                    "as": "customer",
                }
            },
            {"$unwind": "$customer"},
            {"$project": {"_id": 0, "amount": 1, "customer_name": "$customer.name"}},
        ])
        print("주문 + 고객 정보 조인:", await cursor.to_list())


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_pymongo --eval "db.ex16_orders.aggregate([{\$lookup:{from:'ex16_customers',localField:'customer_id',foreignField:'_id',as:'customer'}}])"
