"""
Dialogue Knowledge (대화 지식) 서비스
"""
from typing import List, Optional, Dict, Any
from database.connection import DatabaseConnection
from common.utils.logger import logger
from common.utils.jsonb_handler import serialize_jsonb_data, parse_jsonb_data


class DialogueKnowledgeService:
    """Dialogue Knowledge (대화 지식) 서비스"""
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        self.db = db_connection or DatabaseConnection()
    
    async def get_all_knowledge(self) -> List[Dict[str, Any]]:
        """모든 Dialogue Knowledge 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        knowledge_id, title, content, knowledge_type,
                        related_entities, related_topics, knowledge_properties,
                        created_at, updated_at
                    FROM game_data.dialogue_knowledge
                    ORDER BY knowledge_type, title
                """)
                
                knowledge_list = []
                for row in rows:
                    knowledge_list.append({
                        "knowledge_id": row['knowledge_id'],
                        "title": row['title'],
                        "content": row['content'],
                        "knowledge_type": row['knowledge_type'],
                        "related_entities": parse_jsonb_data(row['related_entities']) or {},
                        "related_topics": parse_jsonb_data(row['related_topics']) or {},
                        "knowledge_properties": parse_jsonb_data(row['knowledge_properties']) or {},
                        "created_at": row['created_at'],
                        "updated_at": row['updated_at']
                    })
                
                return knowledge_list
        except Exception as e:
            logger.error(f"Dialogue Knowledge 전체 조회 실패: {e}")
            raise
    
    async def get_knowledge(self, knowledge_id: str) -> Optional[Dict[str, Any]]:
        """특정 Dialogue Knowledge 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT 
                        knowledge_id, title, content, knowledge_type,
                        related_entities, related_topics, knowledge_properties,
                        created_at, updated_at
                    FROM game_data.dialogue_knowledge
                    WHERE knowledge_id = $1
                """, knowledge_id)
                
                if not row:
                    return None
                
                return {
                    "knowledge_id": row['knowledge_id'],
                    "title": row['title'],
                    "content": row['content'],
                    "knowledge_type": row['knowledge_type'],
                    "related_entities": parse_jsonb_data(row['related_entities']) or {},
                    "related_topics": parse_jsonb_data(row['related_topics']) or {},
                    "knowledge_properties": parse_jsonb_data(row['knowledge_properties']) or {},
                    "created_at": row['created_at'],
                    "updated_at": row['updated_at']
                }
        except Exception as e:
            logger.error(f"Dialogue Knowledge 조회 실패: {e}")
            raise
    
    async def get_knowledge_by_type(self, knowledge_type: str) -> List[Dict[str, Any]]:
        """특정 타입의 Dialogue Knowledge 조회"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        knowledge_id, title, content, knowledge_type,
                        related_entities, related_topics, knowledge_properties,
                        created_at, updated_at
                    FROM game_data.dialogue_knowledge
                    WHERE knowledge_type = $1
                    ORDER BY title
                """, knowledge_type)
                
                knowledge_list = []
                for row in rows:
                    knowledge_list.append({
                        "knowledge_id": row['knowledge_id'],
                        "title": row['title'],
                        "content": row['content'],
                        "knowledge_type": row['knowledge_type'],
                        "related_entities": parse_jsonb_data(row['related_entities']) or {},
                        "related_topics": parse_jsonb_data(row['related_topics']) or {},
                        "knowledge_properties": parse_jsonb_data(row['knowledge_properties']) or {},
                        "created_at": row['created_at'],
                        "updated_at": row['updated_at']
                    })
                
                return knowledge_list
        except Exception as e:
            logger.error(f"타입별 Dialogue Knowledge 조회 실패: {e}")
            raise
    
    async def create_knowledge(
        self,
        knowledge_id: str,
        title: str,
        content: str,
        knowledge_type: str,
        related_entities: Optional[Dict[str, Any]] = None,
        related_topics: Optional[Dict[str, Any]] = None,
        knowledge_properties: Optional[Dict[str, Any]] = None
    ) -> str:
        """Dialogue Knowledge 생성"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO game_data.dialogue_knowledge
                    (knowledge_id, title, content, knowledge_type,
                     related_entities, related_topics, knowledge_properties,
                     created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """,
                    knowledge_id,
                    title,
                    content,
                    knowledge_type,
                    serialize_jsonb_data(related_entities or {}),
                    serialize_jsonb_data(related_topics or {}),
                    serialize_jsonb_data(knowledge_properties or {})
                )
                
                return knowledge_id
        except Exception as e:
            logger.error(f"Dialogue Knowledge 생성 실패: {e}")
            raise
    
    async def update_knowledge(
        self,
        knowledge_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        knowledge_type: Optional[str] = None,
        related_entities: Optional[Dict[str, Any]] = None,
        related_topics: Optional[Dict[str, Any]] = None,
        knowledge_properties: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Dialogue Knowledge 업데이트"""
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
                if knowledge_type is not None:
                    update_fields.append(f"knowledge_type = ${param_index}")
                    values.append(knowledge_type)
                    param_index += 1
                if related_entities is not None:
                    update_fields.append(f"related_entities = ${param_index}")
                    values.append(serialize_jsonb_data(related_entities))
                    param_index += 1
                if related_topics is not None:
                    update_fields.append(f"related_topics = ${param_index}")
                    values.append(serialize_jsonb_data(related_topics))
                    param_index += 1
                if knowledge_properties is not None:
                    update_fields.append(f"knowledge_properties = ${param_index}")
                    values.append(serialize_jsonb_data(knowledge_properties))
                    param_index += 1
                
                if not update_fields:
                    # 업데이트할 필드가 없으면 조회만 반환
                    return await self.get_knowledge(knowledge_id)
                
                # updated_at 업데이트
                update_fields.append(f"updated_at = CURRENT_TIMESTAMP")
                
                values.append(knowledge_id)
                query = f"""
                    UPDATE game_data.dialogue_knowledge
                    SET {', '.join(update_fields)}
                    WHERE knowledge_id = ${param_index}
                """
                
                await conn.execute(query, *values)
                
                return await self.get_knowledge(knowledge_id)
        except Exception as e:
            logger.error(f"Dialogue Knowledge 업데이트 실패: {e}")
            raise
    
    async def delete_knowledge(self, knowledge_id: str) -> bool:
        """Dialogue Knowledge 삭제"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM game_data.dialogue_knowledge
                    WHERE knowledge_id = $1
                """, knowledge_id)
                
                return result == "DELETE 1"
        except Exception as e:
            logger.error(f"Dialogue Knowledge 삭제 실패: {e}")
            raise

