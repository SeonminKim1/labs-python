"""ex13: 문서 참조 (Link, BackLink) - 연결된 문서 가져오기와 N+1 조회."""
import asyncio

from beanie import BackLink, Document, Link, WriteRules
from beanie.exceptions import DocumentWasNotSaved
from pydantic import Field
from pymongo import monitoring

from common import init, raw


class Author(Document):
    name: str
    # BackLink: DB에는 저장되지 않고, Book.author가 이 저자를 가리키는 책들을 거꾸로 찾아온다
    books: list[BackLink["Book"]] = Field(default=[], json_schema_extra={"original_field": "author"})

    class Settings:
        name = "ex13_authors"


class Book(Document):
    title: str
    author: Link[Author]

    class Settings:
        name = "ex13_books"


class QueryCounter(monitoring.CommandListener):
    """DB로 보낸 조회 명령(find/aggregate) 수를 센다."""
    count = 0

    def started(self, event):
        if event.command_name in ("find", "aggregate"):
            QueryCounter.count += 1

    def succeeded(self, event):
        pass

    def failed(self, event):
        pass


monitoring.register(QueryCounter())


async def main():
    async with init(Author, Book):
        await Author.delete_all()
        await Book.delete_all()
        martin, fowler = Author(name="Martin"), Author(name="Fowler")
        await martin.insert()
        await fowler.insert()
        book = Book(title="Clean Code", author=martin)
        await book.insert()
        await Book.insert_many([Book(title="Clean Architecture", author=martin),
                                Book(title="Refactoring", author=fowler)])

        # 1. Link는 DB에 DBRef(컬렉션, _id)로 저장된다. BackLink인 Author.books는 저장되지 않는다
        print("1) book:", await raw(book), "/ author:", await raw(martin))

        # 2. 주의: 기본 조회는 연결된 문서를 가져오지 않는다 → author는 Link 객체라 .name이 없다
        found = await Book.find_one(Book.title == "Clean Code")
        print("2) author 타입:", type(found.author).__name__, "/ hasattr name:", hasattr(found.author, "name"))
        await found.fetch_link(Book.author)  # 필요할 때 하나씩 가져오기
        print("2) fetch_link 후:", found.author.name)

        # 3. 목록에서 책마다 fetch_link를 하면 책 수만큼 조회가 더 나간다 (N+1)
        #    fetch_links=True는 $lookup으로 한 번에 가져온다
        start = QueryCounter.count
        for b in await Book.find_all().to_list():
            await b.fetch_link(Book.author)
        print("3) 책마다 fetch_link:", QueryCounter.count - start, "번")
        start = QueryCounter.count
        books = await Book.find_all(fetch_links=True).to_list()
        print("3) fetch_links=True :", QueryCounter.count - start, "번 →", [(b.title, b.author.name) for b in books])

        # 4. 주의: 연결된 문서의 필드로 조건을 걸면 fetch_links=True가 필요하다 (없으면 에러 없이 빈 결과)
        #    id로 거는 조건은 fetch 없이 된다
        print("4) author.name, fetch 없이:", await Book.find(Book.author.name == "Martin").to_list())
        print("4) author.name, fetch     :", [b.title for b in await Book.find(Book.author.name == "Martin", fetch_links=True).to_list()])
        print("4) author.id              :", [b.title for b in await Book.find(Book.author.id == martin.id).to_list()])

        # 5. BackLink - 저자에서 책 목록으로 거꾸로 가져오기 (fetch_links=True 필요)
        author = await Author.get(martin.id, fetch_links=True)
        print("5) Martin의 책:", [b.title for b in author.books])

        # 6. 주의: 저장되지 않은 문서는 연결해서 저장할 수 없다 → link_rule=WriteRules.WRITE면 함께 저장된다
        try:
            await Book(title="Fluent Python", author=Author(name="Ramalho")).insert()
        except DocumentWasNotSaved as e:
            print("6) DocumentWasNotSaved:", e)
        await Book(title="Fluent Python", author=Author(name="Ramalho")).insert(link_rule=WriteRules.WRITE)
        print("6) WRITE 후 저자 수:", await Author.count())

        # 참고: 저자를 지워도 책의 Link는 남는다. 이때 fetch_links=True로 읽으면 에러 없이 Link 객체 그대로 온다


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_beanie --eval "db.ex13_books.find()"  # author가 DBRef
# - docker exec -it k8s-client-mongo mongosh example_beanie --eval "db.ex13_authors.find()"  # books 필드 없음
