"""ex12: 인덱스 (Indexed, Settings.indexes), unique와 DuplicateKeyError, 동시 upsert 중복 막기."""
import asyncio

from beanie import Document, Indexed
from beanie.operators import Inc
from pymongo import ASCENDING, DESCENDING, IndexModel
from pymongo.errors import DuplicateKeyError

from common import init


class User(Document):
    email: Indexed(str, unique=True)  # 단일 필드 인덱스 (unique)
    name: str
    age: int

    class Settings:
        name = "ex12_users"
        indexes = [IndexModel([("age", DESCENDING), ("name", ASCENDING)], name="age_name")]  # 복합 인덱스


class Stock(Document):
    sku: str
    qty: int

    class Settings:
        name = "ex12_stocks"


class UniqueStock(Document):
    sku: Indexed(str, unique=True)
    qty: int

    class Settings:
        name = "ex12_unique_stocks"


async def plan(filter_):
    """explain()의 실행 계획 단계 (IXSCAN: 인덱스 사용, COLLSCAN: 전체 스캔)."""
    stage = (await User.get_pymongo_collection().find(filter_).explain())["queryPlanner"]["winningPlan"]
    stages = []
    while stage:
        stages.append(stage["stage"])
        stage = stage.get("inputStage")
    return " ← ".join(stages)


async def concurrent_upsert(model):
    """같은 sku로 upsert 20개를 동시에 실행하고 (문서 수, 에러 수)를 반환."""
    await model.delete_all()
    # 커넥션이 열리기 전의 첫 동시 요청은 사실상 차례로 처리되어 경합이 재현되지 않는다 → 먼저 커넥션을 열어 둔다
    await asyncio.gather(*[model.find_all().count() for _ in range(20)])
    results = await asyncio.gather(*[
        model.find_one(model.sku == "D").upsert(Inc({model.qty: 1}), on_insert=model(sku="D", qty=1))
        for _ in range(20)
    ], return_exceptions=True)
    errors = [r for r in results if isinstance(r, DuplicateKeyError)]
    return await model.find(model.sku == "D").count(), len(errors)


async def main():
    async with init(User, Stock, UniqueStock):
        await User.delete_all()

        # 1. init_beanie가 모델에 선언된 인덱스를 만든다
        indexes = await (await User.get_pymongo_collection().list_indexes()).to_list()
        print("1) indexes:", [(i["name"], dict(i["key"]), i.get("unique", False)) for i in indexes])

        # 2. 인덱스가 있는 필드는 IXSCAN 계열(서버 버전에 따라 EXPRESS_IXSCAN 등), 없는 필드는 COLLSCAN
        await User(email="a@x.com", name="alice", age=30).insert()
        print("2) email:", await plan({"email": "a@x.com"}), "/ name:", await plan({"name": "alice"}))

        # 3. unique 위반 → DuplicateKeyError
        try:
            await User(email="a@x.com", name="alice2", age=20).insert()
        except DuplicateKeyError as e:
            print("3) DuplicateKeyError:", e.details["keyValue"])

        # 4. 동시 upsert (ex8) - unique가 없으면 중복 문서가 생긴다 (개수는 실행마다 다름).
        #    unique가 있으면 1건만 남고 나머지는 DuplicateKeyError → 그 호출의 Inc는 반영 안 되므로 재시도 필요
        print("4) unique 없음 (문서 수, 에러 수):", await concurrent_upsert(Stock))
        print("4) unique 있음 (문서 수, 에러 수):", await concurrent_upsert(UniqueStock))

        # 참고: 모델에서 인덱스를 바꾸거나 지워도 init_beanie는 옛 인덱스를 지우지 않는다
        #       → init_beanie(..., allow_index_dropping=True)로 모델에 없는 인덱스를 정리한다


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_beanie --eval "db.ex12_users.getIndexes()"
# - docker exec -it k8s-client-mongo mongosh example_beanie --eval "db.ex12_users.find({email: 'a@x.com'}).explain().queryPlanner.winningPlan"
