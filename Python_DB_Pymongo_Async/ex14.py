"""ex14: 고유 인덱스(unique index)와 중복 키 에러 처리."""
import asyncio

from pymongo.errors import DuplicateKeyError

from common import DB_NAME, get_client

COLLECTION = "ex14_members"


async def main():
    async with get_client() as client:
        col = client[DB_NAME][COLLECTION]
        await col.delete_many({})
        await col.drop_indexes()

        # 1. unique 인덱스 생성 - email 중복 가입을 DB 레벨에서 막는다
        await col.create_index("email", unique=True)

        # 2. 첫 가입은 정상적으로 들어간다
        await col.insert_one({"email": "alice@example.com", "name": "Alice"})
        print("첫 가입 성공")

        # 3. 같은 email로 다시 가입을 시도하면 DuplicateKeyError가 발생한다
        #    - 애플리케이션에서는 이를 잡아서 사용자용 메시지로 바꿔 돌려주는 게 일반적이다
        try:
            await col.insert_one({"email": "alice@example.com", "name": "Alice2"})
        except DuplicateKeyError as e:
            print(f"중복 가입 차단됨 (code={e.code}): 이미 가입된 이메일입니다")

        print("최종 회원:", await col.find({}, {"_id": 0}).to_list())


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_pymongo --eval "db.ex14_members.getIndexes()"
