"""ex4: update_one/update_many과 주요 업데이트 연산자 모음."""
import asyncio

from common import DB_NAME, get_client

COLLECTION = "ex04_accounts"


async def main():
    async with get_client() as client:
        col = client[DB_NAME][COLLECTION]
        await col.delete_many({})
        await col.insert_many([
            {"user": "alice", "balance": 100},
            {"user": "bob", "balance": 50},
        ])

        # 1. $set - alice의 balance를 교체
        result = await col.update_one({"user": "alice"}, {"$set": {"balance": 150}})
        print("1) $set matched/modified:", result.matched_count, result.modified_count)

        # 2. $inc - 전체 계정에 보너스 10 추가
        result = await col.update_many({}, {"$inc": {"balance": 10}})
        print("2) $inc matched/modified:", result.matched_count, result.modified_count)

        # 3. upsert - 조건에 맞는 문서가 없으면 새로 생성, 있으면 수정
        result = await col.update_one(
            {"user": "carol"}, {"$set": {"balance": 0}}, upsert=True
        )
        print("3) upsert upserted_id:", result.upserted_id)

        # 4. $mul - bob 계정에 1.1배 이자 적용 (곱연산)
        result = await col.update_one({"user": "bob"}, {"$mul": {"balance": 1.1}})
        print("4) $mul matched/modified:", result.matched_count, result.modified_count)

        # 5. $max - alice의 balance가 500보다 작으면 500으로 올림 (현재 값과 비교해 더 큰 쪽 유지)
        result = await col.update_one({"user": "alice"}, {"$max": {"balance": 500}})
        print("5) $max matched/modified:", result.matched_count, result.modified_count)

        # 6. $min - alice의 balance가 300보다 크면 300으로 낮춤 (현재 값과 비교해 더 작은 쪽 유지)
        result = await col.update_one({"user": "alice"}, {"$min": {"balance": 300}})
        print("6) $min matched/modified:", result.matched_count, result.modified_count)

        # 7. $push - bob의 tags 배열에 태그 추가 (필드가 없으면 새로 만들어짐)
        result = await col.update_one({"user": "bob"}, {"$push": {"tags": "vip"}})
        print("7) $push matched/modified:", result.matched_count, result.modified_count)

        # 8. $addToSet - 이미 있는 값은 중복 추가하지 않음 ("vip"는 무시, "new"만 추가됨)
        result = await col.update_one(
            {"user": "bob"}, {"$addToSet": {"tags": {"$each": ["vip", "new"]}}}
        )
        print("8) $addToSet matched/modified:", result.matched_count, result.modified_count)

        # 9. $unset - carol에 임시로 넣어둔 필드를 제거
        await col.update_one({"user": "carol"}, {"$set": {"temp_note": "draft"}})
        result = await col.update_one({"user": "carol"}, {"$unset": {"temp_note": ""}})
        print("9) $unset matched/modified:", result.matched_count, result.modified_count)

        # 10. $rename - carol의 "balance" 필드명을 "cash"로 변경
        result = await col.update_one({"user": "carol"}, {"$rename": {"balance": "cash"}})
        print("10) $rename matched/modified:", result.matched_count, result.modified_count)

        print("최종 상태:", await col.find({}, {"_id": 0}).to_list())


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_pymongo --eval "db.ex04_accounts.find()"
