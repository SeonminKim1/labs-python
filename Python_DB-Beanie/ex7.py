"""ex7: 중첩 모델(BaseModel)과 리스트 필드 조회 (dot 경로, 배열 매칭, All, ElemMatch)."""
import asyncio

from beanie import Document
from beanie.operators import All, ElemMatch
from pydantic import BaseModel

from common import init


class Customer(BaseModel):
    name: str
    city: str


class Item(BaseModel):
    sku: str
    qty: int


class Order(Document):
    customer: Customer  # 하위 문서로 저장된다
    items: list[Item]  # 하위 문서의 배열
    tags: list[str] = []

    class Settings:
        name = "ex07_orders"


async def customers(query):
    return [o.customer.name for o in await query.to_list()]


async def main():
    async with init(Order):
        await Order.delete_all()
        await Order.insert_many([
            Order(customer=Customer(name="alice", city="Seoul"),
                  items=[Item(sku="A", qty=1), Item(sku="B", qty=5)], tags=["gift", "fast"]),
            Order(customer=Customer(name="bob", city="Busan"), items=[Item(sku="A", qty=3)], tags=["fast"]),
            Order(customer=Customer(name="carol", city="Seoul"), items=[Item(sku="B", qty=2)]),
        ])

        # 1. 중첩 필드 - 속성 접근이 dot 경로("customer.city")로 바뀐다
        query = Order.find(Order.customer.city == "Seoul")
        print("1)", query.get_filter_query(), "→", await customers(query))

        # 2. 리스트 필드 == 값 - 배열에 그 값이 하나라도 있으면 매칭 (Mongo 배열 규칙)
        print("2) tags == fast:", await customers(Order.find(Order.tags == "fast")))

        # 3. All - 배열에 주어진 값이 모두 있어야 매칭
        print("3) All(gift, fast):", await customers(Order.find(All(Order.tags, ["gift", "fast"]))))

        # 4. 하위 문서 배열의 필드 - items 중 하나라도 sku가 A면 매칭
        print("4) items.sku == A:", await customers(Order.find(Order.items.sku == "A")))

        # 5. 함정: 하위 문서 조건을 따로 주면 서로 다른 원소가 나눠서 만족해도 매칭된다
        #    alice는 A(qty 1)와 B(qty 5)가 조건을 하나씩 만족해서 걸린다 → 한 원소에 모두 걸려면 ElemMatch
        print("5) 따로   :", await customers(Order.find(Order.items.sku == "A", Order.items.qty >= 3)))
        print("5) ElemMatch:", await customers(Order.find(ElemMatch(Order.items, {"sku": "A", "qty": {"$gte": 3}}))))


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_beanie --eval "db.ex07_orders.find()"  # customer/items가 하위 문서로 저장됨
# - docker exec -it k8s-client-mongo mongosh example_beanie --eval "db.ex07_orders.find({items: {\$elemMatch: {sku: 'A', qty: {\$gte: 3}}}})"
