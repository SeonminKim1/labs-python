"""ex7: 배열/중첩 문서를 dot notation과 $in/$all/$elemMatch로 조회한다."""
import asyncio

from common import DB_NAME, get_client

COLLECTION = "ex07_posts"


async def main():
    async with get_client() as client:
        col = client[DB_NAME][COLLECTION]
        await col.delete_many({})
        await col.insert_many([
            {
                "title": "pymongo 소개",
                "tags": ["mongodb", "python"],
                "author": {"name": "alice", "level": "senior"},
                "comments": [{"user": "bob", "score": 5}, {"user": "carol", "score": 2}],
            },
            {
                "title": "비동기 입문",
                "tags": ["python", "asyncio"],
                "author": {"name": "bob", "level": "junior"},
                "comments": [{"user": "alice", "score": 4}],
            },
        ])

        # 1. dot notation - 중첩 문서(author.level) 필드로 조회
        print(
            "author.level=senior:",
            await col.find({"author.level": "senior"}, {"_id": 0, "title": 1}).to_list(),
        )

        # 2. $in - 배열 필드(tags) 중 하나라도 일치하면 매치
        print(
            "tags에 'asyncio' 포함:",
            await col.find({"tags": {"$in": ["asyncio"]}}, {"_id": 0, "title": 1}).to_list(),
        )

        # 3. $all - 배열이 주어진 값을 모두 포함해야 매치
        print(
            "tags가 python과 mongodb를 모두 포함:",
            await col.find(
                {"tags": {"$all": ["python", "mongodb"]}}, {"_id": 0, "title": 1}
            ).to_list(),
        )

        # 4. $elemMatch - 배열 안의 "같은 원소"에서 여러 조건을 동시에 만족해야 매치
        print(
            "score가 4 이상인 댓글이 있는 글:",
            await col.find(
                {"comments": {"$elemMatch": {"score": {"$gte": 4}}}},
                {"_id": 0, "title": 1},
            ).to_list(),
        )


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_pymongo --eval "db.ex07_posts.find({'author.level':'senior'})"
