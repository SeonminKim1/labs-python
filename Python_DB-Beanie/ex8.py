"""ex8: upsert - 없으면 생성, 있으면 수정 (find_one().upsert, update(upsert=True))."""
import asyncio

from beanie import Document
from beanie.operators import Inc, Set

from common import init


class Stock(Document):
    sku: str
    qty: int

    class Settings:
        name = "ex08_stocks"


async def stocks():
    return [(s.sku, s.qty) for s in await Stock.find_all().to_list()]


async def main():
    async with init(Stock):
        await Stock.delete_all()

        # 1. upsert - 없으면 on_insert 문서를 그대로 삽입 (Inc는 적용되지 않음), 있으면 Inc 적용
        #    반환 타입도 다르다: 삽입이면 Document, 수정이면 UpdateResult
        for _ in range(2):
            result = await Stock.find_one(Stock.sku == "A").upsert(Inc({Stock.qty: 5}), on_insert=Stock(sku="A", qty=1))
            print("1)", type(result).__name__, "→", await stocks())

        # 2. 주의: on_insert는 조건과 상관없이 그대로 들어간다
        #    조건(sku == "B")과 다른 값(sku="b")을 넣으면 다음 호출도 못 찾아서 또 삽입한다
        for _ in range(2):
            await Stock.find_one(Stock.sku == "B").upsert(Inc({Stock.qty: 1}), on_insert=Stock(sku="b", qty=1))
        print("2)", await stocks())

        # 3. update(..., upsert=True) - Mongo 기본 upsert. 조건 필드 + 연산 결과로 새 문서를 만든다
        await Stock.find_one(Stock.sku == "C").update(Set({Stock.qty: 3}), upsert=True)
        print("3)", await stocks())

        # 참고: upsert()는 동시에 호출되면 둘 다 "없음"을 보고 각각 삽입해 중복이 생길 수 있다
        #       → 조건 필드에 unique 인덱스를 걸어 DB가 막게 한다 (ex12에서 시연)


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_beanie --eval "db.ex08_stocks.find()"
