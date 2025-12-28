"""
성능 테스트

목적:
- 대량 데이터 처리 성능 검증
- 동시성 처리 성능 측정
- 메모리 사용량 및 응답 시간 최적화
- 시스템 한계점 파악
"""
import pytest
import pytest_asyncio
import asyncio
import time
import uuid
from typing import List, Dict, Any
from common.utils.logger import logger


@pytest.mark.asyncio
class TestPerformance:
    """성능 테스트"""
    
    async def test_massive_entity_creation_performance(self, db_with_templates, entity_manager):
        """
        시나리오: 대량 엔티티 생성 성능 테스트
        1. 1000개 엔티티 동시 생성
        2. 생성 시간 측정
        3. 성공률 확인
        """
        session_id = str(uuid.uuid4())
        entity_count = 1000
        templates = ["NPC_VILLAGER_001", "NPC_MERCHANT_001", "NPC_GOBLIN_001"]
        
        logger.info(f"[PERFORMANCE] Starting massive entity creation test: {entity_count} entities")
        
        start_time = time.time()
        
        # 대량 엔티티 생성
        async def create_entity_batch(batch_size: int) -> List[Dict[str, Any]]:
            tasks = []
            for i in range(batch_size):
                template = templates[i % len(templates)]
                task = entity_manager.create_entity(
                    static_entity_id=template,
                    session_id=session_id,
                    custom_position={"x": float(i), "y": float(i)}
                )
                tasks.append(task)
            return await asyncio.gather(*tasks)
        
        # 배치 단위로 생성 (메모리 효율성)
        batch_size = 100
        all_results = []
        
        for batch_start in range(0, entity_count, batch_size):
            batch_end = min(batch_start + batch_size, entity_count)
            current_batch_size = batch_end - batch_start
            
            batch_results = await create_entity_batch(current_batch_size)
            all_results.extend(batch_results)
            
            logger.info(f"[PERFORMANCE] Batch {batch_start//batch_size + 1} completed: {current_batch_size} entities")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 성공률 계산
        successful_entities = sum(1 for result in all_results if result.status == "success")
        success_rate = (successful_entities / entity_count) * 100
        
        # 성능 지표
        entities_per_second = entity_count / total_time
        
        logger.info(f"[PERFORMANCE] Massive entity creation completed")
        logger.info(f"[PERFORMANCE] Total time: {total_time:.2f} seconds")
        logger.info(f"[PERFORMANCE] Success rate: {success_rate:.1f}%")
        logger.info(f"[PERFORMANCE] Entities per second: {entities_per_second:.1f}")
        
        # 성능 기준 검증
        assert success_rate >= 95.0, f"Success rate too low: {success_rate:.1f}%"
        assert entities_per_second >= 50.0, f"Performance too low: {entities_per_second:.1f} entities/sec"
        assert total_time <= 30.0, f"Total time too long: {total_time:.2f} seconds"
        
        logger.info(f"[OK] Massive entity creation performance test passed")
    
    async def test_concurrent_session_performance(self, db_with_templates, entity_manager, cell_manager):
        """
        시나리오: 동시 세션 성능 테스트
        1. 50개 세션 동시 생성
        2. 각 세션에서 10개 엔티티 생성
        3. 성능 측정
        """
        session_count = 50
        entities_per_session = 10
        total_entities = session_count * entities_per_session
        templates = ["NPC_VILLAGER_001", "NPC_MERCHANT_001", "NPC_GOBLIN_001"]
        
        logger.info(f"[PERFORMANCE] Starting concurrent session test: {session_count} sessions, {total_entities} total entities")
        
        start_time = time.time()
        
        async def create_session_entities(session_id: str, count: int) -> List[Dict[str, Any]]:
            """세션별 엔티티 생성"""
            results = []
            for i in range(count):
                template = templates[i % len(templates)]
                result = await entity_manager.create_entity(
                    static_entity_id=template,
                    session_id=session_id,
                    custom_position={"x": float(i), "y": float(i)}
                )
                results.append(result)
            return results
        
        # 모든 세션 동시 실행
        session_tasks = []
        for i in range(session_count):
            session_id = str(uuid.uuid4())
            task = create_session_entities(session_id, entities_per_session)
            session_tasks.append(task)
        
        all_results = await asyncio.gather(*session_tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 결과 집계
        all_entities = []
        for session_results in all_results:
            all_entities.extend(session_results)
        
        successful_entities = sum(1 for result in all_entities if result.status == "success")
        success_rate = (successful_entities / total_entities) * 100
        
        # 성능 지표
        entities_per_second = total_entities / total_time
        sessions_per_second = session_count / total_time
        
        logger.info(f"[PERFORMANCE] Concurrent session test completed")
        logger.info(f"[PERFORMANCE] Total time: {total_time:.2f} seconds")
        logger.info(f"[PERFORMANCE] Success rate: {success_rate:.1f}%")
        logger.info(f"[PERFORMANCE] Entities per second: {entities_per_second:.1f}")
        logger.info(f"[PERFORMANCE] Sessions per second: {sessions_per_second:.1f}")
        
        # 성능 기준 검증
        assert success_rate >= 90.0, f"Success rate too low: {success_rate:.1f}%"
        assert entities_per_second >= 100.0, f"Entity performance too low: {entities_per_second:.1f} entities/sec"
        assert sessions_per_second >= 5.0, f"Session performance too low: {sessions_per_second:.1f} sessions/sec"
        
        logger.info(f"[OK] Concurrent session performance test passed")
    
    async def test_cell_operations_performance(self, db_with_templates, entity_manager, cell_manager):
        """
        시나리오: 셀 작업 성능 테스트
        1. 100개 셀 생성
        2. 각 셀에 20개 엔티티 배치
        3. 엔티티 이동 작업
        4. 성능 측정
        """
        session_id = str(uuid.uuid4())
        cell_count = 100
        entities_per_cell = 20
        total_entities = cell_count * entities_per_cell
        
        logger.info(f"[PERFORMANCE] Starting cell operations test: {cell_count} cells, {total_entities} entities")
        
        start_time = time.time()
        
        # 1. 셀 생성
        cell_creation_start = time.time()
        cell_tasks = []
        for i in range(cell_count):
            cell_id = f"CELL_PERF_{i:03d}"
            task = cell_manager.create_cell(
                static_cell_id="CELL_VILLAGE_SQUARE_001",
                session_id=session_id
            )
            cell_tasks.append(task)
        
        cell_results = await asyncio.gather(*cell_tasks)
        cell_creation_time = time.time() - cell_creation_start
        
        # 2. 엔티티 생성 및 셀 배치
        entity_placement_start = time.time()
        all_entities = []
        
        for cell_idx, cell_result in enumerate(cell_results):
            if not cell_result.success:
                continue
                
            cell_id = cell_result.cell.cell_id
            
            # 셀별 엔티티 생성 및 배치
            for entity_idx in range(entities_per_cell):
                template = "NPC_VILLAGER_001"
                entity_result = await entity_manager.create_entity(
                    static_entity_id=template,
                    session_id=session_id,
                    custom_position={"x": float(entity_idx), "y": float(entity_idx)}
                )
                
                if entity_result.status == "success":
                    await cell_manager.add_entity_to_cell(entity_result.entity_id, cell_id)
                    all_entities.append(entity_result.entity_id)
        
        entity_placement_time = time.time() - entity_placement_start
        
        # 3. 셀 컨텐츠 로드 성능 테스트
        content_load_start = time.time()
        content_tasks = []
        for cell_result in cell_results:
            if cell_result.success:
                task = cell_manager.load_cell_content(cell_result.cell.cell_id)
                content_tasks.append(task)
        
        content_results = await asyncio.gather(*content_tasks)
        content_load_time = time.time() - content_load_start
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 성능 지표
        cells_per_second = cell_count / cell_creation_time
        entities_per_second = len(all_entities) / entity_placement_time
        content_loads_per_second = len(content_tasks) / content_load_time
        
        logger.info(f"[PERFORMANCE] Cell operations test completed")
        logger.info(f"[PERFORMANCE] Total time: {total_time:.2f} seconds")
        logger.info(f"[PERFORMANCE] Cell creation: {cells_per_second:.1f} cells/sec")
        logger.info(f"[PERFORMANCE] Entity placement: {entities_per_second:.1f} entities/sec")
        logger.info(f"[PERFORMANCE] Content loading: {content_loads_per_second:.1f} loads/sec")
        
        # 성능 기준 검증
        assert cells_per_second >= 10.0, f"Cell creation too slow: {cells_per_second:.1f} cells/sec"
        assert entities_per_second >= 50.0, f"Entity placement too slow: {entities_per_second:.1f} entities/sec"
        assert content_loads_per_second >= 20.0, f"Content loading too slow: {content_loads_per_second:.1f} loads/sec"
        
        logger.info(f"[OK] Cell operations performance test passed")
    
    async def test_dialogue_system_performance(self, db_with_templates, entity_manager, dialogue_manager):
        """
        시나리오: 대화 시스템 성능 테스트
        1. 100개 대화 세션 동시 실행
        2. 대화 시작, 진행, 종료 성능 측정
        3. 메모리 사용량 확인
        """
        session_id = str(uuid.uuid4())
        dialogue_count = 100
        
        logger.info(f"[PERFORMANCE] Starting dialogue system test: {dialogue_count} dialogues")
        
        start_time = time.time()
        
        # 플레이어와 NPC 생성
        player_result = await entity_manager.create_entity(
            static_entity_id="NPC_VILLAGER_001",
            session_id=session_id
        )
        assert player_result.status == "success"
        player_id = player_result.entity_id
        
        npc_result = await entity_manager.create_entity(
            static_entity_id="NPC_MERCHANT_001",
            session_id=session_id
        )
        assert npc_result.status == "success"
        npc_id = npc_result.entity_id
        
        # 대화 성능 테스트
        async def perform_dialogue_sequence(dialogue_id: int) -> Dict[str, Any]:
            """대화 시퀀스 실행"""
            try:
                # 대화 시작
                start_result = await dialogue_manager.start_dialogue(
                    player_id=player_id,
                    npc_id=npc_id,
                    session_id=session_id
                )
                
                if not start_result.success:
                    return {"success": False, "error": "start_failed"}
                
                # 대화 진행
                continue_result = await dialogue_manager.continue_dialogue(
                    player_id=player_id,
                    npc_id=npc_id,
                    session_id=session_id,
                    topic="trade"
                )
                
                if not continue_result.success:
                    return {"success": False, "error": "continue_failed"}
                
                # 대화 종료
                end_result = await dialogue_manager.end_dialogue(
                    player_id=player_id,
                    npc_id=npc_id
                )
                
                return {
                    "success": end_result.success,
                    "dialogue_id": dialogue_id,
                    "start_success": start_result.success,
                    "continue_success": continue_result.success,
                    "end_success": end_result.success
                }
                
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        # 모든 대화 동시 실행
        dialogue_tasks = []
        for i in range(dialogue_count):
            task = perform_dialogue_sequence(i)
            dialogue_tasks.append(task)
        
        dialogue_results = await asyncio.gather(*dialogue_tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 결과 분석
        successful_dialogues = sum(1 for result in dialogue_results if result.get("success", False))
        success_rate = (successful_dialogues / dialogue_count) * 100
        
        # 성능 지표
        dialogues_per_second = dialogue_count / total_time
        
        logger.info(f"[PERFORMANCE] Dialogue system test completed")
        logger.info(f"[PERFORMANCE] Total time: {total_time:.2f} seconds")
        logger.info(f"[PERFORMANCE] Success rate: {success_rate:.1f}%")
        logger.info(f"[PERFORMANCE] Dialogues per second: {dialogues_per_second:.1f}")
        
        # 성능 기준 검증
        assert success_rate >= 80.0, f"Dialogue success rate too low: {success_rate:.1f}%"
        assert dialogues_per_second >= 10.0, f"Dialogue performance too low: {dialogues_per_second:.1f} dialogues/sec"
        assert total_time <= 20.0, f"Total time too long: {total_time:.2f} seconds"
        
        logger.info(f"[OK] Dialogue system performance test passed")
    
    async def test_memory_usage_optimization(self, db_with_templates, entity_manager):
        """
        시나리오: 메모리 사용량 최적화 테스트
        1. 대량 데이터 생성 후 메모리 사용량 확인
        2. 가비지 컬렉션 후 메모리 정리 확인
        3. 메모리 누수 방지 검증
        """
        import gc
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        logger.info(f"[PERFORMANCE] Starting memory usage optimization test")
        
        # 초기 메모리 사용량
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        logger.info(f"[PERFORMANCE] Initial memory usage: {initial_memory:.1f} MB")
        
        # 대량 엔티티 생성
        session_id = str(uuid.uuid4())
        entity_count = 500
        
        start_time = time.time()
        
        entities = []
        for i in range(entity_count):
            result = await entity_manager.create_entity(
                static_entity_id="NPC_VILLAGER_001",
                session_id=session_id,
                custom_position={"x": float(i), "y": float(i)}
            )
            if result.status == "success":
                entities.append(result.entity_id)
        
        creation_time = time.time() - start_time
        
        # 생성 후 메모리 사용량
        after_creation_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = after_creation_memory - initial_memory
        
        logger.info(f"[PERFORMANCE] After creation memory: {after_creation_memory:.1f} MB")
        logger.info(f"[PERFORMANCE] Memory increase: {memory_increase:.1f} MB")
        logger.info(f"[PERFORMANCE] Memory per entity: {memory_increase / len(entities):.3f} MB")
        
        # 가비지 컬렉션
        gc.collect()
        
        # GC 후 메모리 사용량
        after_gc_memory = process.memory_info().rss / 1024 / 1024  # MB
        gc_effectiveness = ((after_creation_memory - after_gc_memory) / after_creation_memory) * 100
        
        logger.info(f"[PERFORMANCE] After GC memory: {after_gc_memory:.1f} MB")
        logger.info(f"[PERFORMANCE] GC effectiveness: {gc_effectiveness:.1f}%")
        
        # 성능 기준 검증
        assert memory_increase <= 100.0, f"Memory increase too high: {memory_increase:.1f} MB"
        assert memory_increase / len(entities) <= 0.5, f"Memory per entity too high: {memory_increase / len(entities):.3f} MB"
        assert gc_effectiveness >= 0.0, f"GC not effective: {gc_effectiveness:.1f}%"
        
        logger.info(f"[OK] Memory usage optimization test passed")
