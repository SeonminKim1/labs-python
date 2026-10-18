"""ex5: delete_one/delete_many으로 문서를 삭제한다."""
import asyncio

from common import DB_NAME, get_client

COLLECTION = "ex05_sessions"


async def main():
    async with get_client() as client:
        col = client[DB_NAME][COLLECTION]
        await col.delete_many({})
        await col.insert_many([
            {"session_id": "s1", "expired": True},
            {"session_id": "s2", "expired": True},
            {"session_id": "s3", "expired": False},
        ])
        print("삭제 전 문서 수:", await col.count_documents({}))

        # 1. delete_one - 조건에 맞는 문서 하나만 삭제
        result = await col.delete_one({"session_id": "s1"})
        print("deleted_count:", result.deleted_count)

        # 2. delete_many - expired가 True인 나머지 문서 삭제
        result = await col.delete_many({"expired": True})
        print("deleted_count:", result.deleted_count)

        print("삭제 후 남은 문서:", await col.find({}, {"_id": 0}).to_list())

        # 컬렉션 자체를 지우고 싶으면 (되돌리기 어려움) 확인 후 아래 주석 해제
        # await col.drop()


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_pymongo --eval "db.ex05_sessions.find()"
