# 욘 엘스터 스타일 사회 시뮬레이션 엔진 설계서

> **문서 버전**: v1.0  
> **작성일**: 2025-10-21  
> **최종 수정**: 2025-10-21

## 🧠 **프로젝트 개요**

**목표**: 욘 엘스터의 행동사회학 이론을 기반으로 한 복합적 사회 시뮬레이션 엔진 구현  
**벤치마크**: 심즈 4 + 사회학적 메커니즘  
**핵심 철학**: 욕망-의도-행동-결과의 복합적 메커니즘을 통한 '살아있는 사회' 구현

---

## 🎯 **1. 이론적 기반: 욘 엘스터의 행동 메커니즘**

### **1.1 핵심 개념 정의**

#### **욕망(Desire) 시스템**
```python
class DesireSystem:
    """욕망 시스템 - 행동의 근본 동기"""
    
    def __init__(self):
        self.desire_categories = {
            'basic_needs': {
                'hunger': {'intensity': 0.0, 'decay_rate': 0.01},
                'thirst': {'intensity': 0.0, 'decay_rate': 0.015},
                'sleep': {'intensity': 0.0, 'decay_rate': 0.005},
                'safety': {'intensity': 0.0, 'decay_rate': 0.002}
            },
            'social_needs': {
                'belonging': {'intensity': 0.0, 'decay_rate': 0.003},
                'recognition': {'intensity': 0.0, 'decay_rate': 0.004},
                'intimacy': {'intensity': 0.0, 'decay_rate': 0.002},
                'power': {'intensity': 0.0, 'decay_rate': 0.001}
            },
            'self_actualization': {
                'creativity': {'intensity': 0.0, 'decay_rate': 0.001},
                'knowledge': {'intensity': 0.0, 'decay_rate': 0.0005},
                'achievement': {'intensity': 0.0, 'decay_rate': 0.002},
                'meaning': {'intensity': 0.0, 'decay_rate': 0.0001}
            }
        }
    
    def calculate_desire_intensity(self, entity_id: str, current_state: Dict) -> Dict[str, float]:
        """현재 상태에 따른 욕망 강도 계산"""
        intensities = {}
        
        for category, desires in self.desire_categories.items():
            for desire, config in desires.items():
                # 기본 강도 + 현재 상태 영향
                base_intensity = config['intensity']
                state_modifier = self._calculate_state_modifier(desire, current_state)
                intensities[desire] = base_intensity + state_modifier
        
        return intensities
```

#### **신념(Belief) 시스템**
```python
class BeliefSystem:
    """신념 시스템 - 행동의 인지적 근거"""
    
    def __init__(self):
        self.belief_types = {
            'factual_beliefs': {
                'world_knowledge': {},  # 세계에 대한 지식
                'social_norms': {},     # 사회적 규범
                'causal_relations': {}  # 인과관계에 대한 믿음
            },
            'evaluative_beliefs': {
                'value_hierarchy': {},  # 가치 위계
                'moral_principles': {}, # 도덕적 원칙
                'aesthetic_preferences': {} # 미적 선호
            },
            'instrumental_beliefs': {
                'efficacy_beliefs': {}, # 효능감
                'control_beliefs': {},  # 통제감
                'expectation_beliefs': {} # 기대감
            }
        }
    
    def evaluate_action_feasibility(self, 
                                  action: str, 
                                  entity_beliefs: Dict,
                                  environmental_context: Dict) -> float:
        """행동의 실행 가능성 평가 (0.0-1.0)"""
        
        # 1. 기술적 가능성 (도구, 능력, 지식)
        technical_feasibility = self._assess_technical_capability(action, entity_beliefs)
        
        # 2. 사회적 가능성 (규범, 허용성, 기대)
        social_feasibility = self._assess_social_acceptability(action, entity_beliefs, environmental_context)
        
        # 3. 심리적 가능성 (의지, 동기, 두려움)
        psychological_feasibility = self._assess_psychological_readiness(action, entity_beliefs)
        
        # 4. 물리적 가능성 (환경, 자원, 제약)
        physical_feasibility = self._assess_physical_constraints(action, environmental_context)
        
        # 가중 평균으로 최종 가능성 계산
        total_feasibility = (
            technical_feasibility * 0.3 +
            social_feasibility * 0.25 +
            psychological_feasibility * 0.25 +
            physical_feasibility * 0.2
        )
        
        return min(1.0, max(0.0, total_feasibility))
```

### **1.2 의도(Intention) 형성 메커니즘**

#### **합리적 선택 모델**
```python
class RationalChoiceModel:
    """합리적 선택 모델 - 욘 엘스터 스타일"""
    
    def __init__(self):
        self.decision_factors = {
            'expected_utility': 0.4,      # 기대 효용
            'cost_benefit_ratio': 0.3,   # 비용-편익 비율
            'social_pressure': 0.2,       # 사회적 압력
            'emotional_factor': 0.1       # 감정적 요인
        }
    
    async def form_intention(self, 
                           entity_id: str,
                           available_actions: List[str],
                           current_desires: Dict[str, float],
                           beliefs: Dict[str, Any],
                           social_context: Dict[str, Any]) -> Dict[str, Any]:
        """의도 형성 과정"""
        
        intention_scores = {}
        
        for action in available_actions:
            # 1. 기대 효용 계산
            expected_utility = await self._calculate_expected_utility(
                action, current_desires, beliefs
            )
            
            # 2. 비용-편익 분석
            cost_benefit = await self._analyze_cost_benefit(
                action, entity_id, social_context
            )
            
            # 3. 사회적 압력 평가
            social_pressure = await self._evaluate_social_pressure(
                action, social_context
            )
            
            # 4. 감정적 요인
            emotional_factor = await self._calculate_emotional_factor(
                action, entity_id
            )
            
            # 최종 의도 점수 계산
            intention_score = (
                expected_utility * self.decision_factors['expected_utility'] +
                cost_benefit * self.decision_factors['cost_benefit_ratio'] +
                social_pressure * self.decision_factors['social_pressure'] +
                emotional_factor * self.decision_factors['emotional_factor']
            )
            
            intention_scores[action] = {
                'score': intention_score,
                'expected_utility': expected_utility,
                'cost_benefit': cost_benefit,
                'social_pressure': social_pressure,
                'emotional_factor': emotional_factor
            }
        
        # 가장 높은 점수의 행동을 의도로 선택
        best_action = max(intention_scores.keys(), 
                         key=lambda x: intention_scores[x]['score'])
        
        return {
            'intended_action': best_action,
            'intention_strength': intention_scores[best_action]['score'],
            'all_scores': intention_scores,
            'decision_process': intention_scores[best_action]
        }
```

### **1.3 행동(Action) 실행 메커니즘**

#### **행동 시퀀스 생성**
```python
class ActionExecutionSystem:
    """행동 실행 시스템"""
    
    def __init__(self):
        self.action_phases = {
            'preparation': 0.1,    # 준비 단계
            'initiation': 0.2,     # 시작 단계
            'execution': 0.5,       # 실행 단계
            'completion': 0.2       # 완료 단계
        }
    
    async def execute_action(self, 
                           intention: Dict[str, Any],
                           entity_capabilities: Dict[str, float],
                           environmental_constraints: Dict[str, Any]) -> Dict[str, Any]:
        """의도를 실제 행동으로 변환"""
        
        action_type = intention['intended_action']
        intention_strength = intention['intention_strength']
        
        # 행동 시퀀스 생성
        action_sequence = await self._generate_action_sequence(
            action_type, intention_strength, entity_capabilities
        )
        
        # 각 단계별 성공 확률 계산
        success_probabilities = []
        for phase, sequence in action_sequence.items():
            phase_prob = await self._calculate_phase_success_probability(
                phase, sequence, entity_capabilities, environmental_constraints
            )
            success_probabilities.append(phase_prob)
        
        # 전체 성공 확률 (연쇄 확률)
        total_success_prob = 1.0
        for prob in success_probabilities:
            total_success_prob *= prob
        
        return {
            'action_sequence': action_sequence,
            'phase_probabilities': success_probabilities,
            'total_success_probability': total_success_prob,
            'execution_plan': await self._create_execution_plan(
                action_sequence, success_probabilities
            )
        }
```

### **1.4 결과(Outcome) 및 합리화(Rationalization)**

#### **결과 평가 시스템**
```python
class OutcomeEvaluationSystem:
    """결과 평가 및 합리화 시스템"""
    
    def __init__(self):
        self.evaluation_criteria = {
            'objective_success': 0.3,    # 객관적 성공
            'subjective_satisfaction': 0.3,  # 주관적 만족
            'social_approval': 0.2,     # 사회적 승인
            'long_term_benefit': 0.2    # 장기적 이익
        }
    
    async def evaluate_outcome(self, 
                             intended_action: str,
                             actual_result: Dict[str, Any],
                             entity_expectations: Dict[str, Any],
                             social_feedback: Dict[str, Any]) -> Dict[str, Any]:
        """행동 결과 평가"""
        
        # 1. 객관적 성공도 평가
        objective_success = await self._evaluate_objective_success(
            intended_action, actual_result
        )
        
        # 2. 주관적 만족도 평가
        subjective_satisfaction = await self._evaluate_subjective_satisfaction(
            actual_result, entity_expectations
        )
        
        # 3. 사회적 승인도 평가
        social_approval = await self._evaluate_social_approval(
            actual_result, social_feedback
        )
        
        # 4. 장기적 이익 평가
        long_term_benefit = await self._evaluate_long_term_benefit(
            actual_result, intended_action
        )
        
        # 종합 평가 점수
        total_score = (
            objective_success * self.evaluation_criteria['objective_success'] +
            subjective_satisfaction * self.evaluation_criteria['subjective_satisfaction'] +
            social_approval * self.evaluation_criteria['social_approval'] +
            long_term_benefit * self.evaluation_criteria['long_term_benefit']
        )
        
        return {
            'total_score': total_score,
            'objective_success': objective_success,
            'subjective_satisfaction': subjective_satisfaction,
            'social_approval': social_approval,
            'long_term_benefit': long_term_benefit,
            'evaluation_breakdown': {
                'objective': objective_success,
                'subjective': subjective_satisfaction,
                'social': social_approval,
                'long_term': long_term_benefit
            }
        }
    
    async def rationalize_outcome(self, 
                                evaluation: Dict[str, Any],
                                entity_beliefs: Dict[str, Any],
                                cognitive_biases: List[str]) -> Dict[str, Any]:
        """결과 합리화 과정"""
        
        # 인지적 편향에 따른 결과 해석
        rationalized_interpretation = {}
        
        for bias in cognitive_biases:
            if bias == 'confirmation_bias':
                # 확인 편향: 기존 신념과 일치하는 정보만 수용
                rationalized_interpretation[bias] = await self._apply_confirmation_bias(
                    evaluation, entity_beliefs
                )
            elif bias == 'self_serving_bias':
                # 자기중심적 편향: 성공은 내 덕, 실패는 외부 요인
                rationalized_interpretation[bias] = await self._apply_self_serving_bias(
                    evaluation
                )
            elif bias == 'hindsight_bias':
                # 후견 편향: 결과를 예측 가능했다고 믿음
                rationalized_interpretation[bias] = await self._apply_hindsight_bias(
                    evaluation
                )
        
        return {
            'original_evaluation': evaluation,
            'rationalized_interpretation': rationalized_interpretation,
            'belief_updates': await self._calculate_belief_updates(
                evaluation, rationalized_interpretation, entity_beliefs
            )
        }
```

---

## 🏠 **2. 심즈 4 벤치마크 분석**

### **2.1 심즈 4의 핵심 메커니즘**

#### **욕구 시스템 (Needs System)**
```python
class Sims4StyleNeedsSystem:
    """심즈 4 스타일 욕구 시스템"""
    
    def __init__(self):
        self.needs = {
            'hunger': {'current': 50, 'decay_rate': 0.5, 'priority': 0.8},
            'hygiene': {'current': 50, 'decay_rate': 0.3, 'priority': 0.6},
            'bladder': {'current': 50, 'decay_rate': 0.4, 'priority': 0.9},
            'energy': {'current': 50, 'decay_rate': 0.2, 'priority': 0.7},
            'fun': {'current': 50, 'decay_rate': 0.1, 'priority': 0.4},
            'social': {'current': 50, 'decay_rate': 0.15, 'priority': 0.5},
            'comfort': {'current': 50, 'decay_rate': 0.1, 'priority': 0.3},
            'environment': {'current': 50, 'decay_rate': 0.05, 'priority': 0.2}
        }
    
    def calculate_need_priority(self) -> str:
        """가장 시급한 욕구 계산"""
        urgent_needs = []
        for need, data in self.needs.items():
            if data['current'] < 30:  # 위험 수준
                urgent_needs.append((need, data['priority'] * (30 - data['current'])))
        
        if urgent_needs:
            return max(urgent_needs, key=lambda x: x[1])[0]
        return None
```

#### **행동 큐 시스템**
```python
class Sims4StyleActionQueue:
    """심즈 4 스타일 행동 큐"""
    
    def __init__(self):
        self.action_queue = []
        self.max_queue_size = 5
        self.current_action = None
    
    def add_action(self, action: str, priority: int = 0):
        """행동을 큐에 추가"""
        if len(self.action_queue) < self.max_queue_size:
            self.action_queue.append({
                'action': action,
                'priority': priority,
                'added_time': time.time()
            })
            # 우선순위에 따라 정렬
            self.action_queue.sort(key=lambda x: x['priority'], reverse=True)
    
    def get_next_action(self) -> Optional[str]:
        """다음 행동 가져오기"""
        if self.action_queue:
            return self.action_queue.pop(0)['action']
        return None
```

### **2.2 심즈 4의 한계점과 개선 방향**

#### **한계점**
1. **단순한 욕구 시스템**: 기본적인 생리적 욕구만 고려
2. **제한된 사회적 상호작용**: 표면적인 관계만 모델링
3. **인지적 복잡성 부족**: 복잡한 의사결정 과정 부재
4. **장기적 목표 부재**: 단기적 욕구 충족에만 집중

#### **개선 방향**
1. **다층적 욕망 시스템**: 생리적 → 사회적 → 자아실현 욕구
2. **복합적 의사결정**: 합리적 선택 + 감정적 요인 + 사회적 압력
3. **인지적 편향 모델링**: 실제 인간의 비합리적 행동 패턴
4. **장기적 목표 추구**: 인생 목표, 가치관, 의미 추구

---

## 🧬 **3. 복합적 사회 시뮬레이션 엔진 설계**

### **3.1 엔티티 생명주기 시스템**

#### **발달 단계별 특성**
```python
class LifeStageSystem:
    """생애주기 시스템"""
    
    def __init__(self):
        self.life_stages = {
            'childhood': {
                'age_range': (0, 12),
                'primary_needs': ['safety', 'belonging', 'play'],
                'cognitive_development': 0.3,
                'social_learning': 0.8,
                'autonomy': 0.2
            },
            'adolescence': {
                'age_range': (13, 19),
                'primary_needs': ['identity', 'peer_acceptance', 'independence'],
                'cognitive_development': 0.7,
                'social_learning': 0.9,
                'autonomy': 0.6
            },
            'young_adult': {
                'age_range': (20, 35),
                'primary_needs': ['intimacy', 'career', 'achievement'],
                'cognitive_development': 0.9,
                'social_learning': 0.7,
                'autonomy': 0.8
            },
            'middle_age': {
                'age_range': (36, 55),
                'primary_needs': ['generativity', 'stability', 'meaning'],
                'cognitive_development': 0.8,
                'social_learning': 0.5,
                'autonomy': 0.9
            },
            'old_age': {
                'age_range': (56, 100),
                'primary_needs': ['integrity', 'wisdom', 'legacy'],
                'cognitive_development': 0.6,
                'social_learning': 0.3,
                'autonomy': 0.7
            }
        }
    
    def get_stage_characteristics(self, age: int) -> Dict[str, Any]:
        """나이에 따른 발달 단계 특성 반환"""
        for stage, characteristics in self.life_stages.items():
            if characteristics['age_range'][0] <= age <= characteristics['age_range'][1]:
                return characteristics
        return self.life_stages['old_age']  # 기본값
```

### **3.2 사회적 관계 네트워크**

#### **관계의 복잡성 모델링**
```python
class SocialRelationshipNetwork:
    """사회적 관계 네트워크"""
    
    def __init__(self):
        self.relationship_types = {
            'family': {
                'bond_strength': 0.9,
                'obligation_level': 0.8,
                'conflict_potential': 0.6,
                'support_capacity': 0.9
            },
            'friendship': {
                'bond_strength': 0.7,
                'obligation_level': 0.4,
                'conflict_potential': 0.3,
                'support_capacity': 0.7
            },
            'romantic': {
                'bond_strength': 0.8,
                'obligation_level': 0.7,
                'conflict_potential': 0.8,
                'support_capacity': 0.8
            },
            'professional': {
                'bond_strength': 0.4,
                'obligation_level': 0.6,
                'conflict_potential': 0.5,
                'support_capacity': 0.3
            },
            'acquaintance': {
                'bond_strength': 0.2,
                'obligation_level': 0.1,
                'conflict_potential': 0.2,
                'support_capacity': 0.2
            }
        }
    
    def calculate_relationship_dynamics(self, 
                                       entity_a: str, 
                                       entity_b: str,
                                       relationship_type: str) -> Dict[str, Any]:
        """관계 역학 계산"""
        
        base_characteristics = self.relationship_types[relationship_type]
        
        # 개인적 특성에 따른 관계 조정
        personality_compatibility = await self._calculate_personality_compatibility(
            entity_a, entity_b
        )
        
        # 공유 경험에 따른 관계 강화
        shared_experiences = await self._calculate_shared_experiences(
            entity_a, entity_b
        )
        
        # 시간에 따른 관계 변화
        relationship_duration = await self._get_relationship_duration(
            entity_a, entity_b
        )
        
        # 최종 관계 특성 계산
        final_characteristics = {}
        for key, value in base_characteristics.items():
            final_characteristics[key] = value * personality_compatibility * shared_experiences
        
        return {
            'relationship_type': relationship_type,
            'characteristics': final_characteristics,
            'compatibility': personality_compatibility,
            'shared_experiences': shared_experiences,
            'duration': relationship_duration
        }
```

### **3.3 관계 개념도 및 호감도 시스템**

#### **관계 개념도 (Relationship Concept Map)**
```python
class RelationshipConceptMap:
    """관계 개념도 시스템"""
    
    def __init__(self):
        self.relationship_dimensions = {
            'emotional_bond': {
                'range': (-1.0, 1.0),
                'description': '감정적 유대감',
                'factors': ['trust', 'intimacy', 'affection']
            },
            'social_distance': {
                'range': (0.0, 1.0),
                'description': '사회적 거리감',
                'factors': ['formality', 'hierarchy', 'familiarity']
            },
            'power_dynamics': {
                'range': (-1.0, 1.0),
                'description': '권력 역학',
                'factors': ['influence', 'control', 'dependence']
            },
            'mutual_benefit': {
                'range': (0.0, 1.0),
                'description': '상호 이익',
                'factors': ['cooperation', 'competition', 'symbiosis']
            }
        }
    
    def calculate_relationship_vector(self, 
                                   entity_a: str, 
                                   entity_b: str) -> Dict[str, float]:
        """관계 벡터 계산"""
        relationship_vector = {}
        
        for dimension, config in self.relationship_dimensions.items():
            # 각 차원별 점수 계산
            score = await self._calculate_dimension_score(
                dimension, entity_a, entity_b
            )
            
            # 범위 내로 제한
            min_val, max_val = config['range']
            relationship_vector[dimension] = max(min_val, min(max_val, score))
        
        return relationship_vector
    
    def get_relationship_type(self, relationship_vector: Dict[str, float]) -> str:
        """관계 벡터를 기반으로 관계 타입 결정"""
        
        emotional_bond = relationship_vector['emotional_bond']
        social_distance = relationship_vector['social_distance']
        power_dynamics = relationship_vector['power_dynamics']
        mutual_benefit = relationship_vector['mutual_benefit']
        
        # 관계 타입 분류 로직
        if emotional_bond > 0.7 and social_distance < 0.3:
            return 'intimate_friend'
        elif emotional_bond > 0.5 and social_distance < 0.5:
            return 'close_friend'
        elif emotional_bond > 0.3 and social_distance < 0.7:
            return 'friend'
        elif social_distance > 0.7:
            return 'stranger'
        elif power_dynamics > 0.5:
            return 'hierarchical'
        elif mutual_benefit > 0.7:
            return 'professional'
        else:
            return 'acquaintance'
```

#### **호감도 시스템 (Affinity System)**
```python
class AffinitySystem:
    """호감도 시스템"""
    
    def __init__(self):
        self.affinity_factors = {
            'personality_compatibility': 0.3,
            'shared_interests': 0.2,
            'shared_experiences': 0.2,
            'mutual_benefit': 0.15,
            'physical_attraction': 0.1,
            'social_status': 0.05
        }
    
    def calculate_affinity(self, 
                          entity_a: str, 
                          entity_b: str,
                          context: Dict[str, Any]) -> Dict[str, Any]:
        """호감도 계산"""
        
        affinity_scores = {}
        total_affinity = 0.0
        
        for factor, weight in self.affinity_factors.items():
            score = await self._calculate_factor_score(
                factor, entity_a, entity_b, context
            )
            affinity_scores[factor] = score
            total_affinity += score * weight
        
        # 호감도 레벨 결정
        affinity_level = self._determine_affinity_level(total_affinity)
        
        return {
            'total_affinity': total_affinity,
            'affinity_level': affinity_level,
            'factor_scores': affinity_scores,
            'relationship_potential': await self._calculate_relationship_potential(
                total_affinity, context
            )
        }
    
    def _determine_affinity_level(self, total_affinity: float) -> str:
        """호감도 레벨 결정"""
        if total_affinity >= 0.8:
            return 'strong_positive'
        elif total_affinity >= 0.6:
            return 'positive'
        elif total_affinity >= 0.4:
            return 'neutral_positive'
        elif total_affinity >= 0.2:
            return 'neutral'
        elif total_affinity >= 0.0:
            return 'neutral_negative'
        elif total_affinity >= -0.2:
            return 'negative'
        else:
            return 'strong_negative'
```

### **3.4 문화적/제도적 맥락**

#### **사회적 규범 시스템**
```python
class CulturalNormSystem:
    """문화적 규범 시스템"""
    
    def __init__(self):
        self.norm_categories = {
            'moral_norms': {
                'honesty': {'strength': 0.8, 'violation_cost': 0.7},
                'fairness': {'strength': 0.9, 'violation_cost': 0.8},
                'loyalty': {'strength': 0.7, 'violation_cost': 0.6}
            },
            'social_norms': {
                'politeness': {'strength': 0.6, 'violation_cost': 0.4},
                'punctuality': {'strength': 0.5, 'violation_cost': 0.3},
                'dress_code': {'strength': 0.4, 'violation_cost': 0.2}
            },
            'institutional_norms': {
                'legal_compliance': {'strength': 0.9, 'violation_cost': 0.9},
                'professional_ethics': {'strength': 0.7, 'violation_cost': 0.6},
                'academic_integrity': {'strength': 0.8, 'violation_cost': 0.7}
            }
        }
    
    def evaluate_norm_violation(self, 
                              action: str,
                              entity_id: str,
                              social_context: Dict[str, Any]) -> Dict[str, Any]:
        """규범 위반 평가"""
        
        violation_scores = {}
        total_violation_cost = 0
        
        for category, norms in self.norm_categories.items():
            category_violation = 0
            for norm, config in norms.items():
                if await self._is_norm_violation(action, norm):
                    violation_cost = config['strength'] * config['violation_cost']
                    category_violation += violation_cost
                    total_violation_cost += violation_cost
            
            violation_scores[category] = category_violation
        
        # 사회적 맥락에 따른 위반 비용 조정
        context_modifier = await self._calculate_context_modifier(
            social_context, entity_id
        )
        
        adjusted_violation_cost = total_violation_cost * context_modifier
        
        return {
            'total_violation_cost': adjusted_violation_cost,
            'category_violations': violation_scores,
            'context_modifier': context_modifier,
            'social_consequences': await self._predict_social_consequences(
                adjusted_violation_cost, social_context
            )
        }
```

---

## 🎮 **4. 다양한 행동 지원 ActionHandler**

### **4.1 확장된 행동 타입 시스템**

#### **행동 카테고리 정의**
```python
class ExtendedActionType(str, Enum):
    """확장된 행동 타입 열거형"""
    
    # 기본 생존 행동
    EAT = "eat"
    DRINK = "drink"
    SLEEP = "sleep"
    REST = "rest"
    HYGIENE = "hygiene"
    
    # 사회적 행동
    GREET = "greet"
    CONVERSE = "converse"
    FLIRT = "flirt"
    ARGUE = "argue"
    APOLOGIZE = "apologize"
    COMPLIMENT = "compliment"
    INSULT = "insult"
    GOSSIP = "gossip"
    
    # 작업/생산 행동
    WORK = "work"
    STUDY = "study"
    CREATE = "create"
    REPAIR = "repair"
    CLEAN = "clean"
    COOK = "cook"
    GARDEN = "garden"
    
    # 여가/오락 행동
    PLAY = "play"
    READ = "read"
    LISTEN_MUSIC = "listen_music"
    WATCH_TV = "watch_tv"
    EXERCISE = "exercise"
    MEDITATE = "meditate"
    PRAY = "pray"
    
    # 이동/탐험 행동
    WALK = "walk"
    RUN = "run"
    TRAVEL = "travel"
    EXPLORE = "explore"
    VISIT = "visit"
    SHOP = "shop"
    
    # 감정적 행동
    CRY = "cry"
    LAUGH = "laugh"
    ANGRY = "angry"
    WORRY = "worry"
    CELEBRATE = "celebrate"
    MOURN = "mourn"
    
    # 복합적 행동
    ROMANCE = "romance"
    PARENT = "parent"
    MENTOR = "mentor"
    LEAD = "lead"
    FOLLOW = "follow"
    REBEL = "rebel"
```

### **4.2 행동별 세부 메커니즘**

#### **사회적 행동 처리**
```python
class SocialActionHandler:
    """사회적 행동 처리기"""
    
    def __init__(self, relationship_network: SocialRelationshipNetwork,
                 affinity_system: AffinitySystem):
        self.relationship_network = relationship_network
        self.affinity_system = affinity_system
    
    async def handle_greet(self, 
                          actor_id: str, 
                          target_id: str,
                          context: Dict[str, Any]) -> ActionResult:
        """인사 행동 처리"""
        
        # 현재 관계 상태 확인
        current_relationship = await self.relationship_network.get_relationship(
            actor_id, target_id
        )
        
        # 인사 방식 결정 (공식적/비공식적)
        greeting_style = await self._determine_greeting_style(
            current_relationship, context
        )
        
        # 인사 성공 확률 계산
        success_probability = await self._calculate_greeting_success_probability(
            actor_id, target_id, greeting_style, context
        )
        
        # 인사 실행
        success = random.random() < success_probability
        
        if success:
            # 관계 개선
            relationship_improvement = await self._calculate_relationship_improvement(
                'greet', current_relationship
            )
            
            await self.relationship_network.update_relationship(
                actor_id, target_id, relationship_improvement
            )
            
            return ActionResult.success_result(
                f"인사가 성공적으로 이루어졌습니다.",
                data={
                    'greeting_style': greeting_style,
                    'relationship_improvement': relationship_improvement
                }
            )
        else:
            return ActionResult.failure_result(
                f"인사가 어색하게 끝났습니다.",
                data={'greeting_style': greeting_style}
            )
    
    async def handle_flirt(self, 
                          actor_id: str, 
                          target_id: str,
                          context: Dict[str, Any]) -> ActionResult:
        """유혹 행동 처리"""
        
        # 현재 호감도 확인
        affinity = await self.affinity_system.calculate_affinity(
            actor_id, target_id, context
        )
        
        # 유혹 성공 확률 (호감도 기반)
        flirt_success_prob = affinity['total_affinity'] * 0.5 + 0.3
        
        # 사회적 맥락 고려
        social_context_modifier = await self._calculate_social_context_modifier(
            'flirt', context
        )
        
        final_success_prob = flirt_success_prob * social_context_modifier
        
        success = random.random() < final_success_prob
        
        if success:
            # 호감도 증가
            affinity_boost = await self._calculate_affinity_boost(
                'flirt', affinity
            )
            
            return ActionResult.success_result(
                f"유혹이 성공했습니다!",
                data={
                    'affinity_boost': affinity_boost,
                    'new_affinity': affinity['total_affinity'] + affinity_boost
                }
            )
        else:
            # 호감도 감소 가능성
            affinity_penalty = await self._calculate_affinity_penalty(
                'flirt_failure', affinity
            )
            
            return ActionResult.failure_result(
                f"유혹이 거절당했습니다.",
                data={'affinity_penalty': affinity_penalty}
            )
```

#### **감정적 행동 처리**
```python
class EmotionalActionHandler:
    """감정적 행동 처리기"""
    
    def __init__(self, emotion_system: EmotionSystem):
        self.emotion_system = emotion_system
    
    async def handle_cry(self, 
                        actor_id: str, 
                        context: Dict[str, Any]) -> ActionResult:
        """울음 행동 처리"""
        
        # 현재 감정 상태 확인
        current_emotions = await self.emotion_system.get_current_emotions(actor_id)
        
        # 울음 트리거 확인
        cry_triggers = await self._identify_cry_triggers(current_emotions, context)
        
        if cry_triggers:
            # 울음 강도 결정
            cry_intensity = await self._calculate_cry_intensity(
                cry_triggers, current_emotions
            )
            
            # 감정적 해방 효과
            emotional_release = await self._calculate_emotional_release(
                cry_intensity
            )
            
            # 주변 사람들의 반응
            social_reactions = await self._calculate_social_reactions(
                actor_id, 'cry', context
            )
            
            return ActionResult.success_result(
                f"울음으로 감정적 해방을 느꼈습니다.",
                data={
                    'cry_intensity': cry_intensity,
                    'emotional_release': emotional_release,
                    'social_reactions': social_reactions
                }
            )
        else:
            return ActionResult.failure_result(
                "울고 싶은 감정이 없습니다."
            )
    
    async def handle_celebrate(self, 
                              actor_id: str, 
                              context: Dict[str, Any]) -> ActionResult:
        """축하 행동 처리"""
        
        # 축하할 이유 확인
        celebration_reasons = await self._identify_celebration_reasons(
            actor_id, context
        )
        
        if celebration_reasons:
            # 축하 강도 결정
            celebration_intensity = await self._calculate_celebration_intensity(
                celebration_reasons
            )
            
            # 기분 개선 효과
            mood_boost = await self._calculate_mood_boost(
                celebration_intensity
            )
            
            # 사회적 공유 효과
            social_sharing = await self._calculate_social_sharing_effect(
                actor_id, 'celebrate', context
            )
            
            return ActionResult.success_result(
                f"축하의 시간을 가졌습니다!",
                data={
                    'celebration_intensity': celebration_intensity,
                    'mood_boost': mood_boost,
                    'social_sharing': social_sharing
                }
            )
        else:
            return ActionResult.failure_result(
                "축하할 특별한 이유가 없습니다."
            )
```

### **4.3 복합적 행동 처리**

#### **로맨스 행동 처리**
```python
class RomanceActionHandler:
    """로맨스 행동 처리기"""
    
    def __init__(self, relationship_network: SocialRelationshipNetwork,
                 affinity_system: AffinitySystem,
                 emotion_system: EmotionSystem):
        self.relationship_network = relationship_network
        self.affinity_system = affinity_system
        self.emotion_system = emotion_system
    
    async def handle_romance(self, 
                           actor_id: str, 
                           target_id: str,
                           romance_type: str,
                           context: Dict[str, Any]) -> ActionResult:
        """로맨스 행동 처리"""
        
        # 현재 관계 상태 확인
        current_relationship = await self.relationship_network.get_relationship(
            actor_id, target_id
        )
        
        # 로맨스 타입별 처리
        if romance_type == 'confess':
            return await self._handle_confession(actor_id, target_id, context)
        elif romance_type == 'date':
            return await self._handle_date(actor_id, target_id, context)
        elif romance_type == 'kiss':
            return await self._handle_kiss(actor_id, target_id, context)
        elif romance_type == 'propose':
            return await self._handle_proposal(actor_id, target_id, context)
        else:
            return ActionResult.failure_result("알 수 없는 로맨스 행동입니다.")
    
    async def _handle_confession(self, 
                                actor_id: str, 
                                target_id: str,
                                context: Dict[str, Any]) -> ActionResult:
        """고백 행동 처리"""
        
        # 현재 호감도 확인
        affinity = await self.affinity_system.calculate_affinity(
            actor_id, target_id, context
        )
        
        # 고백 성공 확률 계산
        confession_success_prob = await self._calculate_confession_success_probability(
            affinity, context
        )
        
        success = random.random() < confession_success_prob
        
        if success:
            # 관계 업그레이드
            relationship_upgrade = await self._calculate_relationship_upgrade(
                'confession_success', affinity
            )
            
            await self.relationship_network.update_relationship(
                actor_id, target_id, relationship_upgrade
            )
            
            return ActionResult.success_result(
                "고백이 받아들여졌습니다!",
                data={
                    'relationship_upgrade': relationship_upgrade,
                    'new_relationship_type': 'romantic'
                }
            )
        else:
            # 관계 악화 가능성
            relationship_damage = await self._calculate_relationship_damage(
                'confession_rejection', affinity
            )
            
            return ActionResult.failure_result(
                "고백이 거절당했습니다.",
                data={'relationship_damage': relationship_damage}
            )
```

---

## 🎯 **5. 구현 로드맵**

### **Phase 1: 핵심 메커니즘 구현 (4주)**
- 욕망-신념-의도-행동-결과 파이프라인
- 기본적인 합리적 선택 모델
- 단순한 사회적 상호작용
- 기본 행동 타입 20개 구현

### **Phase 2: 복합성 추가 (6주)**
- 인지적 편향 시스템
- 복잡한 사회적 관계 네트워크
- 문화적/제도적 맥락
- 확장된 행동 타입 50개 구현

### **Phase 3: 고급 시뮬레이션 (8주)**
- 생애주기별 발달 과정
- 장기적 목표 추구 시스템
- 사회적 학습 및 적응
- 복합적 행동 100개 구현

### **Phase 4: 통합 및 최적화 (4주)**
- 전체 시스템 통합
- 성능 최적화
- 사용자 인터페이스
- 최종 행동 타입 200개 구현

---

## 🚀 **6. 기대 효과**

### **6.1 기술적 혁신**
- **복합적 의사결정**: 단순한 IF-THEN이 아닌 다차원적 판단
- **사회적 학습**: 경험을 통한 행동 패턴 진화
- **예측 불가능성**: 진정한 에이전시를 가진 NPC

### **6.2 게임적 경험**
- **살아있는 사회**: 플레이어 없이도 돌아가는 복잡한 사회
- **의미 있는 선택**: 모든 행동이 장기적 결과를 가짐
- **감정적 몰입**: NPC들의 복잡한 내면 세계

### **6.3 학술적 가치**
- **행동사회학 시뮬레이션**: 이론을 검증할 수 있는 실험실
- **인공사회 연구**: 복잡계 이론의 실증적 검토
- **인간 행동 모델링**: AI 연구에 활용 가능한 프레임워크

---

## 📊 **7. 성공 지표**

### **7.1 기술적 지표**
- **시스템 복잡도**: 100개 이상의 상호작용 변수
- **행동 다양성**: 200가지 이상의 고유한 행동 패턴
- **사회적 안정성**: 100일 이상 지속되는 안정적 사회

### **7.2 사용자 경험 지표**
- **몰입도**: 평균 플레이 시간 2시간 이상
- **예측 불가능성**: 90% 이상의 행동이 예측 불가능
- **감정적 반응**: 사용자의 감정적 몰입도 측정

---

## 🎉 **결론**

이 시스템은 **"디지털 사회학 실험실"**이자 **"살아있는 사회 시뮬레이터"**입니다. 욘 엘스터의 이론적 기반 위에 심즈 4의 접근성을 결합하여, **진정으로 복잡하고 예측 불가능한 사회**를 구현할 수 있습니다.

이것이 바로 **"게임을 넘어선 사회 시뮬레이션 엔진"**의 모습입니다! 🧠✨

---

**문서 작성자**: RPG Engine Development Team  
**최종 검토**: 2025-10-21  
**다음 검토 예정**: 2025-11-21
