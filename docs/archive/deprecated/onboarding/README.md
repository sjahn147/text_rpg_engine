# 📚 온보딩 문서

> **최신화 날짜**: 2025-12-28

**목적**: 새로운 개발자 또는 AI Agent가 프로젝트에 빠르게 합류할 수 있도록 지원

---

## 📋 문서 목록

### 🔥 필수 읽기 (순서대로)

1. **HANDOVER_2025-10-21.md** ⭐⭐⭐
   - 프로젝트 인수인계서 (Part 1)
   - 프로젝트 개요, 문서 읽기 순서, 핵심 아키텍처
   - 예상 시간: 1시간

2. **HANDOVER_2025-10-21_PART2.md** ⭐⭐⭐
   - 프로젝트 인수인계서 (Part 2)
   - 작업 루틴, 알려진 이슈, 다음 작업 TODO
   - 예상 시간: 1시간

---

## 🚀 빠른 시작

### 1️⃣ 첫 1시간: 이해
```bash
# 순서대로 읽기
1. HANDOVER_2025-10-21.md (Part 1)
2. HANDOVER_2025-10-21_PART2.md (Part 2)
3. ../docs/@rules/코딩 컨벤션 및 품질 가이드.md
4. ../../database/setup/mvp_schema.sql
```

### 2️⃣ 두 번째 1시간: 검증
```bash
# 테스트 실행
cd ../../
python -m pytest tests/active/scenarios/test_entity_cell_interaction.py -v

# 결과: 4/4 테스트 통과 확인
```

### 3️⃣ 세 번째 시간: 첫 작업
```bash
# TODO 1: 동시 다중 세션 테스트 작성
# 파일: tests/active/scenarios/test_multi_session.py
```

---

## 📞 핵심 포인트

### ⚠️ 반드시 기억할 것

1. **Cell Manager는 사용자가 직접 수정!**
   - `app/world/cell_manager.py`
   - CURSOR search_replace 사용 금지
   
2. **3-Layer 구조 완전 이해 필수**
   - game_data → runtime_entities → entity_states

3. **JSONB 처리 주의**
   - parse_jsonb_data() 사용
   - position에서 current_cell_id 분리

4. **긴 컨텍스트 사용**
   - search_replace 시 10-15줄 이상
   - 함수 시그니처 포함

---

## 📊 현재 진행 상황

- **Phase 1**: Entity-Cell 상호작용 ✅ **완료** (4/4 테스트)
- **Phase 2**: Dialogue & Action 시스템 ⏳ **진행 예정**
- **Phase 3**: Village Simulation ⬜ **계획 단계**

---

## 🎯 다음 작업

1. [HIGH] 동시 다중 세션 테스트
2. [HIGH] DialogueManager 구현
3. [MEDIUM] ActionHandler 구현
4. [MEDIUM] 성능 테스트
5. [LOW] Village Simulation

---

**최종 업데이트**: 2025-10-21  
**작성자**: AI Assistant (Phase 1 완료)

