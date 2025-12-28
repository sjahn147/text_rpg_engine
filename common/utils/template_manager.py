"""
템플릿 관리 시스템
모든 템플릿을 DB에서 동적으로 관리
"""
import json
import random
from typing import Dict, Any, Optional, List, Union
from database.connection import DatabaseConnection
from common.utils.logger import logger


class TemplateManager:
    """템플릿 관리 클래스"""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
        self._template_cache: Dict[str, Dict[str, List[str]]] = {}
        self._cache_loaded = False
    
    async def load_all_templates(self):
        """모든 템플릿을 DB에서 로드"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                # 대화 컨텍스트에서 템플릿 로드
                dialogue_templates = await conn.fetch("""
                    SELECT title, content, available_topics, entity_personality, priority
                    FROM game_data.dialogue_contexts
                    WHERE is_active = TRUE
                    ORDER BY priority DESC, title
                """)
                
                # 템플릿을 카테고리별로 분류
                self._template_cache = {
                    'greeting': [],
                    'trade': [],
                    'lore': [],
                    'quest': [],
                    'farewell': [],
                    'general': []
                }
                
                for template in dialogue_templates:
                    title = template['title'].lower()
                    content = template['content']
                    topics = parse_jsonb_data(template['available_topics']) or {}
                    personality = template['entity_personality'] or 'neutral'
                    priority = template['priority'] or 0
                    
                    # 템플릿 데이터 구성
                    template_data = {
                        'content': content,
                        'personality': personality,
                        'priority': priority,
                        'topics': topics
                    }
                    
                    # 주제별 분류
                    if 'greeting' in title or 'greeting' in topics:
                        self._template_cache['greeting'].append(template_data)
                    elif 'trade' in title or 'trade' in topics:
                        self._template_cache['trade'].append(template_data)
                    elif 'lore' in title or 'lore' in topics:
                        self._template_cache['lore'].append(template_data)
                    elif 'quest' in title or 'quest' in topics:
                        self._template_cache['quest'].append(template_data)
                    elif 'farewell' in title or 'farewell' in topics:
                        self._template_cache['farewell'].append(template_data)
                    else:
                        self._template_cache['general'].append(template_data)
                
                # 기본 템플릿이 없으면 기본값 설정
                self._ensure_default_templates()
                
                self._cache_loaded = True
                logger.info(f"Loaded templates from database: {sum(len(templates) for templates in self._template_cache.values())} total")
                
        except Exception as e:
            logger.error(f"Failed to load templates: {str(e)}")
            self._set_fallback_templates()
    
    def _ensure_default_templates(self):
        """기본 템플릿이 없으면 기본값 설정"""
        default_templates = {
            'greeting': [
                {'content': '안녕하세요! 무엇을 도와드릴까요?', 'personality': 'neutral', 'priority': 0},
                {'content': '오, 새로운 얼굴이군요!', 'personality': 'friendly', 'priority': 0},
                {'content': '여기서 뭘 하고 계신가요?', 'personality': 'curious', 'priority': 0},
                {'content': '반갑습니다! 여기 처음 오신 건가요?', 'personality': 'welcoming', 'priority': 0}
            ],
            'trade': [
                {'content': '거래를 원하시는군요. 무엇을 사고 싶으신가요?', 'personality': 'business', 'priority': 0},
                {'content': '상점에 오신 것을 환영합니다!', 'personality': 'welcoming', 'priority': 0},
                {'content': '좋은 물건들이 많이 있습니다.', 'personality': 'proud', 'priority': 0},
                {'content': '특별한 할인을 해드릴 수 있습니다.', 'personality': 'generous', 'priority': 0}
            ],
            'lore': [
                {'content': '아, 그 이야기를 알고 싶으시군요.', 'personality': 'wise', 'priority': 0},
                {'content': '오래된 이야기입니다만...', 'personality': 'mysterious', 'priority': 0},
                {'content': '이곳의 전설을 말씀드리겠습니다.', 'personality': 'storyteller', 'priority': 0},
                {'content': '비밀스러운 이야기인데...', 'personality': 'secretive', 'priority': 0}
            ],
            'quest': [
                {'content': '도움이 필요하신가요?', 'personality': 'helpful', 'priority': 0},
                {'content': '특별한 일이 있으시군요.', 'personality': 'observant', 'priority': 0},
                {'content': '제가 도울 수 있는 일이 있다면...', 'personality': 'generous', 'priority': 0},
                {'content': '위험한 일이지만 도와드리겠습니다.', 'personality': 'brave', 'priority': 0}
            ],
            'farewell': [
                {'content': '안녕히 가세요!', 'personality': 'polite', 'priority': 0},
                {'content': '또 만나요!', 'personality': 'friendly', 'priority': 0},
                {'content': '조심히 가세요!', 'personality': 'caring', 'priority': 0},
                {'content': '행운을 빕니다!', 'personality': 'blessing', 'priority': 0}
            ]
        }
        
        for category, templates in default_templates.items():
            if not self._template_cache.get(category):
                self._template_cache[category] = templates
    
    def _set_fallback_templates(self):
        """폴백 템플릿 설정"""
        self._template_cache = {
            'greeting': [{'content': '안녕하세요!', 'personality': 'neutral', 'priority': 0}],
            'trade': [{'content': '거래를 원하시는군요.', 'personality': 'neutral', 'priority': 0}],
            'lore': [{'content': '그 이야기를 알고 싶으시군요.', 'personality': 'neutral', 'priority': 0}],
            'quest': [{'content': '도움이 필요하신가요?', 'personality': 'neutral', 'priority': 0}],
            'farewell': [{'content': '안녕히 가세요!', 'personality': 'neutral', 'priority': 0}],
            'general': [{'content': '무엇을 도와드릴까요?', 'personality': 'neutral', 'priority': 0}]
        }
        self._cache_loaded = True
        logger.warning("Using fallback templates")
    
    async def get_template(self, category: str, personality: str = None, 
                          priority_filter: int = None) -> Optional[str]:
        """특정 카테고리의 템플릿 조회"""
        if not self._cache_loaded:
            await self.load_all_templates()
        
        templates = self._template_cache.get(category, [])
        if not templates:
            return None
        
        # 필터링된 템플릿 목록
        filtered_templates = templates
        
        if personality:
            filtered_templates = [t for t in filtered_templates if t.get('personality') == personality]
        
        if priority_filter is not None:
            filtered_templates = [t for t in filtered_templates if t.get('priority', 0) >= priority_filter]
        
        if not filtered_templates:
            # 필터링 결과가 없으면 원본 템플릿에서 선택
            filtered_templates = templates
        
        # 랜덤 선택
        template = random.choice(filtered_templates)
        return template['content']
    
    async def get_templates_by_category(self, category: str) -> List[Dict[str, Any]]:
        """카테고리별 모든 템플릿 조회"""
        if not self._cache_loaded:
            await self.load_all_templates()
        
        return self._template_cache.get(category, [])
    
    async def get_random_template(self, category: str, personality: str = None) -> str:
        """랜덤 템플릿 조회"""
        template = await self.get_template(category, personality)
        return template or f"[{category} 템플릿을 찾을 수 없습니다]"
    
    async def add_template(self, category: str, content: str, personality: str = 'neutral', 
                          priority: int = 0, topics: Dict[str, Any] = None):
        """새로운 템플릿 추가"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                template_id = f"TEMPLATE_{category.upper()}_{len(self._template_cache.get(category, [])) + 1:03d}"
                
                await conn.execute("""
                    INSERT INTO game_data.dialogue_contexts 
                    (dialogue_id, title, content, entity_personality, priority, available_topics, is_active)
                    VALUES ($1, $2, $3, $4, $5, $6, TRUE)
                """, template_id, f"{category} Template", content, personality, priority, 
                json.dumps(topics or {}))
                
                # 캐시 업데이트
                if category not in self._template_cache:
                    self._template_cache[category] = []
                
                self._template_cache[category].append({
                    'content': content,
                    'personality': personality,
                    'priority': priority,
                    'topics': topics or {}
                })
                
                logger.info(f"Added template: {template_id}")
                
        except Exception as e:
            logger.error(f"Failed to add template: {str(e)}")
    
    async def update_template(self, template_id: str, content: str = None, 
                            personality: str = None, priority: int = None):
        """템플릿 업데이트"""
        try:
            pool = await self.db.pool
            async with pool.acquire() as conn:
                update_fields = []
                params = []
                param_count = 1
                
                if content is not None:
                    update_fields.append(f"content = ${param_count}")
                    params.append(content)
                    param_count += 1
                
                if personality is not None:
                    update_fields.append(f"entity_personality = ${param_count}")
                    params.append(personality)
                    param_count += 1
                
                if priority is not None:
                    update_fields.append(f"priority = ${param_count}")
                    params.append(priority)
                    param_count += 1
                
                if update_fields:
                    update_fields.append("updated_at = CURRENT_TIMESTAMP")
                    params.append(template_id)
                    
                    await conn.execute(f"""
                        UPDATE game_data.dialogue_contexts
                        SET {', '.join(update_fields)}
                        WHERE dialogue_id = ${param_count}
                    """, *params)
                    
                    logger.info(f"Updated template: {template_id}")
                
        except Exception as e:
            logger.error(f"Failed to update template {template_id}: {str(e)}")
    
    def get_cached_template(self, category: str, personality: str = None) -> Optional[str]:
        """캐시된 템플릿 조회 (동기)"""
        templates = self._template_cache.get(category, [])
        if not templates:
            return None
        
        if personality:
            filtered_templates = [t for t in templates if t.get('personality') == personality]
            if filtered_templates:
                template = random.choice(filtered_templates)
                return template['content']
        
        template = random.choice(templates)
        return template['content']
    
    def clear_cache(self):
        """캐시 초기화"""
        self._template_cache.clear()
        self._cache_loaded = False
        logger.info("Template cache cleared")


def parse_jsonb_data(data: Optional[Union[str, Dict[str, Any]]]) -> Dict[str, Any]:
    """JSONB 데이터 파싱"""
    if data is None:
        return {}
    if isinstance(data, dict):
        return data
    if isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return {}
    return {}
