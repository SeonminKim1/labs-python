"""ex2: 문서 삽입 (insert, insert_many, save)과 pydantic 검증 시 주의점."""
import asyncio

from beanie import Document
from pydantic import Field, ValidationError

from common import init, raw


class Product(Document):
    name: str
    price: int = Field(gt=0)

    class Settings:
        name = "ex02_products"


class SafeProduct(Document):
    name: str
    price: int = Field(gt=0)

    class Settings:
        name = "ex02_safe_products"
        validate_on_save = True  # insert/save 직전에 모델을 다시 검증


async def main():
    async with init(Product, SafeProduct):
        await Product.delete_all()

        # 1. insert - 한 건 삽입. 객체에 id가 채워진다
        p = Product(name="keyboard", price=50000)
        await p.insert()
        print("1) insert id:", p.id)

        # 2. 주의: insert_many는 넘긴 객체의 id를 채우지 않는다 → result.inserted_ids 사용
        items = [Product(name="mouse", price=20000), Product(name="monitor", price=300000)]
        result = await Product.insert_many(items)
        print("2) inserted_ids:", result.inserted_ids, "/ 객체 id:", [i.id for i in items])

        # 3. save - id가 없으면 insert, 있으면 모델의 모든 필드를 덮어쓴다 (자세한 동작은 ex4)
        p.price = 45000
        await p.save()
        print("3) save:", await raw(p))

        # 4. 검증: 잘못된 값은 모델 생성 시점에 막힌다
        try:
            Product(name="free", price=0)
        except ValidationError as e:
            print("4) 생성 시 ValidationError:", e.errors()[0]["msg"])

        # 5. 주의: 생성 후 속성 대입은 검증되지 않는다. save()는 DB에 먼저 쓰고 나서
        #    결과를 다시 읽다가 에러를 낸다 → 에러가 났는데도 잘못된 값은 이미 저장돼 있다
        p.price = -1
        try:
            await p.save()
        except ValidationError as e:
            print("5) save() ValidationError:", e.errors()[0]["msg"], "/ 그런데 db:", await raw(p))

        # 6. 대안: Settings.validate_on_save = True → 저장 시점에 막힌다
        sp = SafeProduct(name="desk", price=100000)
        sp.price = -1
        try:
            await sp.insert()
        except ValidationError as e:
            print("6) validate_on_save로 저장 전 차단:", e.errors()[0]["msg"])


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_beanie --eval "db.ex02_products.find()"  # keyboard는 price -1
# - docker exec -it k8s-client-mongo mongosh example_beanie --eval "db.ex02_safe_products.countDocuments()"  # 0
