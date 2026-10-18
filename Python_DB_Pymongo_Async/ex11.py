"""ex11: find_one_and_update/find_one_and_delete로 조회와 수정/삭제를 원자적으로 묶는다."""
import asyncio

from pymongo import ReturnDocument

from common import DB_NAME, get_client

COUNTER_COLLECTION = "ex11_counters"
JOB_COLLECTION = "ex11_jobs"


async def main():
    async with get_client() as client:
        db = client[DB_NAME]
        counters = db[COUNTER_COLLECTION]
        jobs = db[JOB_COLLECTION]
        await counters.delete_many({})
        await jobs.delete_many({})

        # 1. find_one_and_update + $inc + upsert - 원자적 시퀀스 번호 발급기.
        #    조회와 증가가 한 번에 일어나므로 여러 요청이 동시에 불러도 번호가 겹치지 않는다.
        for _ in range(3):
            doc = await counters.find_one_and_update(
                {"_id": "order_seq"},
                {"$inc": {"value": 1}},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )
            print("발급된 번호:", doc["value"])

        # 2. find_one_and_update - 대기 중(pending)인 작업 하나를 processing으로 바꾸면서
        #    동시에 가져온다 (claim). 조건에 status: "pending"이 걸려 있어서 여러 워커가
        #    동시에 호출해도 같은 작업을 중복으로 가져가지 않는다.
        await jobs.insert_many([
            {"name": "send-email", "status": "pending"},
            {"name": "resize-image", "status": "pending"},
        ])
        claimed = await jobs.find_one_and_update(
            {"status": "pending"},
            {"$set": {"status": "processing"}},
            return_document=ReturnDocument.AFTER,
        )
        print("claim한 작업:", claimed)

        # 3. find_one_and_delete - 처리가 끝난 작업을 조회와 동시에 큐에서 제거한다.
        removed = await jobs.find_one_and_delete({"name": "send-email"})
        print("제거된 작업:", removed)
        print("남은 작업:", await jobs.find({}, {"_id": 0}).to_list())


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_pymongo --eval "db.ex11_counters.find()"
# - docker exec -it k8s-client-mongo mongosh example_pymongo --eval "db.ex11_jobs.find()"
