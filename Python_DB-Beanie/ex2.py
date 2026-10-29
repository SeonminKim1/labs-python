"""ex2: 문서 삽입 (insert, insert_many, save)과 pydantic 검증 실패."""
import asyncio

from beanie import Document
from pydantic import Field, ValidationError

from common import init


class Product(Document):
    name: str
    price: int = Field(gt=0)  # 0보다 커야 함
    tags: list[str] = []

    class Settings:
        name = "ex02_products"


class SafeProduct(Document):
    name: str
    price: int = Field(gt=0)

    class Settings:
        name = "ex02_safe_products"
        validate_on_save = True  # insert/save 직전에 모델을 다시 검증


async def main():
    async with init(Product, SafeProduct) as db:
        await Product.delete_all()  # 반복 실행해도 결과가 같도록 초기화

        # 1. insert - 한 건 삽입. 삽입 후 객체에 id가 채워진다
        p = Product(name="keyboard", price=50000)
        await p.insert()
        print("1) insert id:", p.id)

        # 2. insert_many - 여러 건 한 번에 (InsertManyResult 반환)
        #    함정: insert()와 달리 넘긴 객체의 id는 채워지지 않는다 → result.inserted_ids를 사용
        items = [
            Product(name="mouse", price=20000, tags=["usb"]),
            Product(name="monitor", price=300000),
        ]
        result = await Product.insert_many(items)
        print("2) inserted_ids:", result.inserted_ids)
        print("2) 객체의 id:", [item.id for item in items])

        # 3. save - id가 없으면 insert, 있으면 문서 전체를 교체(replace)
        p2 = Product(name="cable", price=5000)
        await p2.save()
        p2.price = 7000
        await p2.save()
        print("3) save 후 price:", (await Product.get(p2.id)).price)

        # 4. 검증: 잘못된 값은 DB에 가기 전에 모델 생성 시점에 막힌다
        try:
            Product(name="free", price=0)
        except ValidationError as e:
            print("4) ValidationError:", e.errors()[0]["msg"])

        # 5. 함정: 생성 후 속성 대입은 검증되지 않는다 → 잘못된 값이 그대로 저장되고,
        #    나중에 그 문서를 읽을 때 ValidationError가 터진다 (조회 쪽에서 발견됨)
        p3 = Product(name="desk", price=100000)
        p3.price = -1
        await p3.insert()
        print("5) 저장된 raw:", await db["ex02_products"].find_one({"_id": p3.id}))
        try:
            await Product.get(p3.id)
        except ValidationError as e:
            print("5) 읽을 때 ValidationError:", e.errors()[0]["msg"])
        await p3.delete()  # 깨진 문서는 지워둔다 (count 등 이후 조회를 위해)

        # 6. 대안: Settings.validate_on_save = True → 저장 시점에 막힌다
        await SafeProduct.delete_all()
        sp = SafeProduct(name="desk", price=100000)
        sp.price = -1
        try:
            await sp.insert()
        except ValidationError as e:
            print("6) validate_on_save로 저장 전 차단:", e.errors()[0]["msg"])

        # 7. 최종 개수 - keyboard, mouse, monitor, cable 4건 (desk는 5에서 삭제)
        print("7) count:", await Product.count())


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_beanie --eval "db.ex02_products.find()"
# - docker exec -it k8s-client-mongo mongosh example_beanie --eval "db.ex02_safe_products.countDocuments()"  # 0이어야 함
