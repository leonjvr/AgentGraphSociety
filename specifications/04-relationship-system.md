# Enhanced Relationship System Specification

## Overview

This document specifies the new graph-based relationship system that replaces the current dictionary-based approach with rich, multi-dimensional relationships in Neo4j.

## Relationship Evolution Model

### 1. Relationship Lifecycle

```
Creation → Growth → Maintenance → Decay → Termination
```

#### Creation Phase
- Triggered by first interaction or introduction
- Initial strength based on context (work, social event, family)
- Relationship type determined by interaction context

#### Growth Phase
- Positive interactions increase strength
- Shared experiences create bonds
- Trust builds through successful interactions

#### Maintenance Phase
- Regular interactions maintain strength
- Lack of interaction causes decay
- Quality of interactions affects trajectory

#### Decay Phase
- Time-based decay without interaction
- Negative interactions accelerate decay
- Can be reversed through positive engagement

#### Termination
- Relationship strength drops below threshold
- Explicit blocking or conflict
- Extended absence (agent deactivation)

### 2. Relationship Strength Algorithm

```python
def calculate_relationship_strength(current_strength: float, 
                                  interaction: Dict,
                                  time_since_last: float) -> float:
    """
    Calculate new relationship strength after interaction.
    
    Factors:
    - Current strength (0-100)
    - Interaction quality (-1 to 1)
    - Time decay
    - Relationship type multiplier
    """
    # Time decay
    decay_rate = 0.1  # 10% per month without interaction
    months_elapsed = time_since_last / (30 * 24 * 3600)
    time_decay = current_strength * (decay_rate * months_elapsed)
    
    # Interaction impact
    interaction_quality = interaction.get("quality", 0.5)
    interaction_impact = 10 * interaction_quality  # ±10 points
    
    # Type multiplier
    type_multipliers = {
        "family": 0.5,      # Slower decay
        "colleague": 0.8,   # Moderate decay
        "friend": 1.0,      # Normal decay
        "acquaintance": 1.2 # Faster decay
    }
    
    # Calculate new strength
    new_strength = current_strength - time_decay + interaction_impact
    new_strength = max(0, min(100, new_strength))  # Clamp 0-100
    
    return new_strength
```

## Multi-Type Relationships

### 1. Relationship Combinations

Agents can have multiple relationship types simultaneously:

```cypher
// Example: Colleague who is also a friend
(:Agent)-[:COLLEAGUE {strength: 60, department: "Engineering"}]->(:Agent)
(:Agent)-[:FRIEND {strength: 75, shared_interests: ["hiking", "gaming"]}]->(:Agent)
```

### 2. Relationship Priority

When multiple relationships exist, priority for interactions:

1. **FAMILY** - Highest priority
2. **FRIEND** - High priority  
3. **COLLEAGUE** - Medium priority
4. **KNOWS** - Low priority

### 3. Context-Aware Selection

```python
async def select_relationship_context(agent_id: int, target_id: int, context: str) -> str:
    """
    Select appropriate relationship type based on context.
    
    Contexts:
    - "work" → COLLEAGUE relationship
    - "home" → FAMILY relationship  
    - "social" → FRIEND relationship
    - "general" → Highest strength relationship
    """
    query = """
    MATCH (a:Agent {id: $agent_id})-[r]->(t:Agent {id: $target_id})
    WHERE type(r) IN ['FAMILY', 'FRIEND', 'COLLEAGUE', 'KNOWS']
    RETURN type(r) as rel_type, r.strength as strength
    ORDER BY 
        CASE $context
            WHEN 'work' THEN CASE type(r) WHEN 'COLLEAGUE' THEN 0 ELSE 1 END
            WHEN 'home' THEN CASE type(r) WHEN 'FAMILY' THEN 0 ELSE 1 END
            WHEN 'social' THEN CASE type(r) WHEN 'FRIEND' THEN 0 ELSE 1 END
            ELSE 0
        END,
        r.strength DESC
    LIMIT 1
    """
```

## Influence Propagation System

### 1. Influence Model

```python
class InfluenceModel:
    """Model for how influence spreads through network."""
    
    def calculate_influence_probability(
        self,
        source_influence: float,      # Source agent's influence score
        relationship_strength: float,  # Relationship strength (0-100)
        message_appeal: float,        # Message appeal factor (0-1)
        target_resistance: float      # Target's resistance (0-1)
    ) -> float:
        """Calculate probability of influence success."""
        
        # Base probability from relationship
        base_prob = relationship_strength / 100.0
        
        # Modify by source influence
        influence_modifier = 1 + (source_influence - 0.5)  # ±50%
        
        # Modify by message appeal
        appeal_modifier = 0.5 + message_appeal  # 50-150%
        
        # Apply resistance
        resistance_modifier = 1 - (target_resistance * 0.5)  # Up to 50% reduction
        
        # Calculate final probability
        probability = base_prob * influence_modifier * appeal_modifier * resistance_modifier
        
        return max(0, min(1, probability))  # Clamp 0-1
```

### 2. Influence Propagation Algorithm

```cypher
// Find agents to influence within N hops
MATCH path = (source:Agent {id: $source_id})-[r:KNOWS|FRIEND|FAMILY|COLLEAGUE*1..n]->(target:Agent)
WHERE ALL(rel IN relationships(path) WHERE rel.strength >= $min_strength)
AND target.id <> $source_id
WITH target, 
     REDUCE(influence = 1.0, rel IN relationships(path) | 
            influence * (rel.strength/100.0) * $decay_factor) as influence_score,
     length(path) as distance
WHERE influence_score >= $threshold
RETURN target, influence_score, distance
ORDER BY influence_score DESC
```

## Community Detection

### 1. Community Formation

Communities form based on:
- Dense connections within group
- Shared attributes (occupation, interests)
- Geographic proximity
- Interaction patterns

### 2. Community Detection Algorithm

```python
async def detect_communities(graph_client: Neo4jClient) -> Dict[int, int]:
    """
    Detect communities using Louvain algorithm.
    Returns mapping of agent_id to community_id.
    """
    query = """
    CALL gds.louvain.stream('social-network', {
        relationshipWeightProperty: 'strength',
        includeIntermediateCommunities: false
    })
    YIELD nodeId, communityId
    RETURN gds.util.asNode(nodeId).id AS agent_id, communityId
    """
    
    results = await graph_client.query(query)
    return {r['agent_id']: r['communityId'] for r in results}
```

### 3. Community-Based Behaviors

```python
class CommunityBehavior:
    """Behaviors influenced by community membership."""
    
    async def get_community_influence(self, agent_id: int) -> float:
        """Get how much agent is influenced by their community."""
        query = """
        MATCH (a:Agent {id: $agent_id})-[r:KNOWS|FRIEND|FAMILY|COLLEAGUE]-(b:Agent)
        WHERE a.community_id = b.community_id
        RETURN AVG(r.strength) as avg_strength,
               COUNT(b) as community_size
        """
        
    async def spread_community_norm(self, norm: str, community_id: int):
        """Spread behavioral norm through community."""
        # Implementation for norm propagation
```

## Relationship Queries

### 1. Friend Recommendation

```cypher
// Recommend friends based on mutual connections and similarity
MATCH (me:Agent {id: $agent_id})-[:KNOWS|FRIEND]-(mutual:Agent)-[:KNOWS|FRIEND]-(potential:Agent)
WHERE NOT (me)-[]-(potential) 
  AND me <> potential
  AND potential.active = true
WITH potential, COUNT(mutual) as mutual_count,
     // Similarity scoring
     CASE WHEN me.occupation = potential.occupation THEN 0.2 ELSE 0 END +
     CASE WHEN me.education = potential.education THEN 0.1 ELSE 0 END +
     CASE WHEN abs(me.age - potential.age) <= 5 THEN 0.1 ELSE 0 END as similarity
RETURN potential, 
       mutual_count * 0.3 + similarity as recommendation_score
ORDER BY recommendation_score DESC
LIMIT 10
```

### 2. Influence Path Finding

```cypher
// Find shortest influence path between agents
MATCH path = shortestPath(
    (source:Agent {id: $source_id})-[r:KNOWS|FRIEND|FAMILY|COLLEAGUE*]-(target:Agent {id: $target_id})
)
WHERE ALL(rel IN relationships(path) WHERE rel.strength >= 30)
RETURN path,
       REDUCE(s = 1.0, rel IN relationships(path) | s * rel.strength/100) as path_strength
```

### 3. Social Circle Analysis

```cypher
// Analyze agent's social circles
MATCH (a:Agent {id: $agent_id})-[r]-(b:Agent)
WITH type(r) as rel_type,
     AVG(r.strength) as avg_strength,
     COUNT(b) as circle_size,
     COLLECT(b.id) as members
RETURN rel_type, avg_strength, circle_size, members
ORDER BY avg_strength DESC
```

## Relationship Events

### 1. Event Types

- **RELATIONSHIP_CREATED**: New connection formed
- **RELATIONSHIP_STRENGTHENED**: Positive interaction
- **RELATIONSHIP_WEAKENED**: Negative interaction or decay
- **RELATIONSHIP_TYPE_CHANGED**: Evolution of relationship
- **RELATIONSHIP_TERMINATED**: Connection ended

### 2. Event Handlers

```python
class RelationshipEventHandler:
    """Handle relationship lifecycle events."""
    
    async def on_relationship_created(self, agent1_id: int, agent2_id: int, 
                                    rel_type: str, context: Dict):
        """Handle new relationship creation."""
        # Create bidirectional relationship
        # Initialize strength based on type and context
        # Trigger introductory interactions
        
    async def on_relationship_strengthened(self, agent1_id: int, agent2_id: int,
                                         interaction: Dict):
        """Handle relationship strengthening."""
        # Update strength
        # Update last_interaction
        # Check for relationship type evolution
        
    async def on_relationship_weakened(self, agent1_id: int, agent2_id: int,
                                     reason: str):
        """Handle relationship weakening."""
        # Decrease strength
        # Check for termination threshold
        # Trigger recovery behaviors
```

## Performance Optimizations

### 1. Relationship Caching

```python
class RelationshipCache:
    """LRU cache for relationship queries."""
    
    def __init__(self, max_size: int = 1000, ttl: int = 300):
        self.cache = {}  # agent_id -> {target_id: relationship_data}
        self.max_size = max_size
        self.ttl = ttl
        
    async def get_relationships(self, agent_id: int) -> List[Dict]:
        """Get cached relationships or fetch from graph."""
        if agent_id in self.cache:
            if self._is_valid(self.cache[agent_id]):
                return self.cache[agent_id]['data']
        
        # Fetch from graph
        relationships = await self._fetch_from_graph(agent_id)
        self._update_cache(agent_id, relationships)
        return relationships
```

### 2. Batch Operations

```python
async def batch_update_relationships(updates: List[Dict]):
    """Batch update multiple relationships in single transaction."""
    query = """
    UNWIND $updates as update
    MATCH (a:Agent {id: update.agent1_id})-[r]-(b:Agent {id: update.agent2_id})
    WHERE type(r) = update.rel_type
    SET r += update.properties
    """
```

### 3. Indexed Queries

Ensure all relationship queries use indexes:
- Index on relationship strength for range queries
- Index on last_interaction for time-based queries
- Composite indexes for complex filters