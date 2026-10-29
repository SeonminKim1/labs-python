"""ex1: Document 모델을 정의하고 init_beanie로 MongoDB 컬렉션과 연결한다."""
import asyncio

from beanie import Document

from common import init


class User(Document):
    # Document = pydantic BaseModel + 컬렉션 매핑. id(_id) 필드는 자동으로 붙는다
    name: str
    age: int

    class Settings:
        name = "ex01_users"  # 컬렉션 이름 (생략하면 클래스 이름 "User")


async def main():
    async with init(User):
        # 1. 저장 - 저장 후 객체에 id가 채워진다 (재실행마다 한 건씩 늘어남)
        user = User(name="alice", age=30)
        await user.insert()
        print("1) id:", user.id, type(user.id).__name__)

        # 2. DB에 실제 저장된 모양 - 모델의 id가 _id로 저장된다
        print("2) raw:", await User.get_pymongo_collection().find_one({"_id": user.id}))

        # 정리하려면 아래 활성화
        # await User.delete_all()


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_beanie --eval "db.ex01_users.find()"
