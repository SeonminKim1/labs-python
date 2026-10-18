"""ex9: datetime 필드를 저장하고 범위로 조회한다."""
import asyncio
from datetime import datetime, timedelta, timezone

from common import DB_NAME, get_client

COLLECTION = "ex09_logs"


async def main():
    async with get_client() as client:
        col = client[DB_NAME][COLLECTION]
        await col.delete_many({})

        now = datetime.now(timezone.utc)
        await col.insert_many([
            {"message": f"log-{i}", "created_at": now - timedelta(hours=i)} for i in range(5)
        ])

        # 1. 범위 조회 - 최근 2시간 이내 로그만 ($gte)
        recent = (
            await col.find({"created_at": {"$gte": now - timedelta(hours=2)}}, {"_id": 0})
            .sort("created_at", -1)
            .to_list()
        )
        print("최근 2시간 로그:", recent)

        # 2. 구간 조회 - 2~4시간 전 사이 ($gte + $lt로 범위 지정)
        window = (
            await col.find(
                {
                    "created_at": {
                        "$gte": now - timedelta(hours=4),
                        "$lt": now - timedelta(hours=2),
                    }
                },
                {"_id": 0},
            )
            .sort("created_at", 1)
            .to_list()
        )
        print("2~4시간 전 로그:", window)


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_pymongo --eval "db.ex09_logs.find().sort({created_at:-1})"
