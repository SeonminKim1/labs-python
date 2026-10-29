"""ex1: Document 모델을 정의하고 init_beanie로 MongoDB 컬렉션과 연결한다."""
import asyncio

from beanie import Document

from common import init


class User(Document):
    # Document = pydantic BaseModel + MongoDB 컬렉션 매핑. id(_id) 필드는 자동으로 붙는다.
    name: str
    age: int

    class Settings:
        name = "ex01_users"  # 컬렉션 이름 (생략하면 클래스 이름 "User"가 된다)


async def main():
    async with init(User) as db:
        # 1. init_beanie가 끝나면 모델이 컬렉션과 연결된다 - 실제 컬렉션 이름 확인
        print("collection:", User.get_collection_name())

        # 2. 모델 하나 저장 - mongosh에서 db.ex01_users.find()로 확인 (재실행마다 한 건씩 늘어남)
        user = User(name="alice", age=30)
        await user.insert()
        print("inserted id:", user.id, type(user.id).__name__)

        # 3. 저장된 문서가 MongoDB에서 어떤 모양인지 확인 (id → _id로 저장됨)
        raw = await db["ex01_users"].find_one({"_id": user.id})
        print("raw document:", raw)

        # 4. 모델 ↔ dict 변환 (pydantic 그대로)
        print("model_dump:", user.model_dump())

        # 정리하려면 아래 활성화
        # await User.delete_all()


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_beanie --eval "db.ex01_users.find()"
