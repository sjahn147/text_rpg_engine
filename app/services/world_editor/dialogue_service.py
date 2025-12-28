"""
Dialogue (대화) 서비스
"""
from typing import List, Optional, Dict, Any
from database.connection import DatabaseConnection
from common.utils.logger import logger
from common.utils.jsonb_handler import serialize_jsonb_data, parse_jsonb_data


class DialogueService:
    """Dialogue (대화) 서비스"""
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        self.db = db_connection or DatabaseConnection()
    
    async def get_dialogue_contexts_by_entity(self, entity_id: str) -> List[Dict[str, Any]]:
        """특정 Entity의 모든 Dialogue Context 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        dialogue_id, title, content, entity_id, cell_id,
                        time_category, event_id, priority,
                        available_topics, entity_personality, constraints,
                        created_at, updated_at
                    FROM game_data.dialogue_contexts
                    WHERE entity_id = $1
                    ORDER BY priority DESC, created_at DESC
                """, entity_id)
                
                contexts = []
                for row in rows:
                    contexts.append({
                        "dialogue_id": row['dialogue_id'],
                        "title": row['title'],
                        "content": row['content'],
                        "entity_id": row['entity_id'],
                        "cell_id": row['cell_id'],
                        "time_category": row['time_category'],
                        "event_id": row['event_id'],
                        "priority": row['priority'],
                        "available_topics": parse_jsonb_data(row['available_topics']) or {},
                        "entity_personality": row['entity_personality'],
                        "constraints": parse_jsonb_data(row['constraints']) or {},
                        "created_at": row['created_at'],
                        "updated_at": row['updated_at']
                    })
                
                return contexts
        except Exception as e:
            logger.error(f"Dialogue Context 조회 실패: {e}")
            raise
    
    async def get_dialogue_context(self, dialogue_id: str) -> Optional[Dict[str, Any]]:
        """특정 Dialogue Context 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT 
                        dialogue_id, title, content, entity_id, cell_id,
                        time_category, event_id, priority,
                        available_topics, entity_personality, constraints,
                        created_at, updated_at
                    FROM game_data.dialogue_contexts
                    WHERE dialogue_id = $1
                """, dialogue_id)
                
                if not row:
                    return None
                
                return {
                    "dialogue_id": row['dialogue_id'],
                    "title": row['title'],
                    "content": row['content'],
                    "entity_id": row['entity_id'],
                    "cell_id": row['cell_id'],
                    "time_category": row['time_category'],
                    "event_id": row['event_id'],
                    "priority": row['priority'],
                    "available_topics": parse_jsonb_data(row['available_topics']) or {},
                    "entity_personality": row['entity_personality'],
                    "constraints": parse_jsonb_data(row['constraints']) or {},
                    "created_at": row['created_at'],
                    "updated_at": row['updated_at']
                }
        except Exception as e:
            logger.error(f"Dialogue Context 조회 실패: {e}")
            raise
    
    async def get_dialogue_topics(self, dialogue_id: str) -> List[Dict[str, Any]]:
        """특정 Dialogue Context의 모든 Topics 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        topic_id, dialogue_id, topic_type, content, conditions,
                        created_at, updated_at
                    FROM game_data.dialogue_topics
                    WHERE dialogue_id = $1
                    ORDER BY topic_type, created_at
                """, dialogue_id)
                
                topics = []
                for row in rows:
                    topics.append({
                        "topic_id": row['topic_id'],
                        "dialogue_id": row['dialogue_id'],
                        "topic_type": row['topic_type'],
                        "content": row['content'],
                        "conditions": parse_jsonb_data(row['conditions']) or {},
                        "created_at": row['created_at'],
                        "updated_at": row['updated_at']
                    })
                
                return topics
        except Exception as e:
            logger.error(f"Dialogue Topics 조회 실패: {e}")
            raise
    
    async def create_dialogue_context(
        self,
        dialogue_id: str,
        title: str,
        content: str,
        entity_id: Optional[str] = None,
        cell_id: Optional[str] = None,
        time_category: Optional[str] = None,
        event_id: Optional[str] = None,
        priority: int = 0,
        available_topics: Optional[Dict[str, Any]] = None,
        entity_personality: Optional[str] = None,
        constraints: Optional[Dict[str, Any]] = None
    ) -> str:
        """Dialogue Context 생성"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO game_data.dialogue_contexts
                    (dialogue_id, title, content, entity_id, cell_id,
                     time_category, event_id, priority,
                     available_topics, entity_personality, constraints,
                     created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """,
                dialogue_id,
                title,
                content,
                entity_id,
                cell_id,
                time_category,
                event_id,
                priority,
                serialize_jsonb_data(available_topics or {}),
                entity_personality,
                serialize_jsonb_data(constraints or {})
                )
                
                return dialogue_id
        except Exception as e:
            logger.error(f"Dialogue Context 생성 실패: {e}")
            raise
    
    async def update_dialogue_context(
        self,
        dialogue_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        entity_id: Optional[str] = None,
        cell_id: Optional[str] = None,
        time_category: Optional[str] = None,
        event_id: Optional[str] = None,
        priority: Optional[int] = None,
        available_topics: Optional[Dict[str, Any]] = None,
        entity_personality: Optional[str] = None,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Dialogue Context 업데이트"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                update_fields = []
                values = []
                param_index = 1
                
                if title is not None:
                    update_fields.append(f"title = ${param_index}")
                    values.append(title)
                    param_index += 1
                if content is not None:
                    update_fields.append(f"content = ${param_index}")
                    values.append(content)
                    param_index += 1
                if entity_id is not None:
                    update_fields.append(f"entity_id = ${param_index}")
                    values.append(entity_id)
                    param_index += 1
                if cell_id is not None:
                    update_fields.append(f"cell_id = ${param_index}")
                    values.append(cell_id)
                    param_index += 1
                if time_category is not None:
                    update_fields.append(f"time_category = ${param_index}")
                    values.append(time_category)
                    param_index += 1
                if event_id is not None:
                    update_fields.append(f"event_id = ${param_index}")
                    values.append(event_id)
                    param_index += 1
                if priority is not None:
                    update_fields.append(f"priority = ${param_index}")
                    values.append(priority)
                    param_index += 1
                if available_topics is not None:
                    update_fields.append(f"available_topics = ${param_index}")
                    values.append(serialize_jsonb_data(available_topics))
                    param_index += 1
                if entity_personality is not None:
                    update_fields.append(f"entity_personality = ${param_index}")
                    values.append(entity_personality)
                    param_index += 1
                if constraints is not None:
                    update_fields.append(f"constraints = ${param_index}")
                    values.append(serialize_jsonb_data(constraints))
                    param_index += 1
                
                if not update_fields:
                    return await self.get_dialogue_context(dialogue_id)
                
                update_fields.append(f"updated_at = CURRENT_TIMESTAMP")
                values.append(dialogue_id)
                
                await conn.execute(f"""
                    UPDATE game_data.dialogue_contexts
                    SET {', '.join(update_fields)}
                    WHERE dialogue_id = ${param_index}
                """, *values)
                
                return await self.get_dialogue_context(dialogue_id)
        except Exception as e:
            logger.error(f"Dialogue Context 업데이트 실패: {e}")
            raise
    
    async def create_dialogue_topic(
        self,
        topic_id: str,
        dialogue_id: str,
        topic_type: str,
        content: str,
        conditions: Optional[Dict[str, Any]] = None
    ) -> str:
        """Dialogue Topic 생성"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO game_data.dialogue_topics
                    (topic_id, dialogue_id, topic_type, content, conditions,
                     created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """,
                topic_id,
                dialogue_id,
                topic_type,
                content,
                serialize_jsonb_data(conditions or {})
                )
                
                return topic_id
        except Exception as e:
            logger.error(f"Dialogue Topic 생성 실패: {e}")
            raise
    
    async def update_dialogue_topic(
        self,
        topic_id: str,
        topic_type: Optional[str] = None,
        content: Optional[str] = None,
        conditions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Dialogue Topic 업데이트"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                update_fields = []
                values = []
                param_index = 1
                
                if topic_type is not None:
                    update_fields.append(f"topic_type = ${param_index}")
                    values.append(topic_type)
                    param_index += 1
                if content is not None:
                    update_fields.append(f"content = ${param_index}")
                    values.append(content)
                    param_index += 1
                if conditions is not None:
                    update_fields.append(f"conditions = ${param_index}")
                    values.append(serialize_jsonb_data(conditions))
                    param_index += 1
                
                if not update_fields:
                    row = await conn.fetchrow("""
                        SELECT topic_id, dialogue_id, topic_type, content, conditions,
                               created_at, updated_at
                        FROM game_data.dialogue_topics
                        WHERE topic_id = $1
                    """, topic_id)
                    if row:
                        return {
                            "topic_id": row['topic_id'],
                            "dialogue_id": row['dialogue_id'],
                            "topic_type": row['topic_type'],
                            "content": row['content'],
                            "conditions": parse_jsonb_data(row['conditions']) or {},
                            "created_at": row['created_at'],
                            "updated_at": row['updated_at']
                        }
                    return None
                
                update_fields.append(f"updated_at = CURRENT_TIMESTAMP")
                values.append(topic_id)
                
                await conn.execute(f"""
                    UPDATE game_data.dialogue_topics
                    SET {', '.join(update_fields)}
                    WHERE topic_id = ${param_index}
                """, *values)
                
                row = await conn.fetchrow("""
                    SELECT topic_id, dialogue_id, topic_type, content, conditions,
                           created_at, updated_at
                    FROM game_data.dialogue_topics
                    WHERE topic_id = $1
                """, topic_id)
                
                if row:
                    return {
                        "topic_id": row['topic_id'],
                        "dialogue_id": row['dialogue_id'],
                        "topic_type": row['topic_type'],
                        "content": row['content'],
                        "conditions": parse_jsonb_data(row['conditions']) or {},
                        "created_at": row['created_at'],
                        "updated_at": row['updated_at']
                    }
                return None
        except Exception as e:
            logger.error(f"Dialogue Topic 업데이트 실패: {e}")
            raise
    
    async def delete_dialogue_topic(self, topic_id: str) -> bool:
        """Dialogue Topic 삭제"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM game_data.dialogue_topics
                    WHERE topic_id = $1
                """, topic_id)
                
                return result == "DELETE 1"
        except Exception as e:
            logger.error(f"Dialogue Topic 삭제 실패: {e}")
            raise

