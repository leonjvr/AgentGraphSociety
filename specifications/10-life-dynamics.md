# Life Dynamics Specification

## Overview

This document specifies the life dynamics system for AgentGraphSociety, enabling agents to experience realistic life stages, major events, career progression, family dynamics, and long-term goal pursuit.

## Life Stage Model

### 1. Core Life Stages

```python
class LifeStage(Enum):
    """
    Major life stages with typical age ranges and characteristics.
    """
    CHILDHOOD = "childhood"           # 0-17
    YOUNG_ADULT = "young_adult"       # 18-25  
    EARLY_CAREER = "early_career"     # 23-35
    ESTABLISHED = "established"       # 30-50
    MID_LIFE = "mid_life"            # 40-60
    PRE_RETIREMENT = "pre_retirement" # 55-65
    RETIREMENT = "retirement"         # 65+
    ELDERLY = "elderly"               # 75+

class LifeStageProfile:
    """
    Defines characteristics and priorities for each life stage.
    """
    stage: LifeStage
    typical_goals: List[LifeGoal]
    common_challenges: List[Challenge]
    social_priorities: Dict[str, float]
    economic_behavior: EconomicProfile
    time_allocation: Dict[str, float]  # How time is typically spent
```

### 2. Life Transitions

```python
class LifeTransition:
    """
    Manages transitions between life stages.
    """
    from_stage: LifeStage
    to_stage: LifeStage
    triggers: List[TransitionTrigger]  # Age, events, achievements
    duration: int  # Days for transition
    impacts: Dict[str, float]  # Changes to agent attributes
    
    def calculate_readiness(self, agent: Agent) -> float:
        """Calculate how ready agent is for transition."""
        age_factor = self._check_age_appropriateness(agent.age)
        goal_completion = self._check_goal_achievements(agent.goals)
        social_factors = self._check_social_readiness(agent.relationships)
        economic_factors = self._check_economic_readiness(agent.financial_state)
        
        return weighted_average([
            (age_factor, 0.3),
            (goal_completion, 0.3),
            (social_factors, 0.2),
            (economic_factors, 0.2)
        ])
```

## Life Events System

### 1. Event Categories

```python
class LifeEventCategory(Enum):
    # Personal
    HEALTH = "health"
    MENTAL_HEALTH = "mental_health"
    PERSONAL_ACHIEVEMENT = "personal_achievement"
    
    # Relationships
    ROMANTIC = "romantic"
    FAMILY = "family"
    FRIENDSHIP = "friendship"
    
    # Career
    EDUCATION = "education"
    CAREER = "career"
    FINANCIAL = "financial"
    
    # Life Changes
    RELOCATION = "relocation"
    LIFESTYLE = "lifestyle"
    LOSS = "loss"

class LifeEvent:
    """
    Represents a significant life event.
    """
    category: LifeEventCategory
    name: str
    description: str
    
    # Event characteristics
    probability_by_stage: Dict[LifeStage, float]
    prerequisites: List[Prerequisite]
    
    # Impacts
    immediate_effects: Dict[str, float]
    long_term_effects: Dict[str, float]
    relationship_impacts: Dict[RelationType, float]
    
    # Duration and processing
    duration_days: int
    processing_time: int  # How long effects last
    can_repeat: bool
    cooldown_days: int
```

### 2. Major Life Events

```python
# Relationship Events
MARRIAGE = LifeEvent(
    category=LifeEventCategory.ROMANTIC,
    name="marriage",
    prerequisites=[
        RelationshipStrength("romantic_partner", min=80),
        Age(min=20),
        FinancialStability(min=0.6)
    ],
    immediate_effects={
        "life_satisfaction": +0.3,
        "social_satisfaction": +0.4,
        "stress_level": +0.2,  # Wedding stress
        "financial_resources": -0.3  # Wedding costs
    },
    long_term_effects={
        "life_satisfaction": +0.2,
        "social_support": +0.3,
        "social_network_size": +0.2
    }
)

DIVORCE = LifeEvent(
    category=LifeEventCategory.ROMANTIC,
    name="divorce",
    prerequisites=[
        RelationshipStatus("married"),
        RelationshipStrength("spouse", max=30)
    ],
    immediate_effects={
        "life_satisfaction": -0.4,
        "stress_level": +0.6,
        "financial_resources": -0.4,
        "social_satisfaction": -0.3
    },
    long_term_effects={
        "trust_in_relationships": -0.2,
        "financial_stability": -0.2
    }
)

# Career Events
JOB_PROMOTION = LifeEvent(
    category=LifeEventCategory.CAREER,
    name="job_promotion",
    prerequisites=[
        EmploymentDuration(min_months=12),
        WorkPerformance(min=0.7),
        SkillLevel(min=0.6)
    ],
    immediate_effects={
        "income": +0.3,
        "career_satisfaction": +0.4,
        "self_esteem": +0.3,
        "work_stress": +0.2
    }
)

JOB_LOSS = LifeEvent(
    category=LifeEventCategory.CAREER,
    name="job_loss",
    immediate_effects={
        "income": -1.0,
        "self_esteem": -0.4,
        "stress_level": +0.7,
        "life_satisfaction": -0.3
    },
    long_term_effects={
        "career_confidence": -0.2,
        "financial_anxiety": +0.3
    }
)

# Family Events
CHILD_BIRTH = LifeEvent(
    category=LifeEventCategory.FAMILY,
    name="child_birth",
    prerequisites=[
        Age(min=20, max=45),
        RelationshipStatus(["married", "partnered"]),
        FinancialStability(min=0.5)
    ],
    immediate_effects={
        "life_satisfaction": +0.5,
        "family_satisfaction": +0.6,
        "sleep_quality": -0.6,
        "free_time": -0.7,
        "financial_pressure": +0.4
    },
    long_term_effects={
        "life_purpose": +0.4,
        "family_bonds": +0.5,
        "career_flexibility_need": +0.3
    }
)
```

### 3. Event Probability System

```python
class EventProbabilityCalculator:
    """
    Calculates probability of life events occurring.
    """
    
    def calculate_event_probability(self, 
                                  agent: Agent, 
                                  event: LifeEvent,
                                  context: SimulationContext) -> float:
        """
        Calculate probability of event occurring for agent.
        """
        # Base probability by life stage
        base_prob = event.probability_by_stage.get(agent.life_stage, 0.0)
        
        # Check prerequisites
        if not self._check_prerequisites(agent, event.prerequisites):
            return 0.0
        
        # Personality influence
        personality_modifier = self._personality_influence(agent.personality, event)
        
        # Social influence (events clustering in social networks)
        social_modifier = self._social_influence(agent, event)
        
        # Environmental factors
        environment_modifier = self._environmental_factors(context, event)
        
        # Recent events influence (avoid too many major events)
        recency_modifier = self._recent_events_dampening(agent.recent_events)
        
        final_probability = base_prob * personality_modifier * \
                          social_modifier * environment_modifier * \
                          recency_modifier
        
        return min(1.0, max(0.0, final_probability))
```

## Goals and Aspirations

### 1. Goal System

```python
class LifeGoal:
    """
    Represents a long-term life goal.
    """
    category: GoalCategory
    name: str
    description: str
    
    # Goal properties
    typical_age_range: Tuple[int, int]
    priority_by_personality: Dict[str, float]  # Personality trait → priority
    
    # Requirements
    sub_goals: List['LifeGoal']
    requirements: List[Requirement]
    typical_duration_years: float
    
    # Success factors
    success_criteria: List[Criterion]
    abandonment_triggers: List[Trigger]

class GoalCategory(Enum):
    CAREER = "career"
    FAMILY = "family"
    FINANCIAL = "financial"
    PERSONAL = "personal"
    SOCIAL = "social"
    EXPERIENTIAL = "experiential"

# Example Goals
BUY_HOUSE = LifeGoal(
    category=GoalCategory.FINANCIAL,
    name="buy_house",
    typical_age_range=(25, 40),
    requirements=[
        FinancialSavings(min=50000),
        StableIncome(months=24),
        CreditScore(min=650)
    ],
    priority_by_personality={
        "conscientiousness": 0.8,
        "security_value": 0.9,
        "family_value": 0.7
    }
)

START_FAMILY = LifeGoal(
    category=GoalCategory.FAMILY,
    name="start_family",
    typical_age_range=(25, 40),
    sub_goals=[
        FIND_PARTNER,
        ACHIEVE_FINANCIAL_STABILITY,
        FIND_SUITABLE_HOME
    ],
    priority_by_personality={
        "family_value": 0.95,
        "traditional_value": 0.8,
        "nurturing_trait": 0.85
    }
)
```

### 2. Goal Pursuit Behavior

```python
class GoalPursuitEngine:
    """
    Manages how agents pursue their life goals.
    """
    
    def update_goal_progress(self, agent: Agent, time_delta: int):
        """
        Update progress on all active goals.
        """
        for goal in agent.active_goals:
            # Calculate effort allocation
            effort = self._calculate_effort_allocation(agent, goal)
            
            # Apply personality-based pursuit strategy
            strategy = self._get_pursuit_strategy(agent.personality, goal)
            
            # Update progress
            progress = self._calculate_progress(goal, effort, strategy)
            goal.current_progress += progress
            
            # Check for completion or abandonment
            if goal.current_progress >= 1.0:
                self._handle_goal_completion(agent, goal)
            elif self._should_abandon_goal(agent, goal):
                self._handle_goal_abandonment(agent, goal)
    
    def select_new_goals(self, agent: Agent) -> List[LifeGoal]:
        """
        Select appropriate new goals based on life stage and personality.
        """
        candidate_goals = self._get_stage_appropriate_goals(agent.life_stage)
        
        # Filter by personality fit
        personality_aligned = [
            g for g in candidate_goals 
            if self._calculate_personality_fit(agent.personality, g) > 0.6
        ]
        
        # Consider social influence
        socially_influenced = self._apply_social_influence(
            agent, 
            personality_aligned
        )
        
        # Rank by multiple factors
        ranked_goals = self._rank_goals(
            agent,
            socially_influenced,
            factors=['personality_fit', 'social_pressure', 'feasibility']
        )
        
        return ranked_goals[:3]  # Top 3 goals
```

## Family Dynamics

### 1. Family Structure

```python
class FamilyUnit:
    """
    Represents a family unit with complex dynamics.
    """
    id: str
    members: List[int]  # Agent IDs
    
    # Family properties
    family_type: FamilyType  # Nuclear, extended, single-parent, etc.
    household_id: int
    
    # Dynamics
    cohesion_level: float  # 0-1, how close the family is
    conflict_level: float  # 0-1, current tension
    communication_style: CommunicationStyle
    
    # Shared resources
    shared_finances: bool
    financial_pool: float
    
    # Family culture
    values: Dict[str, float]
    traditions: List[Tradition]
    rules: List[FamilyRule]

class FamilyRole(Enum):
    PARENT = "parent"
    CHILD = "child"
    SPOUSE = "spouse"
    SIBLING = "sibling"
    GRANDPARENT = "grandparent"
    EXTENDED = "extended"
```

### 2. Family Lifecycle

```python
class FamilyLifecycle:
    """
    Manages family formation, evolution, and dissolution.
    """
    
    stages = [
        "FORMATION",      # Couple forms
        "EXPANSION",      # Children born
        "SCHOOL_AGE",     # Children in school
        "ADOLESCENCE",    # Teenage children
        "LAUNCHING",      # Children leave home
        "EMPTY_NEST",     # Couple alone again
        "RETIREMENT",     # Retirement phase
        "DISSOLUTION"     # Death or separation
    ]
    
    def update_family_stage(self, family: FamilyUnit):
        """
        Update family developmental stage based on member ages and events.
        """
        youngest_child_age = self._get_youngest_child_age(family)
        parent_ages = self._get_parent_ages(family)
        
        if youngest_child_age is None:
            if min(parent_ages) > 65:
                return "RETIREMENT"
            else:
                return "FORMATION"
        elif youngest_child_age < 5:
            return "EXPANSION"
        elif youngest_child_age < 12:
            return "SCHOOL_AGE"
        elif youngest_child_age < 18:
            return "ADOLESCENCE"
        elif youngest_child_age < 25:
            return "LAUNCHING"
        else:
            return "EMPTY_NEST"
```

## Career Progression

### 1. Career Path Model

```python
class CareerPath:
    """
    Defines possible career progressions.
    """
    field: CareerField
    levels: List[CareerLevel]
    
    # Progression requirements
    skill_requirements: Dict[str, List[float]]  # Skill → required levels
    experience_requirements: List[int]  # Years at each level
    
    # Career characteristics
    income_progression: List[float]
    work_life_balance: List[float]
    job_security: List[float]
    
    # Transitions
    lateral_moves: List[CareerField]  # Possible career changes
    specializations: List[Specialization]

class CareerLevel:
    """
    Represents a level within a career path.
    """
    title: str
    responsibilities: List[str]
    required_skills: Dict[str, float]
    typical_age_range: Tuple[int, int]
    
    # Work characteristics
    autonomy_level: float
    stress_level: float
    travel_requirement: float
    remote_work_possibility: float
```

### 2. Career Development

```python
class CareerDevelopmentEngine:
    """
    Manages agent career progression.
    """
    
    def evaluate_promotion_readiness(self, agent: Agent) -> float:
        """
        Evaluate if agent is ready for promotion.
        """
        skill_match = self._evaluate_skills(agent)
        performance = self._evaluate_performance(agent)
        tenure = self._evaluate_tenure(agent)
        network = self._evaluate_professional_network(agent)
        
        # Personality factors
        ambition = agent.personality.conscientiousness * 0.5 + \
                  agent.values.get("career", 0.5) * 0.5
        
        return weighted_average([
            (skill_match, 0.3),
            (performance, 0.3),
            (tenure, 0.2),
            (network, 0.1),
            (ambition, 0.1)
        ])
    
    def handle_career_transition(self, agent: Agent, transition: CareerTransition):
        """
        Process career transition effects.
        """
        # Update job attributes
        agent.career.level = transition.new_level
        agent.career.title = transition.new_title
        
        # Update income
        agent.financial.income = transition.new_income
        
        # Update work-life balance
        agent.time_allocation = self._recalculate_time_allocation(
            transition.new_responsibilities
        )
        
        # Psychological impacts
        if transition.is_promotion:
            agent.mental_state.self_esteem += 0.2
            agent.mental_state.stress_level += 0.1
        elif transition.is_lateral:
            agent.mental_state.stress_level += 0.2  # Change stress
        elif transition.is_demotion:
            agent.mental_state.self_esteem -= 0.3
            agent.mental_state.stress_level += 0.3
```

## Neo4j Integration

### 1. Life Event Nodes

```cypher
(:LifeEvent {
  id: String,
  agent_id: Integer,
  event_type: String,
  occurred_at: DateTime,
  life_stage: String,
  
  // Event details
  category: String,
  severity: Float,  // 0-1, how major the event is
  
  // Impacts
  immediate_impacts: String,  // JSON
  processed: Boolean,
  processing_complete_date: DateTime
})

// Relationships
(:Agent)-[:EXPERIENCED {
  impact_score: Float,
  recovery_time_days: Integer,
  changed_life_trajectory: Boolean
}]->(:LifeEvent)

(:LifeEvent)-[:TRIGGERED]->(:LifeEvent)  // Causal chains
(:LifeEvent)-[:INFLUENCED_BY]->(:Agent)  // Social influence
```

### 2. Family Relationship Enhancements

```cypher
// Enhanced FAMILY relationship
(:Agent)-[:FAMILY {
  role: String,  // "parent", "child", "spouse", "sibling"
  family_unit_id: String,
  
  // Family dynamics
  emotional_closeness: Float,
  communication_frequency: String,
  support_given: Float,
  support_received: Float,
  
  // History
  relationship_formed: DateTime,
  major_conflicts: Integer,
  shared_experiences: Integer
}]->(:Agent)
```

### 3. Career Network

```cypher
(:Agent)-[:MENTORS {
  since: DateTime,
  field: String,
  influence_on_career: Float
}]->(:Agent)

(:Agent)-[:PROFESSIONAL_NETWORK {
  context: String,  // How they met
  strength: Float,
  last_interaction: DateTime,
  mutual_benefit_score: Float
}]->(:Agent)
```

## Implementation Considerations

### 1. Life Stage Transitions

```python
def check_life_stage_transition(agent: Agent) -> Optional[LifeStage]:
    """
    Check if agent should transition to new life stage.
    """
    current_stage = agent.life_stage
    age = agent.age
    
    # Age-based transitions
    if current_stage == LifeStage.YOUNG_ADULT and age >= 30:
        if agent.career.established and agent.financial.stable:
            return LifeStage.ESTABLISHED
        else:
            return LifeStage.EARLY_CAREER
    
    # Goal-based transitions
    major_goals_completed = [
        g for g in agent.completed_goals 
        if g.category in [GoalCategory.CAREER, GoalCategory.FAMILY]
    ]
    
    if len(major_goals_completed) >= 3 and age >= 35:
        return LifeStage.MID_LIFE
    
    return None
```

### 2. Event Scheduling

```python
class LifeEventScheduler:
    """
    Schedules and manages life events.
    """
    
    def schedule_next_events(self, agent: Agent, time_horizon_days: int):
        """
        Schedule probable events for agent.
        """
        event_probabilities = {}
        
        # Calculate probabilities for all possible events
        for event_type in LifeEventCatalog.get_all():
            prob = self.event_calculator.calculate_probability(
                agent, 
                event_type
            )
            if prob > 0.01:  # Minimum threshold
                event_probabilities[event_type] = prob
        
        # Stochastic scheduling
        scheduled_events = []
        for day in range(time_horizon_days):
            for event_type, base_prob in event_probabilities.items():
                # Daily probability
                daily_prob = 1 - (1 - base_prob) ** (1/365)
                
                if random.random() < daily_prob:
                    scheduled_events.append(
                        ScheduledEvent(
                            event_type=event_type,
                            scheduled_day=day,
                            probability=daily_prob
                        )
                    )
        
        return scheduled_events
```

### 3. Impact Propagation

```python
def propagate_life_event_impacts(agent: Agent, event: LifeEvent):
    """
    Propagate impacts of life event through agent's life.
    """
    # Immediate impacts
    for attribute, change in event.immediate_effects.items():
        current_value = getattr(agent, attribute)
        new_value = max(0, min(1, current_value + change))
        setattr(agent, attribute, new_value)
    
    # Relationship impacts
    if event.category in [LifeEventCategory.ROMANTIC, LifeEventCategory.FAMILY]:
        for rel_type, impact in event.relationship_impacts.items():
            affected_relationships = agent.get_relationships_by_type(rel_type)
            for rel in affected_relationships:
                rel.adjust_strength(impact)
    
    # Schedule long-term impacts
    for attribute, change in event.long_term_effects.items():
        agent.schedule_gradual_change(
            attribute=attribute,
            target_change=change,
            duration_days=event.processing_time
        )
    
    # Trigger related events
    triggered_events = event.get_triggered_events()
    for triggered in triggered_events:
        agent.event_queue.add_with_delay(triggered, random.randint(30, 180))
```