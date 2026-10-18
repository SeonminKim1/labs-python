"""ex13: create_index/list_indexes로 인덱스를 만들고 조회 계획 변화를 확인한다."""
import asyncio

from common import DB_NAME, get_client

COLLECTION = "ex13_logs"


async def main():
    async with get_client() as client:
        col = client[DB_NAME][COLLECTION]
        await col.delete_many({})
        await col.drop_indexes()  # 이전 실행에서 만든 인덱스 제거하고 깨끗하게 시작
        await col.insert_many(
            [{"level": "error" if i % 5 == 0 else "info", "seq": i} for i in range(1000)]
        )

        # 1. 인덱스 생성 전 - level로 조회하면 전체 스캔(COLLSCAN)이 되는지 확인
        plan = await col.find({"level": "error"}).explain()
        print("인덱스 생성 전 stage:", plan["queryPlanner"]["winningPlan"]["stage"])

        # 2. 인덱스 생성 - level 필드에 단일 필드 인덱스
        index_name = await col.create_index("level")
        print("생성된 인덱스:", index_name)

        # 3. 인덱스 생성 후 - 문서 전체를 돌려주므로 최상위는 FETCH지만, 그 아래
        #    inputStage가 IXSCAN으로 바뀌어 인덱스를 탄다는 걸 확인할 수 있음
        plan = await col.find({"level": "error"}).explain()
        winning_plan = plan["queryPlanner"]["winningPlan"]
        print("인덱스 생성 후 stage:", winning_plan["stage"])
        print("인덱스 생성 후 inputStage:", winning_plan["inputStage"]["stage"])

        # 4. 현재 컬렉션에 있는 인덱스 목록 확인
        indexes = await (await col.list_indexes()).to_list()
        print("인덱스 목록:", [idx["name"] for idx in indexes])


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_pymongo --eval "db.ex13_logs.getIndexes()"
