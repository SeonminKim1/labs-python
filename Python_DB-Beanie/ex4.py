"""ex4: 문서 수정 (set, inc, find().update)과 save()/replace()의 덮어쓰기 동작."""
import asyncio

from beanie import Document
from beanie.operators import Inc, Push

from common import init, raw


class Account(Document):
    user: str
    balance: int
    tags: list[str] = []

    class Settings:
        name = "ex04_accounts"


async def main():
    async with init(Account):
        await Account.delete_all()
        alice, bob = Account(user="alice", balance=100), Account(user="bob", balance=50)
        await alice.insert()
        await bob.insert()

        # 1. set / inc - 지정한 필드만 수정. 메모리의 객체도 같이 바뀐다
        await alice.set({Account.balance: 150})
        await alice.inc({Account.balance: 10})
        print("1) local:", alice.balance, "/ db:", await raw(alice))

        # 2. find().update - 조건에 맞는 문서 전부 수정 (Push 같은 배열 연산자도 beanie.operators에 있다)
        #    주의: 이미 읽어둔 객체는 갱신되지 않는다 → 필요하면 다시 조회
        result = await Account.find(Account.balance > 0).update(Inc({Account.balance: 1}), Push({Account.tags: "event"}))
        print("2) modified:", result.modified_count, "/ alice local:", alice.balance, "/ db:", await raw(alice))

        # 3. 주의: save()는 바꾼 필드만이 아니라 모델의 모든 필드를 덮어쓴다
        #    → 오래된 객체로 save()하면 그 사이 바뀐 값이 사라진다 (lost update)
        stale = await Account.get(bob.id)  # 다른 요청이 읽어둔 객체라고 가정
        await bob.inc({Account.balance: 1000})  # 그 사이 입금
        print("3) 입금 직후:", await raw(bob))
        stale.user = "bobby"
        await stale.save()
        print("3) stale.save() 후:", await raw(bob))
        # 대안: 바꾼 필드만 set()으로 저장 (또는 ex9 상태 관리, ex11 revision)

        # 4. save() vs replace() - save()는 모델 필드만 $set → 모델에 없는 필드는 남는다.
        #    replace()는 문서 전체 교체 → 모델에 없는 필드가 지워진다
        await Account.get_pymongo_collection().update_one({"_id": alice.id}, {"$set": {"legacy": "old"}})
        a = await Account.get(alice.id)
        await a.save()
        print("4) save()   :", await raw(a))
        await a.replace()
        print("4) replace():", await raw(a))


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_beanie --eval "db.ex04_accounts.find()"
