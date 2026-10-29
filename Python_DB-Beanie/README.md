# example-beanie

[Beanie](https://beanie-odm.dev/) (MongoDB 비동기 ODM) 학습용 예제 모음.
pymongo 예제(`../Python_DB_Pymongo_Async`)와 같은 형식이며, 모델(pydantic) 기반으로 같은 일을 어떻게 하는지 비교하며 보면 좋다.

## 사전 준비

- Python >= 3.11, [uv](https://docs.astral.sh/uv/)
- `mongodb://localhost:27017`에서 접속 가능한 MongoDB
  (예: `docker run -d -p 27017:27017 mongo`)
- 의존성 설치: `uv sync` (beanie 2.x — motor가 아닌 pymongo `AsyncMongoClient` 기반)

## 실행

```
uv run python ex1.py
```

공용 연결/초기화(`MONGO_URI`, `DB_NAME`, `init(*models)`)와 DB에 실제 저장된 문서를 보는 `raw(doc)`는 `common.py`에 있다.
각 예제는 `ex<번호>_<이름>` 컬렉션을 사용한다.

## 목차

연결 → 기본 CRUD → 조회 기법 → 쓰기 기법 → 인덱스 → 관계/집계 순으로 배치했다.

| # | 파일 | 내용 |
|---|------|------|
| 1 | `ex1.py` | `Document` 정의 + `init_beanie` 연결, `id` ↔ `_id` 저장 모양 |
| 2 | `ex2.py` | 삽입 (`insert`, `insert_many`, `save`) + `insert_many` id 함정, 에러가 나도 저장되는 검증 함정과 `validate_on_save` |
| 3 | `ex3.py` | 조회 (`get`, `find_one`, `find`, 필드 비교식, `beanie.operators`, dict 필터, `and`/`or` 함정) |
| 4 | `ex4.py` | 수정 (`set`, `inc`, `find().update`, `Push`) + 읽어둔 객체 미갱신, `save()` lost update 함정, `save()` vs `replace()` |
| 5 | `ex5.py` | 삭제 (`delete`, `find().delete`, `find_one().delete`) + sort/limit이 무시되는 삭제 범위 함정 |
| 6 | `ex6.py` | 정렬, `skip`/`limit` vs keyset 페이지네이션, 쿼리 객체가 바뀌는 `count` 함정, projection 모델 |
| 7 | `ex7.py` | 중첩 모델·리스트 필드 조회 (dot 경로, 배열 매칭, `All`, `ElemMatch`) + 원소 간 조건 분산 함정 |
| 8 | `ex8.py` | upsert (`find_one().upsert`, `update(upsert=True)`) + `on_insert` 동작·반환 타입 함정 |
| 9 | `ex9.py` | 상태 관리 (`use_state_management`, `get_changes`, `save_changes`) + 같은 필드 충돌·`save()` 함정 |

(예제를 추가/수정할 때마다 이 표도 같이 갱신한다.)
