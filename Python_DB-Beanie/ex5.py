"""ex5: 문서 삭제 (delete, find().delete, find_one().delete)와 삭제 범위 주의점."""
import asyncio

from beanie import Document

from common import init


class Task(Document):
    title: str
    status: str  # todo / done
    priority: int

    class Settings:
        name = "ex05_tasks"


async def remaining():
    return sorted(t.title for t in await Task.find_all().to_list())  # find_all = 조건 없이 전체


async def main():
    async with init(Task):
        await Task.delete_all()
        await Task.insert_many([
            Task(title=f"t{i}", status=s, priority=p)
            for i, (s, p) in enumerate([("done", 1), ("done", 2), ("done", 3),
                                        ("todo", 1), ("todo", 2), ("todo", 3), ("todo", 1)], 1)
        ])

        # 1. doc.delete - 객체 하나 삭제
        result = await (await Task.find_one(Task.title == "t1")).delete()
        print("1) deleted:", result.deleted_count, "→", await remaining())

        # 2. find().delete - 조건에 맞는 전부 삭제
        result = await Task.find(Task.status == "done").delete()
        print("2) deleted:", result.deleted_count, "→", await remaining())

        # 3. find_one().delete - 첫 문서 하나만. 맞는 게 없으면 None이 아니라 deleted_count=0
        result = await Task.find_one(Task.status == "todo").delete()
        print("3) deleted:", result.deleted_count, "→", await remaining())
        print("3) 없는 문서:", (await Task.find_one(Task.title == "없음").delete()).deleted_count)

        # 4. "priority가 가장 낮은 todo 1건" 삭제 - 대상을 먼저 조회한 뒤 그 문서만 삭제
        #    (sort는 ex6, first_or_none = 결과의 첫 문서, 없으면 None)
        target = await Task.find(Task.status == "todo").sort(+Task.priority).first_or_none()
        await target.delete()
        print("4) 삭제 대상:", target.title, "→", await remaining())

        # 5. 주의: 같은 일을 find().sort().limit(1).delete()로 하면 sort/limit이 무시되어 조건에 맞는 전부가 지워진다
        result = await Task.find(Task.status == "todo").sort(+Task.priority).limit(1).delete()
        print("5) deleted:", result.deleted_count, "→", await remaining())

        # 정리하려면 아래 활성화 (조건 없는 find().delete()도 필터가 {}라 전체 삭제와 같다)
        # await Task.delete_all()


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_beanie --eval "db.ex05_tasks.find()"
