"""ex9: 상태 관리 (use_state_management, save_changes) - 바뀐 필드만 저장."""
import asyncio

from beanie import Document

from common import init, raw


class Account(Document):
    user: str
    balance: int
    tags: list[str] = []

    class Settings:
        name = "ex09_accounts"
        use_state_management = True  # 꺼져 있으면 save_changes()가 StateManagementIsTurnedOff 에러


async def main():
    async with init(Account):
        await Account.delete_all()
        acc = Account(user="alice", balance=100)
        await acc.insert()

        # 1. 변경 추적 - DB에서 읽거나 저장한 시점의 값과 비교한다. 리스트를 직접 고친 것(append)도 잡힌다
        stale = await Account.get(acc.id)  # 다른 요청이 읽어둔 객체라고 가정
        stale.user = "alice2"
        stale.tags.append("vip")
        print("1) is_changed:", stale.is_changed, "/ changes:", stale.get_changes())

        # 2. save_changes - 바뀐 필드만 $set → 그 사이 바뀐 다른 필드(balance)는 보존된다 (ex4 lost update 해결)
        await acc.inc({Account.balance: 1000})
        await stale.save_changes()
        print("2) save_changes 후:", await raw(acc))

        # 3. 한계: 같은 필드를 동시에 바꾸면 여전히 나중 저장이 이긴다 (+1이 사라지고 0) → ex11 revision
        stale = await Account.get(acc.id)
        await acc.inc({Account.balance: 1})
        stale.balance = 0
        await stale.save_changes()
        print("3) 같은 필드:", await raw(acc))

        # 4. 주의: 상태 관리를 켜도 save()는 여전히 모든 필드를 덮어쓴다 (+500이 사라지고 0)
        #    → 바뀐 필드만 저장하려면 save_changes()
        stale = await Account.get(acc.id)
        await acc.inc({Account.balance: 500})
        stale.user = "alice3"
        await stale.save()
        print("4) save():", await raw(acc))


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_beanie --eval "db.ex09_accounts.find()"
