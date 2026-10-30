"""ex14: 집계 - 간단 집계 메서드(sum, avg, max, min)와 aggregate 파이프라인."""
import asyncio

from beanie import Document
from pydantic import BaseModel, Field

from common import init


class Sale(Document):
    category: str
    qty: int
    price: int

    class Settings:
        name = "ex14_sales"


class CategoryRevenue(BaseModel):
    category: str = Field(alias="_id")  # $group의 _id를 이름 있는 필드로 받는다
    revenue: int
    orders: int


PIPELINE = [
    {"$group": {"_id": "$category",
                "revenue": {"$sum": {"$multiply": ["$qty", "$price"]}},
                "orders": {"$sum": 1}}},
    {"$sort": {"revenue": -1}},
]


async def main():
    async with init(Sale):
        await Sale.delete_all()
        await Sale.insert_many([
            Sale(category=c, qty=q, price=p)
            for c, q, p in [("pen", 1, 1000), ("pen", 3, 1000), ("book", 2, 15000), ("book", 1, 20000), ("cup", 5, 3000)]
        ])

        # 1. 간단 집계 - 필드 하나의 합계·평균·최댓값·최솟값. find() 조건과 함께 쓸 수 있다
        print("1) pen qty 합:", await Sale.find(Sale.category == "pen").sum(Sale.qty),
              "/ price 평균:", await Sale.avg(Sale.price),
              "/ 최고가:", await Sale.max(Sale.price), "/ 최저가:", await Sale.min(Sale.price))

        # 2. 주의: 대상 문서가 없으면 0이 아니라 None
        print("2) 없는 카테고리 합:", await Sale.find(Sale.category == "none").sum(Sale.qty))

        # 3. aggregate - 파이프라인 결과는 dict 목록
        print("3) dict:", await Sale.aggregate(PIPELINE).to_list())

        # 4. projection_model - 결과를 dict 대신 모델 객체로 받는다
        print("4) model:", await Sale.aggregate(PIPELINE, projection_model=CategoryRevenue).to_list())

        # 5. find(조건).aggregate - 조건이 $match로 파이프라인 앞에 붙는다
        #    주의: find에 붙인 sort/limit은 파이프라인 뒤에 붙는다. "qty가 가장 큰 1건(cup)만 집계"하려던
        #    코드가 $group 뒤에 없는 qty로 정렬하고 집계 결과에서 1건을 자른다
        #    → 정렬·개수 제한은 파이프라인 안에 직접 넣는다
        query = Sale.find(Sale.qty >= 2).sort(-Sale.qty).limit(1).aggregate(PIPELINE)
        print("5) 실제 파이프라인:", [list(stage)[0] for stage in query.get_aggregation_pipeline()])
        print("5) 결과:", await query.to_list())


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_beanie --eval "db.ex14_sales.aggregate([{\$group: {_id: '\$category', revenue: {\$sum: {\$multiply: ['\$qty', '\$price']}}}}])"
