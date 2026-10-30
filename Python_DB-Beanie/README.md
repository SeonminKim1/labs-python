# example-beanie

[Beanie](https://beanie-odm.dev/) (MongoDB 비동기 ODM) 학습용 예제 모음. pymongo 버전: `../Python_DB_Pymongo_Async`

## 사전 준비

- Python >= 3.11, [uv](https://docs.astral.sh/uv/)
- `mongodb://localhost:27017`에서 접속 가능한 MongoDB
  (예: `docker run -d -p 27017:27017 mongo`)
- 의존성 설치: `uv sync` (beanie 2.x, pymongo `AsyncMongoClient` 기반)

## 실행

```
uv run python ex1.py
```

- `common.py`: 연결·초기화 `init(*models)`, 저장된 문서 확인 `raw(doc)`
- 컬렉션 이름: `ex<번호>_<이름>`

## 목차

| # | 파일 | 내용 |
|---|------|------|
| 1 | `ex1.py` | `Document` 정의 + `init_beanie` 연결, `id` ↔ `_id` 저장 모양 |
| 2 | `ex2.py` | 삽입 (`insert`, `insert_many`, `save`)과 pydantic 검증, `validate_on_save` |
| 3 | `ex3.py` | 조회 (`get`, `find_one`, `find`, 필드 비교식, `beanie.operators`, dict 필터, `Or`) |
| 4 | `ex4.py` | 수정 (`set`, `inc`, `find().update`, `Push`), `save()` vs `replace()` |
| 5 | `ex5.py` | 삭제 (`delete`, `find().delete`, `find_one().delete`) |
| 6 | `ex6.py` | 정렬, `skip`/`limit` vs keyset 페이지네이션, `count`, projection 모델 |
| 7 | `ex7.py` | 중첩 모델·리스트 필드 조회 (dot 경로, 배열 매칭, `All`, `ElemMatch`) |
| 8 | `ex8.py` | upsert (`find_one().upsert`, `update(upsert=True)`) |
| 9 | `ex9.py` | 상태 관리 (`use_state_management`, `get_changes`, `save_changes`) |
| 10 | `ex10.py` | 이벤트 훅 (`before_event`)으로 `updated_at` 자동 설정 |
| 11 | `ex11.py` | 낙관적 락 (`use_revision`, `RevisionIdWasChanged`, 재시도) |
| 12 | `ex12.py` | 인덱스 (`Indexed`, `Settings.indexes`, `explain`), unique + `DuplicateKeyError`, 동시 upsert 중복 막기 |
| 13 | `ex13.py` | 문서 참조 (`Link`, `BackLink`, `fetch_link`, `fetch_links`, `WriteRules.WRITE`), N+1 조회 비교 |
| 14 | `ex14.py` | 집계 (`sum`/`avg`/`max`/`min`, `aggregate`, `projection_model`) |

제외: 트랜잭션(replica set 필요), 마이그레이션, 상속, Time-series, View
