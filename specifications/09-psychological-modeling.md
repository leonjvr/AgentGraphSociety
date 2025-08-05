# Psychological Modeling Specification

## Overview

This document specifies the enhanced psychological modeling system for AgentGraphSociety, providing agents with realistic personality traits, cognitive biases, mental states, and decision-making processes.

## Core Psychological Components

### 1. Personality Model (Big Five)

The Big Five personality model provides a scientifically validated framework for personality:

```python
class PersonalityProfile:
    """
    Big Five personality traits affecting agent behavior.
    Each trait is on a 0-1 scale.
    """
    openness: float              # Creativity, curiosity, openness to new experiences
    conscientiousness: float     # Organization, dependability, self-discipline
    extraversion: float          # Sociability, assertiveness, positive emotions
    agreeableness: float         # Trust, altruism, cooperation
    neuroticism: float           # Emotional instability, anxiety, moodiness
    
    def get_behavioral_tendencies(self) -> Dict[str, float]:
        """Calculate behavioral tendencies from personality."""
        return {
            "risk_taking": self.openness * 0.6 + (1 - self.neuroticism) * 0.4,
            "social_seeking": self.extraversion * 0.8 + self.agreeableness * 0.2,
            "routine_preference": self.conscientiousness * 0.7 + (1 - self.openness) * 0.3,
            "stress_susceptibility": self.neuroticism * 0.8 + (1 - self.conscientiousness) * 0.2,
            "cooperation_tendency": self.agreeableness * 0.7 + self.conscientiousness * 0.3
        }
```

### 2. Values and Belief System

```python
class ValueSystem:
    """
    Agent's core values affecting decision-making priorities.
    """
    # Core life values (0-1 importance)
    values: Dict[str, float] = {
        "family": 0.8,           # Importance of family relationships
        "career": 0.7,           # Career advancement priority
        "wealth": 0.5,           # Material success
        "social_status": 0.6,    # Social recognition
        "personal_growth": 0.7,  # Self-improvement
        "security": 0.8,         # Safety and stability
        "adventure": 0.4,        # New experiences
        "altruism": 0.6,         # Helping others
        "tradition": 0.5,        # Cultural/family traditions
        "autonomy": 0.7          # Independence
    }
    
    # Belief dimensions
    political_leaning: float     # -1 (left) to 1 (right)
    religious_commitment: float  # 0-1
    environmental_concern: float # 0-1
    technology_adoption: float   # 0-1 (early adopter to resistant)
    
    def calculate_decision_weights(self, decision_context: str) -> Dict[str, float]:
        """Weight different factors based on values for specific decisions."""
        # Context-specific value applications
```

### 3. Cognitive Patterns

```python
class CognitiveProfile:
    """
    Cognitive biases and thinking patterns.
    """
    # Cognitive biases (0-1 strength)
    confirmation_bias: float      # Tendency to seek confirming information
    anchoring_bias: float         # Over-reliance on first information
    availability_bias: float      # Overweight recent/memorable events
    loss_aversion: float          # Losses hurt more than gains
    social_proof_sensitivity: float # Following others' behavior
    optimism_bias: float          # Overestimate positive outcomes
    
    # Thinking styles
    analytical_thinking: float    # Logic vs. intuition
    long_term_orientation: float  # Future vs. present focus
    detail_orientation: float     # Big picture vs. details
    
    # Learning parameters
    learning_rate: float          # How quickly beliefs update
    memory_decay: float           # How quickly experiences fade
    pattern_recognition: float    # Ability to identify patterns
```

### 4. Mental State Model

```python
class MentalState:
    """
    Dynamic mental health and well-being indicators.
    """
    # Well-being metrics (0-1)
    life_satisfaction: float
    self_esteem: float
    sense_of_purpose: float
    social_connectedness: float
    
    # Mental health indicators (0-1, higher = worse)
    stress_level: float
    anxiety_level: float
    depression_score: float
    burnout_level: float
    
    # Coping resources (0-1)
    resilience: float
    social_support: float
    coping_skills: float
    emotional_regulation: float
    
    def update_from_events(self, events: List[LifeEvent]):
        """Update mental state based on life events."""
        # Implementation of stress accumulation and recovery
```

## Behavioral Generation

### 1. Decision-Making Process

```python
class PsychologicalDecisionMaker:
    """
    Makes decisions incorporating personality, values, and mental state.
    """
    
    async def make_decision(self, 
                          options: List[DecisionOption],
                          context: DecisionContext) -> Decision:
        """
        Enhanced decision-making process.
        """
        # 1. Filter options by mental state
        viable_options = self._filter_by_mental_capacity(options)
        
        # 2. Apply personality influences
        personality_scores = self._apply_personality_bias(viable_options)
        
        # 3. Apply value alignment
        value_scores = self._calculate_value_alignment(viable_options)
        
        # 4. Apply cognitive biases
        biased_scores = self._apply_cognitive_biases(viable_options, personality_scores)
        
        # 5. Consider social influences
        social_scores = self._calculate_social_influence(viable_options)
        
        # 6. Combine all factors
        final_scores = self._integrate_all_factors(
            personality_scores,
            value_scores,
            biased_scores,
            social_scores
        )
        
        # 7. Add noise for realism
        final_scores = self._add_decision_noise(final_scores)
        
        return self._select_option(viable_options, final_scores)
```

### 2. Personality-Behavior Mapping

```python
# Personality → Behavior mappings

HIGH_OPENNESS_BEHAVIORS = {
    "try_new_restaurant": 0.8,
    "change_routine": 0.7,
    "explore_new_area": 0.9,
    "adopt_new_technology": 0.8,
    "question_traditions": 0.6
}

HIGH_CONSCIENTIOUSNESS_BEHAVIORS = {
    "maintain_schedule": 0.9,
    "plan_ahead": 0.8,
    "save_money": 0.7,
    "exercise_regularly": 0.7,
    "arrive_early": 0.8
}

HIGH_EXTRAVERSION_BEHAVIORS = {
    "initiate_conversation": 0.9,
    "attend_social_events": 0.8,
    "seek_group_activities": 0.7,
    "express_emotions": 0.8,
    "take_leadership": 0.6
}

HIGH_AGREEABLENESS_BEHAVIORS = {
    "help_others": 0.9,
    "avoid_conflict": 0.8,
    "share_resources": 0.7,
    "forgive_quickly": 0.8,
    "cooperate": 0.9
}

HIGH_NEUROTICISM_BEHAVIORS = {
    "worry_about_future": 0.8,
    "avoid_risks": 0.7,
    "seek_reassurance": 0.8,
    "ruminate_problems": 0.9,
    "emotional_reactions": 0.8
}
```

### 3. Emotional Dynamics

```python
class EmotionalSystem:
    """
    Advanced emotional modeling with personality influences.
    """
    
    def calculate_emotional_response(self, 
                                   event: Event,
                                   personality: PersonalityProfile,
                                   current_state: MentalState) -> EmotionalState:
        """
        Calculate emotional response based on personality and state.
        """
        base_response = self._get_base_emotional_response(event)
        
        # Personality modulation
        if personality.neuroticism > 0.7:
            base_response.intensity *= 1.5  # Stronger reactions
            base_response.duration *= 1.3   # Longer lasting
        
        if personality.extraversion > 0.7:
            base_response.expression_level *= 1.4  # More expressive
        
        # Mental state influence
        if current_state.stress_level > 0.8:
            base_response.negativity_bias *= 1.3
            
        return base_response
```

## Neo4j Integration

### 1. Psychological Node Properties

```cypher
(:Agent {
  // Existing properties...
  
  // Big Five Personality
  personality_openness: Float,
  personality_conscientiousness: Float,
  personality_extraversion: Float,
  personality_agreeableness: Float,
  personality_neuroticism: Float,
  
  // Values (stored as JSON)
  values: String,  // JSON of value system
  
  // Mental State
  stress_level: Float,
  life_satisfaction: Float,
  self_esteem: Float,
  
  // Cognitive traits
  risk_tolerance: Float,
  learning_rate: Float,
  cognitive_flexibility: Float
})
```

### 2. Psychological Influence Queries

```cypher
// Find agents with compatible personalities
MATCH (a:Agent {id: $agent_id}), (b:Agent)
WHERE abs(a.personality_extraversion - b.personality_extraversion) < 0.3
  AND abs(a.personality_openness - b.personality_openness) < 0.3
RETURN b, 
       distance(point({
         x: a.personality_openness, 
         y: a.personality_conscientiousness,
         z: a.personality_extraversion
       }), point({
         x: b.personality_openness,
         y: b.personality_conscientiousness,
         z: b.personality_extraversion
       })) as personality_distance
ORDER BY personality_distance
LIMIT 20
```

### 3. Stress Propagation

```cypher
// Model stress contagion through social network
MATCH (stressed:Agent)-[r:KNOWS|FAMILY|COLLEAGUE]-(connected:Agent)
WHERE stressed.stress_level > 0.8
  AND r.strength > 50
  AND r.last_interaction > datetime() - duration('P7D')
SET connected.stress_exposure = connected.stress_exposure + 
    (stressed.stress_level * r.strength / 100 * 0.3)
```

## Implementation Considerations

### 1. Personality Initialization

```python
def generate_personality_profile() -> PersonalityProfile:
    """
    Generate realistic personality profile with correlations.
    """
    # Some traits are correlated in real populations
    openness = np.random.beta(5, 5)  # Bell curve
    
    # Conscientiousness slightly negatively correlated with openness
    conscientiousness = np.clip(
        np.random.normal(0.5 - 0.2 * (openness - 0.5), 0.15), 
        0, 1
    )
    
    # Generate other traits with realistic distributions
    return PersonalityProfile(
        openness=openness,
        conscientiousness=conscientiousness,
        extraversion=np.random.beta(4, 6),  # Slightly introverted population
        agreeableness=np.random.beta(6, 4),  # Slightly agreeable population
        neuroticism=np.random.beta(5, 5)
    )
```

### 2. Behavioral Consistency

```python
class BehaviorConsistencyTracker:
    """
    Ensures agents behave consistently with their personality over time.
    """
    
    def validate_action(self, 
                       agent: Agent, 
                       proposed_action: Action) -> float:
        """
        Return probability that agent would take this action.
        """
        personality_fit = self._calculate_personality_fit(
            agent.personality, 
            proposed_action
        )
        
        historical_consistency = self._check_historical_patterns(
            agent.action_history,
            proposed_action
        )
        
        return personality_fit * 0.7 + historical_consistency * 0.3
```

### 3. Mental Health Dynamics

```python
class MentalHealthSimulator:
    """
    Simulates realistic mental health dynamics.
    """
    
    def update_mental_health(self, 
                           agent: Agent,
                           daily_events: List[Event],
                           social_support: float) -> MentalState:
        """
        Update mental health based on events and support.
        """
        stressors = sum(e.stress_value for e in daily_events if e.is_negative)
        positive_events = sum(e.joy_value for e in daily_events if e.is_positive)
        
        # Personality affects stress response
        stress_vulnerability = agent.personality.neuroticism * 1.5
        resilience_factor = agent.personality.conscientiousness * 0.8 + \
                          (1 - agent.personality.neuroticism) * 0.2
        
        # Calculate new stress level
        new_stress = agent.mental_state.stress_level + \
                    (stressors * stress_vulnerability) - \
                    (positive_events * resilience_factor) - \
                    (social_support * 0.3)
        
        # Bounded with recovery
        new_stress = max(0, min(1, new_stress * 0.95))  # Natural recovery
        
        return agent.mental_state.with_updates(stress_level=new_stress)
```

## Testing and Validation

### 1. Personality Consistency Tests
- Verify behavioral patterns match personality profiles
- Test decision consistency over time
- Validate against psychological research

### 2. Mental Health Realism
- Ensure stress accumulation is realistic
- Test recovery mechanisms
- Validate social support effects

### 3. Social Dynamics
- Test personality-based friend selection
- Verify emotional contagion
- Validate group dynamics