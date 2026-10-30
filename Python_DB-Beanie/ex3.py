"""ex3: 문서 조회 (get, find_one, find)와 Beanie 쿼리 문법."""
import asyncio

from beanie import Document, PydanticObjectId
from beanie.operators import GTE, In, Or

from common import init


class Book(Document):
    title: str
    author: str
    year: int
    price: int

    class Settings:
        name = "ex03_books"


async def main():
    async with init(Book):
        await Book.delete_all()
        result = await Book.insert_many([
            Book(title="Clean Code", author="Martin", year=2008, price=30000),
            Book(title="Clean Architecture", author="Martin", year=2017, price=32000),
            Book(title="Refactoring", author="Fowler", year=2018, price=35000),
            Book(title="Fluent Python", author="Ramalho", year=2022, price=45000),
        ])

        # 1. get - _id로 한 건 조회. 없는 id면 예외가 아니라 None
        print("1) get:", (await Book.get(result.inserted_ids[0])).title, "/", await Book.get(PydanticObjectId()))

        # 2. find_one - 조건에 맞는 첫 문서
        print("2) find_one:", (await Book.find_one(Book.author == "Fowler")).title)

        # 3. find - 필드 비교식이 Mongo 필터로 바뀐다. 조건을 여러 개 주면 AND
        query = Book.find(Book.author == "Martin", Book.year >= 2010)
        print("3) 필터:", query.get_filter_query(), "→", [b.title for b in await query.to_list()])

        # 4. 연산자 함수 (beanie.operators) - In, GTE 등
        books = await Book.find(In(Book.author, ["Fowler", "Ramalho"]), GTE(Book.price, 40000)).to_list()
        print("4) operators:", [b.title for b in books])

        # 5. dict 필터 (pymongo 문법)도 된다 - 단, 필드명 오타를 못 잡으므로 식 문법 권장
        print("5) dict:", [b.title for b in await Book.find({"year": {"$lt": 2015}}).to_list()])

        # 6. async for - 결과가 많을 때 to_list()로 전부 올리지 않고 한 건씩 처리
        async for b in Book.find(Book.price < 33000):
            print("6) async for:", b.title)

        # 7. 주의: 파이썬 and/or는 에러 없이 한쪽 식만 남긴다 (`or`는 앞, `and`는 뒤) → Or / And 사용
        for label, q in [("or  ", Book.find(Book.year < 2010 or Book.author == "Ramalho")),
                         ("Or()", Book.find(Or(Book.year < 2010, Book.author == "Ramalho")))]:
            print(f"7) {label}:", q.get_filter_query(), "→", [b.title for b in await q.to_list()])


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_beanie --eval "db.ex03_books.find({author: 'Martin', year: {\$gte: 2010}})"
