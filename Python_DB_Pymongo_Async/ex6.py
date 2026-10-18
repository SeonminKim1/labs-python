"""ex6: sort로 정렬하고 페이지 단위로 나눠 조회한다 (skip/limit vs keyset)."""
import asyncio

from common import DB_NAME, get_client

COLLECTION = "ex06_articles"
PAGE_SIZE = 3


async def main():
    async with get_client() as client:
        col = client[DB_NAME][COLLECTION]
        await col.delete_many({})
        await col.insert_many(
            [{"title": f"article-{i:02d}", "views": i * 7 % 23} for i in range(1, 11)]
        )

        # 1. sort - views 내림차순으로 전체 정렬
        cursor = col.find({}, {"_id": 0}).sort("views", -1)
        print("views 내림차순:", await cursor.to_list())

        # 2. skip + limit - 구현이 가장 쉬운 페이지네이션. title 기준 1페이지/2페이지.
        #    주의: skip(n)은 앞의 n개 문서를 실제로 읽고 버리는 방식이라 n(=페이지 번호)이
        #    커질수록 느려진다 - 관리자 화면처럼 페이지 수가 적을 때만 적합하다.
        page1 = (
            await col.find({}, {"_id": 0}).sort("title", 1).skip(0).limit(PAGE_SIZE).to_list()
        )
        page2 = (
            await col.find({}, {"_id": 0})
            .sort("title", 1)
            .skip(PAGE_SIZE)
            .limit(PAGE_SIZE)
            .to_list()
        )
        print("skip/limit 1페이지:", page1)
        print("skip/limit 2페이지:", page2)

        # 3. keyset(range) 페이지네이션 - 대규모 컬렉션/무한 스크롤에서 실제로 쓰는 방식.
        #    skip 없이, 직전 페이지의 마지막 정렬 키(title)보다 큰 문서만 조회한다.
        #    offset이 몇이든 항상 인덱스로 바로 찾아가므로 뒷페이지에서도 느려지지 않는다.
        first_page = await col.find({}, {"_id": 0}).sort("title", 1).limit(PAGE_SIZE).to_list()
        last_title = first_page[-1]["title"]
        next_page = (
            await col.find({"title": {"$gt": last_title}}, {"_id": 0})
            .sort("title", 1)
            .limit(PAGE_SIZE)
            .to_list()
        )
        print("keyset 1페이지:", first_page)
        print(f"keyset 2페이지 (title > {last_title!r}):", next_page)

        # 4. 전체 페이지 수 계산에 필요한 총 문서 수 (skip/limit 방식에서만 필요)
        total = await col.count_documents({})
        print("총 문서 수:", total, "/ 페이지 크기:", PAGE_SIZE)


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_pymongo --eval "db.ex06_articles.find().sort({title:1}).skip(3).limit(3)"
# - docker exec -it k8s-client-mongo mongosh example_pymongo --eval "db.ex06_articles.find({title:{\$gt:'article-03'}}).sort({title:1}).limit(3)"
