"""ex6: 정렬, 페이지네이션(skip/limit vs keyset), count, projection 모델."""
import asyncio

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field

from common import init


class Product(Document):
    name: str
    category: str
    price: int
    description: str = "긴 설명 ..."

    class Settings:
        name = "ex06_products"


class ProductSummary(BaseModel):
    # projection 모델: 이 모델의 필드만 DB에서 읽는다. id도 받으려면 alias로 _id를 명시
    id: PydanticObjectId = Field(alias="_id")
    name: str


async def main():
    async with init(Product):
        await Product.delete_all()
        await Product.insert_many([
            Product(name=f"p{i}", category="book" if i % 2 else "pen", price=(i % 4) * 1000)
            for i in range(10)
        ])

        # 1. sort - 필드 앞에 -(내림차순)/+(오름차순), 여러 키는 순서대로 적용. 문자열 "-price"도 가능
        items = await Product.find().sort(-Product.price, +Product.name).to_list()
        print("1) sort:", [(p.name, p.price) for p in items])

        # 2. skip/limit 페이지네이션 - book 2페이지 (페이지 크기 3)
        query = Product.find(Product.category == "book").sort(+Product.name)
        print("2) 2페이지:", [p.name for p in await query.skip(3).limit(3).to_list()])

        # 3. 함정: skip()/limit()은 새 쿼리가 아니라 query 객체 자체를 바꾼다
        #    → 2의 query로 count()하면 전체가 아니라 2페이지 범위만 센다. 전체 개수는 새 쿼리로
        print("3) 2의 query:", await query.count(), "/ 새 쿼리:", await Product.find(Product.category == "book").count())

        # 4. keyset 페이지네이션 - skip은 건너뛸 문서를 매번 다 읽어 뒤 페이지일수록 느리다.
        #    마지막으로 본 _id 다음부터 읽으면 페이지 위치와 상관없이 인덱스로 바로 찾는다
        last_id = None
        while batch := await Product.find(Product.id > last_id if last_id else {}).sort(+Product.id).limit(4).to_list():
            print("4) page:", [p.name for p in batch])
            last_id = batch[-1].id

        # 5. projection - 필요한 필드만 읽기 (큰 description 제외). 결과는 Document가 아니라 save() 등이 없다
        print("5) project:", await Product.find(Product.price >= 3000).project(ProductSummary).to_list())


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_beanie --eval "db.ex06_products.find().sort({price: -1, name: 1})"
# - docker exec -it k8s-client-mongo mongosh example_beanie --eval "db.ex06_products.find({price: {\$gte: 3000}}, {name: 1})"
