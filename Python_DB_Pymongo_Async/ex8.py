"""ex8: distinct()으로 필드의 고유 값 목록을 조회한다."""
import asyncio

from common import DB_NAME, get_client

COLLECTION = "ex08_events"


async def main():
    async with get_client() as client:
        col = client[DB_NAME][COLLECTION]
        await col.delete_many({})
        await col.insert_many([
            {"type": "click", "page": "home"},
            {"type": "click", "page": "home"},
            {"type": "view", "page": "home"},
            {"type": "view", "page": "pricing"},
            {"type": "signup", "page": "pricing"},
        ])

        # 1. distinct - 전체 문서에서 type 필드의 고유 값 목록
        #    (필터 UI의 드롭다운 옵션 목록을 뽑을 때 자주 쓰는 패턴)
        print("전체 type 종류:", await col.distinct("type"))

        # 2. distinct + 필터 - page가 pricing인 문서로 한정해서 type 고유 값 조회
        print("pricing 페이지의 type 종류:", await col.distinct("type", {"page": "pricing"}))


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_pymongo --eval "db.ex08_events.distinct('type')"
