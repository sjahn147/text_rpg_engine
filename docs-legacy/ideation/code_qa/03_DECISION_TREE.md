# RPG Engine Decision Tree – Operational Judgment Rules

> **최신화 날짜**: 2025-12-28

본 문서는 에이전트가 개발 중 "무엇을 할 수 있고, 무엇을 중단해야 하며, 언제 인간 승인(Human Confirm)이 필요한지"를 정의한다.

---

## 1. Database Operation Decision Tree

```
┌── Is DB being modified? (INSERT, UPDATE, DELETE, ALTER)
│
│   ┌── NO → Safe to Execute (Read-Only)
│   │
│   └── YES
│         └── Has Backup Plan?
│               │
│               ├── NO → Block & Request Backup Setup
│               └── YES
│                     └── Has Human Confirmation?
│                           │
│                           ├── NO → Block & Request Confirm
│                           └── YES → Execute
```

Blocking Conditions
- 스키마 변경 (DROP, ALTER, TRUNCATE)
- 데이터 전체 삭제 (`DELETE FROM *`, `WHERE 1=1`)
- 프로덕션 DB 작업

---

## 2. Exception Handling Decision Tree

```
┌── Is there a specific Exception class?
│
│   ┌── YES → Use specific exception
│   └── NO → Create/Refactor to explicit exception

┌── Is 'except:' or 'except Exception:' used?
    ├── YES → Block & Request Refactor
    └── NO → Accept
```

---

## 3. Refactoring Trigger Tree

```
┌── Function length > 50 lines?
│     ├── YES → Refactor Required
│     └── NO
│
┌── Nested blocks > 3 (if, for, while)?
│     ├── YES → Strategy/Validator extraction
│     └── NO
│
┌── Duplicate logic found?
      ├── YES → Extract Method/Class
      └── NO → Accept
```

---

## 4. Test Quality Tree

```
┌── Is a failing test present before implementation?
│     ├── NO → Block (Test First Required)
│     └── YES
│
┌── Is external dependency mocked?
│     ├── NO → Require Mock/Stub
│     └── YES
│
┌── Coverage >= 80%?
      ├── NO → Block Merge
      └── YES → Accept
```

---

## 5. Immutability Rule Tree

```
┌── Is object mutated in-place?
│     ├── YES → Replace with immutable copy
│     └── NO
│
┌── Is global/shared state modified?
      ├── YES → Block & Redesign with DI
      └── NO → Accept
```

---

## 6. Async Rule Tree

```
┌── Is I/O or DB call inside sync function?
│     ├── YES → Block & Convert to async
│     └── NO
│
┌── Is global lock used for concurrency?
      ├── YES → Replace with granular lock/semaphore
      └── NO → Accept
```

---

## 7. Critical Review Tree (PR Evaluation)

```
┌── Does code "work"?
│       └─ 무효. 동작만으로는 승인되지 않음.
│
┌── Does code "reveal intent" clearly?
│       ├─ NO → Request Documentation/Refactor
│       └─ YES
│
┌── Are potential failures addressed (try/except/test)?
        ├─ NO → Block
        └─ YES → Accept
```

---

## 8. Runtime vs Tooling Conflict Resolution

```
┌── Context?
│     ├── runtime (frame/tick-bound)
│     │     ┌── Is hot path within frame budget?
│     │     │     ├── NO → Allow controlled local mutation inside tick → Create immutable snapshot at tick end → Accept
│     │     │     └── YES → Prefer immutable structures (structural sharing) → Accept
│     │
│     │     ┌── Non-determinism (RNG/AI)?
│     │           ├── YES → Use simulation/property-based/golden-snapshot tests → Accept
│     │           └── NO → Use classic TDD unit/integration tests → Accept
│     │
│     │     ┌── DB access needed?
│     │           ├── YES → Block (runtime is memory-first) → Move to preload/cache/tooling
│     │           └── NO → Accept
│
│     └── tooling (editor/data/DB)
│           ├── MUST follow: schema-first, backup, human-confirm
│           ├── Prohibit string SQL, broad exception, global state
│           └── Strict TDD + type-safety enforced
```

Priority Override Rules
- MUST items always block PR. SHOULD/MAY yield warnings/suggestions only.
- Runtime frame budget breach permits local mutation within the tick, provided immutable snapshot export at tick boundary.
- RNG/AI determinism is not required; instead, require simulation/property-based coverage and reproducible seeds for golden snapshots.

---

## 9. Human Escalation Protocol

| 상황 | 반드시 인간 승인 요청 |
|------|------------------------|
| DB 구조 변경 | Human Confirm 필요 |
| 성능 최적화로 기존 로직 삭제 | Human Confirm 필요 |
| 철학 위반 의도 감지 | Human Review 요청 |
| 외부 서비스 연동 | Credential 확인 필요 |
| 데이터 손실 가능 작업 | Human Backup Approval |

---

## 10. Final Principle

“모든 결정은 속도가 아닌 무결성을 기준으로 한다.”
위 트리 중 하나라도 위반되면, 에이전트는 개발을 계속하지 않고 문제를 명시적으로 보고해야 한다.
