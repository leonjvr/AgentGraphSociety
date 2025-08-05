# Agent Class Modifications Specification

## Overview

This document specifies the modifications required to existing agent classes to integrate Neo4j graph database functionality and enhanced psychological/behavioral modeling while maintaining backward compatibility.

## Core Agent Base Class Changes

### 1. GraphAgentBase Class (New)

Create a new base class that extends the existing agent functionality with graph capabilities.

**File**: `agentsociety/agent/graph_agent_base.py`

```python
class GraphAgentBase(Agent):
    """Base class for graph-enabled agents with psychological modeling."""
    
    def __init__(self, *args, graph_client: Optional[Neo4jClient] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.graph_client = graph_client
        self._graph_node_id = None  # Neo4j node ID
        self._relationship_cache = {}  # Local cache for performance
        
        # Initialize psychological components
        self.personality_profile = None
        self.value_system = None
        self.cognitive_profile = None
        self.mental_state = None
        self.life_stage = None
        self.active_goals = []
        self.life_event_history = []
        
    async def init(self):
        """Enhanced initialization with graph sync and psychological setup."""
        await super().init()
        
        # Initialize psychological components
        await self._initialize_psychological_profile()
        await self._initialize_life_dynamics()
        
        if self.graph_client:
            await self._create_or_update_graph_node()
            await self._sync_relationships_to_graph()
            await self._sync_psychological_data_to_graph()
    
    async def _initialize_psychological_profile(self):
        """Initialize agent's psychological profile."""
        # Implementation details in section below
        
    async def _initialize_life_dynamics(self):
        """Initialize life stage, goals, and history."""
        # Implementation details in section below
        
    async def _create_or_update_graph_node(self):
        """Create or update agent node in Neo4j with psychological attributes."""
        # Implementation details in section below
        
    async def _sync_relationships_to_graph(self):
        """Sync existing relationships to graph."""
        # Implementation details in section below
        
    async def _sync_psychological_data_to_graph(self):
        """Sync psychological and life dynamics data to graph."""
        # Implementation details in section below
```

### 2. CitizenAgentBase Modifications

**File**: `agentsociety/agent/agent.py`

**Changes Required**:

1. **Inheritance Change**:
```python
# OLD
class CitizenAgentBase(Agent):

# NEW
class CitizenAgentBase(GraphAgentBase):
```

2. **Method Overrides**:
```python
async def send_message_to_agent(self, to_agent_id: int, content: str, type: str = "social"):
    """Enhanced with graph relationship updates."""
    # Call parent method
    await super().send_message_to_agent(to_agent_id, content, type)
    
    # Update graph relationship
    if self.graph_client:
        await self._update_graph_interaction(to_agent_id, type)

async def _update_graph_interaction(self, target_id: int, interaction_type: str):
    """Update relationship properties in graph after interaction."""
    await self.graph_client.update_relationship_interaction(
        self.id, 
        target_id,
        {
            "last_interaction": datetime.now(),
            "interaction_count": "interaction_count + 1"
        }
    )
```

## Psychological Modeling Implementation

### 1. PersonalityProfile Class

**File**: `agentsociety/agent/psychology/personality.py`

```python
from dataclasses import dataclass
from typing import Dict
import numpy as np

@dataclass
class PersonalityProfile:
    """Big Five personality traits."""
    openness: float              # 0-1: Creativity, curiosity
    conscientiousness: float     # 0-1: Organization, self-discipline
    extraversion: float          # 0-1: Sociability, assertiveness
    agreeableness: float         # 0-1: Trust, cooperation
    neuroticism: float           # 0-1: Emotional instability
    
    def get_behavioral_tendencies(self) -> Dict[str, float]:
        """Calculate behavioral tendencies from personality."""
        return {
            "risk_taking": self.openness * 0.6 + (1 - self.neuroticism) * 0.4,
            "social_seeking": self.extraversion * 0.8 + self.agreeableness * 0.2,
            "routine_preference": self.conscientiousness * 0.7 + (1 - self.openness) * 0.3,
            "stress_susceptibility": self.neuroticism * 0.8 + (1 - self.conscientiousness) * 0.2,
            "cooperation_tendency": self.agreeableness * 0.7 + self.conscientiousness * 0.3
        }
    
    @classmethod
    def generate_random(cls) -> 'PersonalityProfile':
        """Generate realistic personality with trait correlations."""
        # Some traits are correlated in real populations
        openness = np.random.beta(5, 5)
        
        # Conscientiousness slightly negatively correlated with openness
        conscientiousness = np.clip(
            np.random.normal(0.5 - 0.2 * (openness - 0.5), 0.15), 
            0, 1
        )
        
        return cls(
            openness=openness,
            conscientiousness=conscientiousness,
            extraversion=np.random.beta(4, 6),  # Slightly introverted population
            agreeableness=np.random.beta(6, 4),  # Slightly agreeable population
            neuroticism=np.random.beta(5, 5)
        )
```

### 2. ValueSystem and MentalState Classes

**File**: `agentsociety/agent/psychology/values.py`

```python
@dataclass
class ValueSystem:
    """Agent's core values affecting decision-making."""
    values: Dict[str, float] = field(default_factory=lambda: {
        "family": 0.8,
        "career": 0.7,
        "wealth": 0.5,
        "social_status": 0.6,
        "personal_growth": 0.7,
        "security": 0.8,
        "adventure": 0.4,
        "altruism": 0.6,
        "tradition": 0.5,
        "autonomy": 0.7
    })
    
    political_leaning: float = 0.0      # -1 to 1
    religious_commitment: float = 0.5    # 0-1
    environmental_concern: float = 0.6   # 0-1
    technology_adoption: float = 0.7     # 0-1

@dataclass
class MentalState:
    """Dynamic mental health and well-being."""
    # Well-being metrics (0-1)
    life_satisfaction: float = 0.7
    self_esteem: float = 0.7
    sense_of_purpose: float = 0.6
    social_connectedness: float = 0.6
    
    # Mental health indicators (0-1, higher = worse)
    stress_level: float = 0.3
    anxiety_level: float = 0.2
    depression_score: float = 0.1
    burnout_level: float = 0.2
    
    # Coping resources (0-1)
    resilience: float = 0.6
    social_support: float = 0.7
    coping_skills: float = 0.6
    emotional_regulation: float = 0.7
```

### 3. Life Dynamics Classes

**File**: `agentsociety/agent/psychology/life_dynamics.py`

```python
from enum import Enum

class LifeStage(Enum):
    """Major life stages."""
    CHILDHOOD = "childhood"           # 0-17
    YOUNG_ADULT = "young_adult"       # 18-25  
    EARLY_CAREER = "early_career"     # 23-35
    ESTABLISHED = "established"       # 30-50
    MID_LIFE = "mid_life"            # 40-60
    PRE_RETIREMENT = "pre_retirement" # 55-65
    RETIREMENT = "retirement"         # 65+
    ELDERLY = "elderly"               # 75+

@dataclass
class LifeGoal:
    """Represents a long-term life goal."""
    id: str
    name: str
    category: str  # "career", "family", "financial", etc.
    priority: float  # 0-1
    progress: float  # 0-1
    status: str  # "active", "completed", "abandoned"
    
@dataclass
class LifeEvent:
    """Significant life event."""
    id: str
    event_type: str  # "marriage", "job_loss", etc.
    category: str  # "romantic", "career", "family"
    occurred_at: datetime
    severity: float  # 0-1
    immediate_impacts: Dict[str, float]
    processing_complete: bool = False
```

## SocietyAgent Modifications

**File**: `agentsociety/cityagent/societyagent.py`

### 1. Memory Attributes Changes

Add new psychological attributes to memory configuration:

```python
# In memory_config.py
# Add to citizen memory attributes:

# Psychological attributes
"personality_openness": MemoryAttribute(
    name="personality_openness",
    type=float,
    default_or_value=0.5,
    description="Big Five: Openness to experience",
    whether_embedding=True,
),
"personality_conscientiousness": MemoryAttribute(
    name="personality_conscientiousness",
    type=float,
    default_or_value=0.5,
    description="Big Five: Conscientiousness",
    whether_embedding=True,
),
"personality_extraversion": MemoryAttribute(
    name="personality_extraversion",
    type=float,
    default_or_value=0.5,
    description="Big Five: Extraversion",
    whether_embedding=True,
),
"personality_agreeableness": MemoryAttribute(
    name="personality_agreeableness",
    type=float,
    default_or_value=0.5,
    description="Big Five: Agreeableness",
    whether_embedding=True,
),
"personality_neuroticism": MemoryAttribute(
    name="personality_neuroticism",
    type=float,
    default_or_value=0.5,
    description="Big Five: Neuroticism",
    whether_embedding=True,
),

# Mental state attributes
"stress_level": MemoryAttribute(
    name="stress_level",
    type=float,
    default_or_value=0.3,
    description="Current stress level (0-1)",
    whether_embedding=False,
),
"life_satisfaction": MemoryAttribute(
    name="life_satisfaction",
    type=float,
    default_or_value=0.7,
    description="Overall life satisfaction (0-1)",
    whether_embedding=False,
),

# Life dynamics
"life_stage": MemoryAttribute(
    name="life_stage",
    type=str,
    default_or_value="young_adult",
    description="Current life stage",
    whether_embedding=True,
),
"active_goals": MemoryAttribute(
    name="active_goals",
    type=list,
    default_or_value=[],
    description="Current life goals",
    whether_embedding=False,
),
"life_events": MemoryAttribute(
    name="life_events",
    type=list,
    default_or_value=[],
    description="Significant life events history",
    whether_embedding=False,
),
```

### 2. New Methods

```python
class SocietyAgent(CitizenAgentBase):
    
    # Existing graph methods remain...
    
    async def get_friends_from_graph(self, 
                                    min_strength: float = 0,
                                    relationship_types: List[str] = None) -> List[Dict]:
        """Get friends from graph with filtering."""
        if not self.graph_client:
            # Fallback to memory-based friends
            return await self._get_friends_from_memory(min_strength, relationship_types)
        
        return await self.graph_client.get_agent_relationships(
            self.id,
            min_strength=min_strength,
            relationship_types=relationship_types
        )
    
    # New psychological methods
    
    async def make_decision(self, options: List[DecisionOption]) -> Decision:
        """Make decision incorporating personality and mental state."""
        # Get current mental state
        stress = await self.status.get("stress_level", 0.3)
        
        # Get personality traits
        openness = await self.status.get("personality_openness", 0.5)
        neuroticism = await self.status.get("personality_neuroticism", 0.5)
        
        # Filter options based on mental capacity
        if stress > 0.8:
            # High stress limits options
            options = [opt for opt in options if opt.complexity < 0.5]
        
        # Apply personality biases
        scored_options = []
        for option in options:
            score = option.base_score
            
            # Risk-averse if high neuroticism
            if option.risk_level > 0 and neuroticism > 0.7:
                score *= (1 - option.risk_level * 0.5)
            
            # Novelty seeking if high openness
            if option.novelty > 0 and openness > 0.7:
                score *= (1 + option.novelty * 0.3)
            
            scored_options.append((option, score))
        
        # Select best option
        best_option = max(scored_options, key=lambda x: x[1])
        return best_option[0]
    
    async def process_life_event(self, event: LifeEvent):
        """Process a life event and update agent state."""
        # Store event
        events = await self.status.get("life_events", [])
        events.append(event)
        await self.status.update("life_events", events)
        
        # Apply immediate impacts
        for attribute, change in event.immediate_impacts.items():
            current = await self.status.get(attribute, 0.5)
            new_value = max(0, min(1, current + change))
            await self.status.update(attribute, new_value)
        
        # Update graph
        if self.graph_client:
            await self.graph_client.create_life_event(
                agent_id=self.id,
                event_data=event
            )
    
    async def update_mental_health(self, daily_events: List[Event]):
        """Update mental health based on daily experiences."""
        # Get personality traits
        neuroticism = await self.status.get("personality_neuroticism", 0.5)
        resilience = await self.status.get("resilience", 0.6)
        
        # Calculate stress from events
        stressors = sum(e.stress_value for e in daily_events if e.is_negative)
        positive = sum(e.joy_value for e in daily_events if e.is_positive)
        
        # Personality affects stress response
        stress_vulnerability = neuroticism * 1.5
        
        # Update stress level
        current_stress = await self.status.get("stress_level", 0.3)
        new_stress = current_stress + (stressors * stress_vulnerability) - (positive * resilience)
        new_stress = max(0, min(1, new_stress * 0.95))  # Natural recovery
        
        await self.status.update("stress_level", new_stress)
    
    async def pursue_goals(self):
        """Update progress on active life goals."""
        goals = await self.status.get("active_goals", [])
        personality = await self._get_personality_profile()
        
        for goal in goals:
            # Calculate effort based on personality alignment
            effort = self._calculate_goal_effort(goal, personality)
            
            # Update progress
            goal.progress += effort * 0.01  # Daily progress
            
            # Check completion
            if goal.progress >= 1.0:
                await self._complete_goal(goal)
    
    async def _get_personality_profile(self) -> PersonalityProfile:
        """Get personality profile from memory."""
        return PersonalityProfile(
            openness=await self.status.get("personality_openness", 0.5),
            conscientiousness=await self.status.get("personality_conscientiousness", 0.5),
            extraversion=await self.status.get("personality_extraversion", 0.5),
            agreeableness=await self.status.get("personality_agreeableness", 0.5),
            neuroticism=await self.status.get("personality_neuroticism", 0.5)
        )
```

## Block Modifications

### 1. SocialBlock Changes

**File**: `agentsociety/cityagent/blocks/social_block.py`

#### FindPersonBlock Modifications

```python
class FindPersonBlock(Block):
    
    async def forward(self, context: DotDict):
        """Enhanced friend selection using graph queries."""
        try:
            # Try graph-based selection first
            if self.agent and self.agent.graph_client:
                target = await self._graph_based_selection(context)
                if target:
                    return self._create_success_result(target, "graph")
            
            # Fallback to original implementation
            return await self._memory_based_selection(context)
            
        except Exception as e:
            # Error handling
            
    async def _graph_based_selection(self, context) -> Optional[int]:
        """Select friend using graph queries and algorithms."""
        # Get current context
        current_emotion = await self.memory.status.get("emotion_types")
        current_location = await self.memory.status.get("position")
        
        # Query graph for best match
        query = """
        MATCH (me:Agent {id: $agent_id})-[r:KNOWS|FRIEND|FAMILY|COLLEAGUE]->(friend:Agent)
        WHERE friend.active = true
        WITH friend, r,
             r.strength * 
             CASE WHEN r.type = 'FAMILY' THEN 1.5 ELSE 1.0 END *
             CASE WHEN friend.emotion_state = $emotion THEN 1.2 ELSE 1.0 END *
             CASE WHEN distance(friend.current_location, $location) < 1000 THEN 1.3 ELSE 1.0 END
             as selection_score
        RETURN friend.id as target_id, selection_score
        ORDER BY selection_score DESC
        LIMIT 1
        """
        
        result = await self.agent.graph_client.query(query, {
            "agent_id": self.agent.id,
            "emotion": current_emotion,
            "location": current_location
        })
        
        return result[0]["target_id"] if result else None
```

#### MessageBlock Modifications

```python
class MessageBlock(Block):
    
    async def forward(self, context: DotDict):
        """Enhanced message generation with relationship context."""
        # Get target
        target = context.get("target")
        
        # Get relationship details from graph if available
        relationship_context = await self._get_relationship_context(target)
        
        # Generate message with enhanced context
        message = await self._generate_contextual_message(target, relationship_context)
        
        # Send message (existing logic)
        await self.agent.send_message(target, message)
        
        # Update graph relationships
        if self.agent.graph_client:
            await self._update_graph_after_message(target, message)
        
        return self._create_result(target, message)
    
    async def _get_relationship_context(self, target_id: int) -> Dict:
        """Get rich relationship context from graph."""
        if not self.agent.graph_client:
            # Fallback to memory
            relationships = await self.memory.status.get("relationships", {})
            return {
                "strength": relationships.get(target_id, 50),
                "type": "friend"
            }
        
        # Get from graph
        return await self.agent.graph_client.get_relationship_details(
            self.agent.id,
            target_id
        )
```

### 2. New Psychological Blocks

#### PersonalityInfluenceBlock (New)

```python
class PersonalityInfluenceBlock(Block):
    """Apply personality influences to agent decisions."""
    
    name = "PersonalityInfluenceBlock"
    description = "Personality-based decision modification"
    
    async def forward(self, context: DotDict):
        # Get personality profile
        personality = await self.agent._get_personality_profile()
        
        # Get decision context
        decision_type = context.get("decision_type", "general")
        options = context.get("options", [])
        
        # Apply personality filters
        filtered_options = []
        for option in options:
            # Extraversion affects social choices
            if decision_type == "social":
                if personality.extraversion < 0.3 and option.requires_social > 0.7:
                    continue  # Introverts avoid highly social options
            
            # Openness affects novelty
            if personality.openness < 0.3 and option.novelty > 0.7:
                continue  # Low openness avoids very novel options
            
            # Conscientiousness affects planning
            if decision_type == "planning":
                option.score *= (0.5 + personality.conscientiousness * 0.5)
            
            filtered_options.append(option)
        
        return {
            "success": True,
            "filtered_options": filtered_options,
            "personality_applied": True
        }
```

#### LifeEventTriggerBlock (New)

```python
class LifeEventTriggerBlock(Block):
    """Check and trigger life events based on agent state."""
    
    name = "LifeEventTriggerBlock"
    description = "Life event detection and triggering"
    
    async def forward(self, context: DotDict):
        # Get agent state
        age = await self.memory.profile.get("age")
        life_stage = await self.memory.status.get("life_stage")
        relationships = await self.memory.status.get("relationships", {})
        
        # Check for potential life events
        triggered_events = []
        
        # Marriage check
        if age > 25 and life_stage in ["young_adult", "early_career"]:
            romantic_partner = await self._find_romantic_partner(relationships)
            if romantic_partner and relationships.get(romantic_partner, 0) > 80:
                if random.random() < 0.01:  # 1% daily chance
                    event = LifeEvent(
                        id=f"marriage_{self.agent.id}_{romantic_partner}",
                        event_type="marriage",
                        category="romantic",
                        occurred_at=datetime.now(),
                        severity=0.8,
                        immediate_impacts={
                            "life_satisfaction": 0.3,
                            "stress_level": 0.2
                        }
                    )
                    triggered_events.append(event)
                    await self.agent.process_life_event(event)
        
        # Job change check
        stress = await self.memory.status.get("stress_level", 0.3)
        job_satisfaction = await self.memory.status.get("job_satisfaction", 0.7)
        if stress > 0.7 and job_satisfaction < 0.3:
            if random.random() < 0.005:  # 0.5% daily chance
                event = LifeEvent(
                    id=f"job_change_{self.agent.id}_{datetime.now()}",
                    event_type="job_change",
                    category="career",
                    occurred_at=datetime.now(),
                    severity=0.6,
                    immediate_impacts={
                        "stress_level": -0.2,
                        "income": 0.1,
                        "life_satisfaction": 0.1
                    }
                )
                triggered_events.append(event)
                await self.agent.process_life_event(event)
        
        return {
            "success": True,
            "triggered_events": triggered_events,
            "events_count": len(triggered_events)
        }
```

#### MentalHealthBlock (New)

```python
class MentalHealthBlock(Block):
    """Monitor and update agent mental health."""
    
    name = "MentalHealthBlock"
    description = "Mental health monitoring and intervention"
    
    async def forward(self, context: DotDict):
        # Get current mental state
        stress = await self.memory.status.get("stress_level", 0.3)
        life_satisfaction = await self.memory.status.get("life_satisfaction", 0.7)
        social_support = await self._calculate_social_support()
        
        # Check for interventions needed
        interventions = []
        
        if stress > 0.8:
            # High stress - need stress reduction
            interventions.append({
                "type": "stress_reduction",
                "priority": "high",
                "actions": ["seek_social_support", "reduce_workload", "relaxation"]
            })
        
        if life_satisfaction < 0.3:
            # Low satisfaction - need life changes
            interventions.append({
                "type": "life_improvement", 
                "priority": "medium",
                "actions": ["pursue_hobbies", "strengthen_relationships", "set_goals"]
            })
        
        # Apply coping strategies based on personality
        personality = await self.agent._get_personality_profile()
        coping_effectiveness = self._calculate_coping_effectiveness(
            personality, 
            social_support
        )
        
        # Update mental health
        if interventions:
            stress_reduction = 0.1 * coping_effectiveness
            new_stress = max(0, stress - stress_reduction)
            await self.memory.status.update("stress_level", new_stress)
        
        return {
            "success": True,
            "mental_health_status": {
                "stress": stress,
                "life_satisfaction": life_satisfaction,
                "social_support": social_support
            },
            "interventions": interventions
        }
```

### 3. New Graph-Aware Blocks

#### NetworkAnalysisBlock (New)

```python
class NetworkAnalysisBlock(Block):
    """Analyze agent's position in social network."""
    
    name = "NetworkAnalysisBlock"
    description = "Analyze social network position and influence"
    
    async def forward(self, context: DotDict):
        if not self.agent.graph_client:
            return {"success": False, "reason": "Graph not available"}
        
        # Calculate network metrics
        metrics = await self.agent.graph_client.calculate_network_metrics(
            self.agent.id
        )
        
        # Store in memory for other blocks
        await self.memory.status.update("network_metrics", metrics)
        
        return {
            "success": True,
            "metrics": metrics,
            "influence_score": metrics.get("pagerank", 0),
            "community_id": metrics.get("community", None)
        }
```

#### InfluencePropagationBlock (New)

```python
class InfluencePropagationBlock(Block):
    """Propagate influence through social network."""
    
    name = "InfluencePropagationBlock"
    description = "Spread information or influence through network"
    
    async def forward(self, context: DotDict):
        message = context.get("influence_message")
        max_hops = context.get("max_hops", 2)
        
        if not self.agent.graph_client:
            # Fallback to direct friends only
            friends = await self.memory.status.get("friends", [])
            return await self._direct_influence(friends, message)
        
        # Graph-based influence propagation
        influenced = await self.agent.graph_client.propagate_influence(
            source_id=self.agent.id,
            message=message,
            max_hops=max_hops,
            decay_factor=0.7
        )
        
        return {
            "success": True,
            "influenced_agents": influenced,
            "reach": len(influenced)
        }
```

## Configuration Changes

### 1. Agent Configuration

**File**: `agentsociety/configs/agent.py`

```python
class AgentConfig(BaseModel):
    # Existing fields...
    
    # Graph configuration
    enable_graph: bool = Field(default=False, description="Enable Neo4j graph features")
    graph_sync_interval: int = Field(default=300, description="Seconds between graph syncs")
    graph_cache_ttl: int = Field(default=60, description="Graph cache TTL in seconds")
    
    # Graph behavior
    use_graph_for_social: bool = Field(default=True, description="Use graph for social interactions")
    graph_fallback: bool = Field(default=True, description="Fallback to memory if graph unavailable")
```

### 2. Memory Configuration

**File**: `agentsociety/cityagent/memory_config.py`

Add new memory attributes for graph integration:

```python
# Graph-related memory attributes
"graph_node_id": MemoryAttribute(
    name="graph_node_id",
    type=str,
    default_or_value=None,
    description="Neo4j node ID for this agent",
    whether_embedding=False,
),
"graph_metrics": MemoryAttribute(
    name="graph_metrics",
    type=dict,
    default_or_value={},
    description="Cached network metrics",
    whether_embedding=False,
),
"graph_last_sync": MemoryAttribute(
    name="graph_last_sync",
    type=datetime,
    default_or_value=None,
    description="Last graph synchronization time",
    whether_embedding=False,
)
```

## Backward Compatibility

### 1. Compatibility Layer

All modifications maintain backward compatibility:

1. **Fallback Mechanism**: If graph_client is None, use existing memory-based logic
2. **Dual Storage**: Keep memory attributes synchronized with graph
3. **Progressive Enhancement**: Graph features enhance but don't replace core functionality

### 2. Migration Helper Methods

```python
class GraphMigrationHelper:
    """Helper methods for migrating existing agents to graph."""
    
    @staticmethod
    async def migrate_agent_to_graph(agent: Agent, graph_client: Neo4jClient):
        """Migrate single agent to graph."""
        # Create node
        node_data = await GraphMigrationHelper._extract_node_data(agent)
        node_id = await graph_client.create_agent_node(node_data)
        
        # Migrate relationships
        await GraphMigrationHelper._migrate_relationships(agent, graph_client)
        
        # Update agent
        await agent.status.update("graph_node_id", node_id)
    
    @staticmethod
    async def sync_from_graph(agent: Agent, graph_client: Neo4jClient):
        """Sync agent state from graph to memory."""
        # Implementation for reverse sync
```

## Testing Requirements

### 1. Graph Integration Tests
- **Unit Tests**: Test each modified method with and without graph_client
- **Integration Tests**: Test full agent lifecycle with graph integration
- **Performance Tests**: Ensure graph queries don't degrade performance
- **Compatibility Tests**: Verify backward compatibility with existing code

### 2. Psychological Modeling Tests
- **Personality Consistency**: Verify behaviors match personality profiles
- **Decision Making**: Test that personality influences decisions appropriately
- **Mental Health Dynamics**: Test stress accumulation and recovery
- **Life Event Triggers**: Verify appropriate event triggering based on conditions

### 3. Life Dynamics Tests
- **Life Stage Transitions**: Test appropriate stage transitions based on age/achievements
- **Goal Pursuit**: Verify goal progress and completion mechanics
- **Event Processing**: Test immediate and long-term impacts of life events
- **Family Dynamics**: Test family unit cohesion and conflict resolution

### 4. Integration Tests
- **Full Lifecycle**: Test agent from young adult through retirement
- **Social Networks**: Test how personality affects relationship formation
- **Event Cascades**: Test how life events trigger other events
- **Graph Sync**: Verify all psychological data syncs properly to Neo4j