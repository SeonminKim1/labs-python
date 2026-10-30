"""ex10: 이벤트 훅 (before_event) - updated_at 자동 설정과 훅이 실행되지 않는 경우."""
import asyncio
from datetime import datetime, timezone

from beanie import Document, Insert, Replace, Save, SaveChanges, Update, before_event
from beanie.operators import Set

from common import init, raw


class Post(Document):
    title: str
    updated_at: datetime | None = None

    class Settings:
        name = "ex10_posts"

    # 메서드마다 발생하는 이벤트가 다르다: Save를 빼면 save()에서, Update를 빼면 set()에서
    # 훅은 돌아도 바뀐 updated_at이 DB에 저장되지 않는다 → 다섯 개를 모두 건다
    @before_event(Insert, Replace, Save, SaveChanges, Update)
    def touch(self):
        self.updated_at = datetime.now(timezone.utc)


async def touched(doc, op):
    """op 실행 전후로 DB의 updated_at이 바뀌었는지 (시각 차이가 보이도록 10ms 대기)."""
    before = (await raw(doc))["updated_at"]
    await asyncio.sleep(0.01)
    await op
    return (await raw(doc))["updated_at"] != before


async def main():
    async with init(Post):
        await Post.delete_all()

        # 1. insert - 저장 직전에 훅이 실행되어 updated_at이 채워진다
        post = Post(title="hello")
        await post.insert()
        print("1) insert:", await raw(post))

        # 2. 객체 단위 수정(save, set 등)은 훅이 실행된다
        post.title = "hello2"
        print("2) save() :", await touched(post, post.save()))
        print("2) set()  :", await touched(post, post.set({Post.title: "hello3"})))

        # 3. 주의: 쿼리 단위 작업은 객체를 거치지 않아 훅이 실행되지 않는다
        print("3) find().update():", await touched(post, Post.find(Post.id == post.id).update(Set({Post.title: "x"}))))
        await Post.insert_many([Post(title="bulk")])
        print("3) insert_many   :", (await Post.find_one(Post.title == "bulk")).updated_at)
        # → 쿼리 단위로 수정할 땐 Set({..., Post.updated_at: 현재 시각})처럼 직접 넣는다


if __name__ == "__main__":
    asyncio.run(main())

# 확인:
# - docker exec -it k8s-client-mongo mongosh example_beanie --eval "db.ex10_posts.find()"
