"""ex1: AsyncMongoClient로 MongoDB 서버에 연결하고 기본 정보를 확인한다."""
import asyncio

from common import DB_NAME, get_client


async def main():
    async with get_client() as client:
        # 1. 서버가 살아있는지 ping - 결과가 {'ok': 1.0}이면 정상
        print("ping:", await client.admin.command("ping"))

        # 2. 서버 버전 확인 - mongosh의 `db.version()` 결과와 비교 가능
        print("version:", (await client.server_info())["version"])

        # 3. 현재 보이는 데이터베이스 목록 확인
        print("databases:", await client.list_database_names())

        db = client[DB_NAME]
        print(f"이 예제 시리즈가 사용할 DB: {db.name}")


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh --eval "db.version()"
# - docker exec -it k8s-client-mongo mongosh --eval "db.adminCommand('listDatabases')"
