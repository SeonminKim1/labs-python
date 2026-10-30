"""ex11: 낙관적 락 (use_revision) - 동시 수정 충돌을 감지한다."""
import asyncio

from beanie import Document
from beanie.exceptions import RevisionIdWasChanged
from beanie.operators import Inc

from common import init, raw


class Account(Document):
    user: str
    balance: int

    class Settings:
        name = "ex11_accounts"
        use_revision = True  # 저장할 때마다 바뀌는 revision_id를 문서에 함께 저장


async def main():
    async with init(Account):
        await Account.delete_all()
        acc = Account(user="alice", balance=100)
        await acc.insert()
        print("1) revision_id:", acc.revision_id)

        # 2. 충돌 감지 - 읽은 뒤 다른 곳에서 먼저 저장했으면 revision_id가 달라 저장이 거부된다
        #    (save/replace/save_changes/set 모두 해당. ex4, ex9의 lost update를 막는다)
        mine, other = await Account.get(acc.id), await Account.get(acc.id)
        other.balance += 1000
        await other.save()
        mine.balance = 0
        try:
            await mine.save()
        except RevisionIdWasChanged:
            print("2) RevisionIdWasChanged / db:", (await raw(acc))["balance"])

        # 3. 충돌 처리 - 최신 문서를 다시 읽어 변경을 다시 적용한 뒤 저장 (재시도)
        #    (ignore_revision=True로 강제 저장도 되지만 충돌을 무시하는 것이다)
        mine = await Account.get(acc.id)
        mine.user = "alice2"
        await mine.save()
        print("3) 재시도 후:", {k: v for k, v in (await raw(acc)).items() if k != "revision_id"})

        # 4. 주의: find().update()는 revision을 확인하지도, 바꾸지도 않는다
        #    → 그 뒤에 오래된 객체로 save()해도 충돌로 잡히지 않고 쿼리 수정분(+5)을 덮어쓴다
        stale = await Account.get(acc.id)
        await Account.find(Account.id == acc.id).update(Inc({Account.balance: 5}))
        print("4) 쿼리 수정 후:", (await raw(acc))["balance"])
        stale.user = "alice3"
        await stale.save()
        print("4) stale.save() 후:", (await raw(acc))["balance"])


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_beanie --eval "db.ex11_accounts.find()"  # revision_id 필드 확인
