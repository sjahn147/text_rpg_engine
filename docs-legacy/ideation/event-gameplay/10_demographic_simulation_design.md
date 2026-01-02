# 사회학적 인구통계학 시뮬레이션 설계서

> **문서 버전**: v1.0  
> **작성일**: 2025-10-21  
> **최종 수정**: 2025-10-21

## 📊 **프로젝트 개요**

**목표**: 몬테카를로 시뮬레이션을 통한 현실적인 인구통계학 변수 생성 시스템  
**핵심 철학**: 통계적 분포와 상관관계를 반영한 살아있는 사회 구현  
**기술적 접근**: 몬테카를로 시뮬레이션 + 사회학적 변수 모델링

---

## 🎯 **1. 사회학적 인구통계학 변수 시스템**

### **1.1 핵심 인구통계학 변수**
```python
class DemographicVariables:
    """인구통계학 변수 시스템"""
    
    def __init__(self):
        self.demographic_categories = {
            'age': {
                'distribution': 'normal',
                'mean': 35.0,
                'std': 15.0,
                'min': 0,
                'max': 100,
                'bins': [(0, 12, 'childhood'), (13, 19, 'adolescence'), 
                        (20, 35, 'young_adult'), (36, 55, 'middle_age'), 
                        (56, 100, 'old_age')]
            },
            'gender': {
                'distribution': 'categorical',
                'probabilities': {'male': 0.49, 'female': 0.49, 'non_binary': 0.02},
                'cultural_factors': True
            },
            'occupation': {
                'distribution': 'weighted_categorical',
                'categories': {
                    'unemployed': 0.05,
                    'student': 0.15,
                    'service': 0.25,
                    'professional': 0.20,
                    'manual_labor': 0.15,
                    'creative': 0.08,
                    'academic': 0.05,
                    'retired': 0.07
                },
                'age_correlation': True,
                'education_correlation': True
            },
            'religion': {
                'distribution': 'weighted_categorical',
                'categories': {
                    'none': 0.30,
                    'christian': 0.25,
                    'muslim': 0.15,
                    'buddhist': 0.10,
                    'hindu': 0.08,
                    'jewish': 0.05,
                    'other': 0.07
                },
                'cultural_factors': True,
                'family_inheritance': True
            },
            'education': {
                'distribution': 'ordinal',
                'levels': {
                    'no_formal': 0.05,
                    'elementary': 0.10,
                    'middle_school': 0.15,
                    'high_school': 0.30,
                    'college': 0.25,
                    'graduate': 0.15
                },
                'age_correlation': True,
                'socioeconomic_correlation': True
            },
            'socioeconomic_status': {
                'distribution': 'normal',
                'mean': 50.0,
                'std': 20.0,
                'min': 0,
                'max': 100,
                'occupation_correlation': True,
                'education_correlation': True
            }
        }
```

### **1.2 몬테카를로 시뮬레이션 엔진**
```python
class MonteCarloDemographicSimulator:
    """몬테카를로 인구통계학 시뮬레이터"""
    
    def __init__(self, demographic_vars: DemographicVariables):
        self.demographic_vars = demographic_vars
        self.correlation_matrix = self._build_correlation_matrix()
    
    def generate_population_sample(self, 
                                 population_size: int,
                                 cultural_context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """인구 표본 생성"""
        
        population = []
        
        for i in range(population_size):
            # 기본 변수들 생성
            individual = {}
            
            # 1. 나이 생성 (정규분포)
            age = self._generate_age()
            individual['age'] = age
            
            # 2. 성별 생성 (문화적 맥락 고려)
            gender = self._generate_gender(cultural_context)
            individual['gender'] = gender
            
            # 3. 교육 수준 생성 (나이와 상관관계)
            education = self._generate_education(age, cultural_context)
            individual['education'] = education
            
            # 4. 직업 생성 (나이, 교육, 성별과 상관관계)
            occupation = self._generate_occupation(age, education, gender, cultural_context)
            individual['occupation'] = occupation
            
            # 5. 종교 생성 (가족 상속, 문화적 맥락)
            religion = self._generate_religion(cultural_context)
            individual['religion'] = religion
            
            # 6. 사회경제적 지위 생성 (직업, 교육과 상관관계)
            socioeconomic_status = self._generate_socioeconomic_status(
                occupation, education, age
            )
            individual['socioeconomic_status'] = socioeconomic_status
            
            # 7. 파생 변수들 계산
            individual.update(self._calculate_derived_variables(individual))
            
            population.append(individual)
        
        return population
    
    def _generate_age(self) -> int:
        """나이 생성 (정규분포)"""
        age_config = self.demographic_vars.demographic_categories['age']
        
        # 정규분포에서 샘플링
        age = np.random.normal(age_config['mean'], age_config['std'])
        
        # 범위 제한
        age = max(age_config['min'], min(age_config['max'], age))
        
        return int(age)
    
    def _generate_gender(self, cultural_context: Dict[str, Any] = None) -> str:
        """성별 생성 (문화적 맥락 고려)"""
        gender_config = self.demographic_vars.demographic_categories['gender']
        
        # 기본 확률
        probabilities = gender_config['probabilities'].copy()
        
        # 문화적 맥락에 따른 조정
        if cultural_context and 'gender_bias' in cultural_context:
            bias = cultural_context['gender_bias']
            for gender, prob in probabilities.items():
                probabilities[gender] = prob * bias.get(gender, 1.0)
        
        # 정규화
        total_prob = sum(probabilities.values())
        for gender in probabilities:
            probabilities[gender] /= total_prob
        
        # 카테고리 분포에서 샘플링
        return np.random.choice(
            list(probabilities.keys()),
            p=list(probabilities.values())
        )
    
    def _generate_education(self, age: int, cultural_context: Dict[str, Any] = None) -> str:
        """교육 수준 생성 (나이와 상관관계)"""
        education_config = self.demographic_vars.demographic_categories['education']
        
        # 나이에 따른 교육 수준 조정
        age_education_modifier = self._calculate_age_education_modifier(age)
        
        # 기본 확률
        probabilities = education_config['levels'].copy()
        
        # 나이 기반 조정
        for level, prob in probabilities.items():
            probabilities[level] = prob * age_education_modifier.get(level, 1.0)
        
        # 정규화
        total_prob = sum(probabilities.values())
        for level in probabilities:
            probabilities[level] /= total_prob
        
        return np.random.choice(
            list(probabilities.keys()),
            p=list(probabilities.values())
        )
    
    def _generate_occupation(self, 
                           age: int, 
                           education: str, 
                           gender: str,
                           cultural_context: Dict[str, Any] = None) -> str:
        """직업 생성 (다중 상관관계)"""
        occupation_config = self.demographic_vars.demographic_categories['occupation']
        
        # 기본 확률
        probabilities = occupation_config['categories'].copy()
        
        # 나이 기반 조정
        age_modifier = self._calculate_age_occupation_modifier(age)
        for occupation, prob in probabilities.items():
            probabilities[occupation] = prob * age_modifier.get(occupation, 1.0)
        
        # 교육 수준 기반 조정
        education_modifier = self._calculate_education_occupation_modifier(education)
        for occupation, prob in probabilities.items():
            probabilities[occupation] = prob * education_modifier.get(occupation, 1.0)
        
        # 성별 기반 조정 (성별 고정관념)
        gender_modifier = self._calculate_gender_occupation_modifier(gender)
        for occupation, prob in probabilities.items():
            probabilities[occupation] = prob * gender_modifier.get(occupation, 1.0)
        
        # 정규화
        total_prob = sum(probabilities.values())
        for occupation in probabilities:
            probabilities[occupation] /= total_prob
        
        return np.random.choice(
            list(probabilities.keys()),
            p=list(probabilities.values())
        )
    
    def _generate_religion(self, cultural_context: Dict[str, Any] = None) -> str:
        """종교 생성 (문화적 맥락 고려)"""
        religion_config = self.demographic_vars.demographic_categories['religion']
        
        # 기본 확률
        probabilities = religion_config['categories'].copy()
        
        # 문화적 맥락에 따른 조정
        if cultural_context and 'religious_context' in cultural_context:
            context = cultural_context['religious_context']
            for religion, prob in probabilities.items():
                probabilities[religion] = prob * context.get(religion, 1.0)
        
        # 정규화
        total_prob = sum(probabilities.values())
        for religion in probabilities:
            probabilities[religion] /= total_prob
        
        return np.random.choice(
            list(probabilities.keys()),
            p=list(probabilities.values())
        )
    
    def _generate_socioeconomic_status(self, 
                                     occupation: str, 
                                     education: str, 
                                     age: int) -> float:
        """사회경제적 지위 생성 (다중 상관관계)"""
        base_status = 50.0  # 기본값
        
        # 직업 기반 조정
        occupation_modifier = self._get_occupation_ses_modifier(occupation)
        base_status += occupation_modifier
        
        # 교육 수준 기반 조정
        education_modifier = self._get_education_ses_modifier(education)
        base_status += education_modifier
        
        # 나이 기반 조정 (경력 효과)
        age_modifier = self._get_age_ses_modifier(age)
        base_status += age_modifier
        
        # 랜덤 노이즈 추가
        noise = np.random.normal(0, 10)
        base_status += noise
        
        # 범위 제한 (0-100)
        return max(0, min(100, base_status))
```

### **1.3 상관관계 매트릭스**
```python
class CorrelationMatrix:
    """상관관계 매트릭스"""
    
    def __init__(self):
        self.correlations = {
            'age_education': {
                'childhood': {'no_formal': 0.8, 'elementary': 0.2},
                'adolescence': {'middle_school': 0.6, 'high_school': 0.4},
                'young_adult': {'high_school': 0.4, 'college': 0.5, 'graduate': 0.1},
                'middle_age': {'high_school': 0.3, 'college': 0.4, 'graduate': 0.3},
                'old_age': {'high_school': 0.5, 'college': 0.3, 'graduate': 0.2}
            },
            'education_occupation': {
                'no_formal': {'unemployed': 0.4, 'manual_labor': 0.6},
                'elementary': {'unemployed': 0.3, 'manual_labor': 0.5, 'service': 0.2},
                'middle_school': {'service': 0.4, 'manual_labor': 0.4, 'professional': 0.2},
                'high_school': {'service': 0.3, 'professional': 0.4, 'creative': 0.3},
                'college': {'professional': 0.5, 'academic': 0.3, 'creative': 0.2},
                'graduate': {'academic': 0.6, 'professional': 0.4}
            },
            'gender_occupation': {
                'male': {'manual_labor': 1.5, 'professional': 1.2, 'service': 0.8},
                'female': {'service': 1.3, 'professional': 1.1, 'manual_labor': 0.7},
                'non_binary': {'creative': 1.5, 'academic': 1.2, 'professional': 1.0}
            },
            'occupation_ses': {
                'unemployed': -30,
                'student': -10,
                'service': 0,
                'professional': 20,
                'manual_labor': -5,
                'creative': 10,
                'academic': 15,
                'retired': 5
            },
            'education_ses': {
                'no_formal': -20,
                'elementary': -15,
                'middle_school': -10,
                'high_school': 0,
                'college': 15,
                'graduate': 25
            }
        }
```

---

## 🌍 **2. 문화적 맥락 시스템**

### **2.1 문화적 변수**
```python
class CulturalContext:
    """문화적 맥락 시스템"""
    
    def __init__(self):
        self.cultural_factors = {
            'region': {
                'western': {
                    'gender_bias': {'male': 1.0, 'female': 1.0, 'non_binary': 1.0},
                    'religious_context': {'christian': 1.2, 'none': 1.1, 'other': 0.8},
                    'education_emphasis': 1.2,
                    'occupation_diversity': 1.1
                },
                'eastern': {
                    'gender_bias': {'male': 1.1, 'female': 0.9, 'non_binary': 0.8},
                    'religious_context': {'buddhist': 1.3, 'none': 0.9, 'other': 0.7},
                    'education_emphasis': 1.3,
                    'occupation_diversity': 0.9
                },
                'middle_eastern': {
                    'gender_bias': {'male': 1.2, 'female': 0.8, 'non_binary': 0.5},
                    'religious_context': {'muslim': 1.5, 'christian': 1.0, 'none': 0.5},
                    'education_emphasis': 1.0,
                    'occupation_diversity': 0.8
                }
            },
            'urbanization': {
                'urban': {
                    'education_emphasis': 1.3,
                    'occupation_diversity': 1.2,
                    'religious_diversity': 1.1,
                    'gender_equality': 1.1
                },
                'rural': {
                    'education_emphasis': 0.8,
                    'occupation_diversity': 0.7,
                    'religious_diversity': 0.9,
                    'gender_equality': 0.9
                }
            },
            'historical_period': {
                'medieval': {
                    'education_emphasis': 0.3,
                    'occupation_diversity': 0.5,
                    'gender_equality': 0.3,
                    'religious_dominance': 1.5
                },
                'industrial': {
                    'education_emphasis': 0.8,
                    'occupation_diversity': 1.2,
                    'gender_equality': 0.6,
                    'religious_dominance': 0.8
                },
                'modern': {
                    'education_emphasis': 1.2,
                    'occupation_diversity': 1.3,
                    'gender_equality': 1.1,
                    'religious_dominance': 0.6
                }
            }
        }
```

### **2.2 지역별 인구 분포**
```python
class RegionalDemographics:
    """지역별 인구 분포"""
    
    def __init__(self):
        self.regional_profiles = {
            'rekrosta': {
                'population_size': 50000,
                'cultural_context': {
                    'region': 'western',
                    'urbanization': 'urban',
                    'historical_period': 'modern'
                },
                'demographic_characteristics': {
                    'age_distribution': {'mean': 38.0, 'std': 16.0},
                    'education_emphasis': 1.2,
                    'occupation_diversity': 1.1,
                    'religious_diversity': 1.0
                }
            },
            'rural_village': {
                'population_size': 2000,
                'cultural_context': {
                    'region': 'eastern',
                    'urbanization': 'rural',
                    'historical_period': 'modern'
                },
                'demographic_characteristics': {
                    'age_distribution': {'mean': 45.0, 'std': 18.0},
                    'education_emphasis': 0.8,
                    'occupation_diversity': 0.7,
                    'religious_diversity': 0.9
                }
            },
            'academic_city': {
                'population_size': 15000,
                'cultural_context': {
                    'region': 'western',
                    'urbanization': 'urban',
                    'historical_period': 'modern'
                },
                'demographic_characteristics': {
                    'age_distribution': {'mean': 32.0, 'std': 12.0},
                    'education_emphasis': 1.5,
                    'occupation_diversity': 1.3,
                    'religious_diversity': 1.2
                }
            }
        }
```

---

## 🎯 **3. 실제 구현 예시**

### **3.1 인구 생성 함수**
```python
async def generate_realistic_population(
    region_name: str,
    population_size: int,
    cultural_context: Dict[str, Any] = None
) -> List[Dict[str, Any]]:
    """현실적인 인구 생성"""
    
    # 지역별 설정 로드
    regional_config = RegionalDemographics().regional_profiles[region_name]
    
    # 문화적 맥락 설정
    if not cultural_context:
        cultural_context = regional_config['cultural_context']
    
    # 인구통계학 변수 설정
    demographic_vars = DemographicVariables()
    
    # 몬테카를로 시뮬레이터 초기화
    simulator = MonteCarloDemographicSimulator(demographic_vars)
    
    # 인구 생성
    population = simulator.generate_population_sample(
        population_size, cultural_context
    )
    
    # 지역별 특성 적용
    population = await apply_regional_characteristics(
        population, regional_config
    )
    
    return population

async def apply_regional_characteristics(
    population: List[Dict[str, Any]],
    regional_config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """지역별 특성 적용"""
    
    characteristics = regional_config['demographic_characteristics']
    
    for individual in population:
        # 교육 강조도 적용
        if characteristics['education_emphasis'] > 1.0:
            individual['education'] = await boost_education_level(
                individual['education'], characteristics['education_emphasis']
            )
        
        # 직업 다양성 적용
        if characteristics['occupation_diversity'] > 1.0:
            individual['occupation'] = await diversify_occupation(
                individual['occupation'], characteristics['occupation_diversity']
            )
        
        # 종교 다양성 적용
        if characteristics['religious_diversity'] > 1.0:
            individual['religion'] = await diversify_religion(
                individual['religion'], characteristics['religious_diversity']
            )
    
    return population
```

### **3.2 인구 통계 검증**
```python
class PopulationStatisticsValidator:
    """인구 통계 검증기"""
    
    def __init__(self):
        self.expected_distributions = {
            'age': {'mean': 35.0, 'std': 15.0, 'tolerance': 0.1},
            'gender': {'male': 0.49, 'female': 0.49, 'non_binary': 0.02, 'tolerance': 0.05},
            'education': {'college': 0.25, 'graduate': 0.15, 'tolerance': 0.1},
            'occupation': {'professional': 0.20, 'service': 0.25, 'tolerance': 0.1}
        }
    
    def validate_population(self, population: List[Dict[str, Any]]) -> Dict[str, Any]:
        """인구 통계 검증"""
        
        validation_results = {}
        
        # 나이 분포 검증
        ages = [individual['age'] for individual in population]
        age_mean = np.mean(ages)
        age_std = np.std(ages)
        
        expected_age = self.expected_distributions['age']
        age_valid = (
            abs(age_mean - expected_age['mean']) < expected_age['tolerance'] * expected_age['mean'] and
            abs(age_std - expected_age['std']) < expected_age['tolerance'] * expected_age['std']
        )
        
        validation_results['age'] = {
            'valid': age_valid,
            'actual_mean': age_mean,
            'expected_mean': expected_age['mean'],
            'actual_std': age_std,
            'expected_std': expected_age['std']
        }
        
        # 성별 분포 검증
        gender_counts = {}
        for individual in population:
            gender = individual['gender']
            gender_counts[gender] = gender_counts.get(gender, 0) + 1
        
        gender_proportions = {
            gender: count / len(population) 
            for gender, count in gender_counts.items()
        }
        
        expected_gender = self.expected_distributions['gender']
        gender_valid = all(
            abs(gender_proportions.get(gender, 0) - expected_gender[gender]) < expected_gender['tolerance']
            for gender in expected_gender.keys()
        )
        
        validation_results['gender'] = {
            'valid': gender_valid,
            'actual_proportions': gender_proportions,
            'expected_proportions': expected_gender
        }
        
        return validation_results
```

---

## 📊 **4. 데이터베이스 스키마 확장**

### **4.1 인구통계학 테이블**
```sql
-- 인구통계학 변수 테이블
CREATE TABLE game_data.demographic_variables (
    entity_id VARCHAR(50) PRIMARY KEY,
    age INTEGER CHECK (age >= 0 AND age <= 100),
    gender VARCHAR(20) CHECK (gender IN ('male', 'female', 'non_binary')),
    education VARCHAR(20) CHECK (education IN ('no_formal', 'elementary', 'middle_school', 'high_school', 'college', 'graduate')),
    occupation VARCHAR(30) CHECK (occupation IN ('unemployed', 'student', 'service', 'professional', 'manual_labor', 'creative', 'academic', 'retired')),
    religion VARCHAR(20) CHECK (religion IN ('none', 'christian', 'muslim', 'buddhist', 'hindu', 'jewish', 'other')),
    socioeconomic_status FLOAT CHECK (socioeconomic_status >= 0 AND socioeconomic_status <= 100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (entity_id) REFERENCES game_data.entities(entity_id) ON DELETE CASCADE
);

-- 상관관계 매트릭스 테이블
CREATE TABLE game_data.correlation_matrix (
    variable_a VARCHAR(30),
    variable_b VARCHAR(30),
    correlation_strength FLOAT,
    correlation_type VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (variable_a, variable_b)
);

-- 지역별 인구 프로필 테이블
CREATE TABLE game_data.regional_profiles (
    region_name VARCHAR(50) PRIMARY KEY,
    population_size INTEGER,
    cultural_context JSONB,
    demographic_characteristics JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **4.2 몬테카를로 시뮬레이션 결과 테이블**
```sql
-- 시뮬레이션 결과 테이블
CREATE TABLE runtime_data.simulation_results (
    simulation_id UUID PRIMARY KEY,
    region_name VARCHAR(50),
    population_size INTEGER,
    simulation_parameters JSONB,
    generated_population JSONB,
    validation_results JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인구 통계 검증 테이블
CREATE TABLE runtime_data.population_validation (
    validation_id UUID PRIMARY KEY,
    simulation_id UUID,
    variable_name VARCHAR(30),
    expected_value FLOAT,
    actual_value FLOAT,
    tolerance FLOAT,
    is_valid BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (simulation_id) REFERENCES runtime_data.simulation_results(simulation_id) ON DELETE CASCADE
);
```

---

## 🚀 **5. 구현 로드맵**

### **Phase 1: 기본 시스템 구현 (3주)**
- 인구통계학 변수 정의
- 기본 몬테카를로 시뮬레이터
- 단순한 상관관계 모델링

### **Phase 2: 문화적 맥락 추가 (4주)**
- 지역별 인구 프로필
- 문화적 변수 시스템
- 복잡한 상관관계 매트릭스

### **Phase 3: 검증 및 최적화 (3주)**
- 통계적 검증 시스템
- 성능 최적화
- 실제 데이터와의 비교

### **Phase 4: 통합 및 확장 (2주)**
- 기존 시스템과 통합
- 추가 변수 지원
- 고급 시뮬레이션 기능

---

## 📈 **6. 기대 효과**

### **6.1 현실성 향상**
- **통계적으로 유의미한 인구 분포**: 실제 인구 통계와 유사한 분포
- **상관관계 반영**: 나이-교육-직업-소득 간의 현실적 상관관계
- **문화적 다양성**: 지역별, 시대별 문화적 특성 반영

### **6.2 게임적 경험**
- **다양한 NPC**: 각기 다른 배경과 특성을 가진 NPC들
- **현실적인 상호작용**: 실제 사회와 유사한 관계 패턴
- **예측 불가능성**: 통계적 분포 내에서의 랜덤성

### **6.3 학술적 가치**
- **인구통계학 시뮬레이션**: 실제 인구 통계 검증
- **사회학적 연구**: 다양한 사회적 요인의 상호작용 분석
- **정책 시뮬레이션**: 인구 정책의 효과 예측

---

## 🎯 **7. 성공 지표**

### **7.1 통계적 지표**
- **분포 정확도**: 실제 인구 통계와 90% 이상 일치
- **상관관계 강도**: 예상 상관관계와 0.8 이상 일치
- **문화적 반영도**: 지역별 특성이 80% 이상 반영

### **7.2 기술적 지표**
- **생성 속도**: 10,000명 인구 1분 이내 생성
- **메모리 효율성**: 100,000명 인구 1GB 이내 처리
- **확장성**: 1,000,000명 인구 처리 가능

### **7.3 사용자 경험 지표**
- **다양성**: 95% 이상의 NPC가 고유한 특성 보유
- **현실성**: 사용자가 "현실적"이라고 평가하는 비율 80% 이상
- **몰입도**: 평균 플레이 시간 30% 증가

---

## 🎉 **결론**

**몬테카를로 시뮬레이션**을 통한 **사회학적 인구통계학 변수** 구현은:

1. **현실적인 인구 분포** 생성
2. **복잡한 상관관계** 모델링
3. **문화적 맥락** 반영
4. **통계적 검증** 가능

이를 통해 **진정으로 살아있는 사회**를 구현할 수 있습니다! 🧠✨

---

**문서 작성자**: RPG Engine Development Team  
**최종 검토**: 2025-10-21  
**다음 검토 예정**: 2025-11-21
