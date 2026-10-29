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
        print("1) get:", (await Book.get(result.inserted_ids[0])).title)
        print("1) get(없는 id):", await Book.get(PydanticObjectId()))

        # 2. find_one - 조건에 맞는 첫 문서. 필드 비교식이 그대로 Mongo 필터가 된다
        book = await Book.find_one(Book.author == "Fowler")
        print("2) find_one:", book.title)

        # 3. find + to_list - 여러 건. 인자를 여러 개 주면 AND
        books = await Book.find(Book.author == "Martin", Book.year >= 2010).to_list()
        print("3) find AND:", [b.title for b in books])

        # 4. 연산자 함수 (beanie.operators) - In, GTE 등
        books = await Book.find(In(Book.author, ["Fowler", "Ramalho"]), GTE(Book.price, 40000)).to_list()
        print("4) operators:", [b.title for b in books])

        # 5. dict 필터도 그대로 쓸 수 있다 (pymongo 문법) - 필드명 오타를 못 잡으므로 식 문법 권장
        books = await Book.find({"year": {"$lt": 2015}}).to_list()
        print("5) dict filter:", [b.title for b in books])

        # 6. 비동기 반복 - 결과가 많을 때 to_list() 대신 한 건씩 처리
        print("6) async for:", end=" ")
        async for b in Book.find(Book.price < 33000):
            print(b.title, end=" / ")
        print()

        # 7. 실제로 만들어지는 Mongo 필터 확인
        print("7) query:", Book.find(Book.author == "Martin", Book.year >= 2010).get_filter_query())

        # 8. 함정: 파이썬 and/or는 쓰면 안 된다 - 에러 없이 한쪽 식만 남는다 → Or / And 사용
        #    (`or`는 앞의 식만, `and`는 뒤의 식만 남는다. 7의 get_filter_query()로 확인)
        wrong = Book.find(Book.year < 2010 or Book.author == "Ramalho")
        print("8) or 사용  :", wrong.get_filter_query(), [b.title for b in await wrong.to_list()])
        right = Book.find(Or(Book.year < 2010, Book.author == "Ramalho"))
        print("8) Or() 사용:", right.get_filter_query(), [b.title for b in await right.to_list()])


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_beanie --eval "db.ex03_books.find({author: 'Martin', year: {\$gte: 2010}})"
