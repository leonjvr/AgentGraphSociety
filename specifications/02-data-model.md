# Neo4j Data Model Specification

## Node Types

### 1. Agent Node
Primary node representing all agent types in the system.

```cypher
(:Agent {
  // Core Identity
  id: Integer,                    // Unique agent ID (matches AgentSociety ID)
  uuid: String,                   // UUID for distributed systems
  name: String,                   // Agent name
  type: String,                   // "Citizen", "Institution", "Supervisor", "Individual"
  
  // Demographics (Citizen agents)
  age: Integer,
  gender: String,
  education: String,
  occupation: String,
  marriage_status: String,
  
  // Personality & Psychology
  personality: String,            // Personality description (legacy)
  
  // Big Five Personality Model
  personality_openness: Float,              // 0-1: Creativity, curiosity
  personality_conscientiousness: Float,     // 0-1: Organization, self-discipline
  personality_extraversion: Float,          // 0-1: Sociability, assertiveness
  personality_agreeableness: Float,         // 0-1: Trust, cooperation
  personality_neuroticism: Float,           // 0-1: Emotional instability
  
  // Values System (stored as JSON)
  values: String,                           // JSON: family, career, wealth, etc.
  political_leaning: Float,                 // -1 to 1: left to right
  religious_commitment: Float,              // 0-1: religious involvement
  environmental_concern: Float,             // 0-1: environmental awareness
  technology_adoption: Float,               // 0-1: early adopter to resistant
  
  // Mental State
  emotion_state: String,                    // Current emotional state (legacy)
  stress_level: Float,                      // 0-1: current stress
  anxiety_level: Float,                     // 0-1: anxiety symptoms
  depression_score: Float,                  // 0-1: depression indicators
  life_satisfaction: Float,                 // 0-1: overall satisfaction
  self_esteem: Float,                       // 0-1: self-worth
  burnout_level: Float,                     // 0-1: exhaustion level
  
  // Cognitive Profile
  risk_tolerance: Float,                    // 0-1: risk-taking tendency
  learning_rate: Float,                     // 0-1: speed of belief updates
  cognitive_flexibility: Float,             // 0-1: adaptability
  confirmation_bias: Float,                 // 0-1: bias strength
  social_proof_sensitivity: Float,          // 0-1: conformity tendency
  
  // Life Stage & Goals
  life_stage: String,                       // "young_adult", "established", etc.
  major_goals: String,                      // JSON: current life goals
  life_events_history: String,              // JSON: significant events
  
  // Economic Status
  income: Float,
  currency: Float,
  consumption_level: String,
  
  // Location
  current_location: Point,        // Spatial coordinates
  home_location: Point,
  work_location: Point,
  
  // Metadata
  created_at: DateTime,
  updated_at: DateTime,
  active: Boolean
})
```

### 2. Organization Node
Specialized nodes for institutional agents.

```cypher
(:Organization {
  id: Integer,
  name: String,
  type: String,                   // "Firm", "Bank", "Government", "NBS"
  
  // Organization specifics
  employee_capacity: Integer,
  economic_role: String,
  
  // Location
  location: Point,
  
  // Metadata
  created_at: DateTime
})
```

### 3. Location Node
Represents areas of interest (AOIs) and important locations.

```cypher
(:Location {
  id: Integer,
  name: String,
  type: String,                   // "Home", "Work", "Public", "Commercial"
  category: String,               // "Restaurant", "Park", "Office", etc.
  
  // Spatial data
  coordinates: Point,
  area_boundary: String,          // GeoJSON polygon
  
  // Capacity
  max_occupancy: Integer,
  current_occupancy: Integer
})
```

### 4. Message Node (Optional)
For persistent message storage and analysis.

```cypher
(:Message {
  id: String,
  content: String,
  timestamp: DateTime,
  type: String,                   // "social", "economic", "broadcast"
  sentiment: Float,               // -1 to 1
  
  // Metadata
  propagation_count: Integer,
  read_by: [Integer]              // Array of agent IDs
})
```

### 5. LifeEvent Node
Represents significant life events that shape agent behavior.

```cypher
(:LifeEvent {
  id: String,
  agent_id: Integer,
  event_type: String,             // "marriage", "divorce", "job_loss", etc.
  category: String,               // "romantic", "career", "family", "health"
  occurred_at: DateTime,
  life_stage: String,             // Life stage when event occurred
  
  // Event details
  severity: Float,                // 0-1: how major the event is
  description: String,
  
  // Impacts (stored as JSON)
  immediate_impacts: String,      // JSON: immediate attribute changes
  long_term_impacts: String,      // JSON: gradual changes
  
  // Processing
  processed: Boolean,
  processing_complete_date: DateTime,
  recovery_time_days: Integer
})
```

### 6. Goal Node
Represents life goals and aspirations.

```cypher
(:Goal {
  id: String,
  name: String,
  category: String,               // "career", "family", "financial", etc.
  description: String,
  
  // Goal properties
  priority: Float,                // 0-1: importance to agent
  progress: Float,                // 0-1: completion percentage
  
  // Timeline
  created_at: DateTime,
  target_date: DateTime,
  completed_at: DateTime,
  
  // Status
  status: String,                 // "active", "completed", "abandoned"
  abandonment_reason: String
})
```

### 7. FamilyUnit Node
Represents family groups for complex family dynamics.

```cypher
(:FamilyUnit {
  id: String,
  family_type: String,            // "nuclear", "extended", "single_parent"
  household_id: String,
  
  // Family dynamics
  cohesion_level: Float,          // 0-1: family closeness
  conflict_level: Float,          // 0-1: current tensions
  communication_style: String,    // "open", "reserved", "conflicted"
  
  // Economic
  shared_finances: Boolean,
  financial_pool: Float,
  
  // Metadata
  formed_at: DateTime,
  life_cycle_stage: String        // "formation", "expansion", "empty_nest"
})
```

## Relationship Types

### 1. Social Relationships

#### KNOWS
Basic social connection between agents.
```cypher
(:Agent)-[:KNOWS {
  strength: Float,              // 0-100 relationship strength
  since: DateTime,              // Relationship start date
  last_interaction: DateTime,
  interaction_count: Integer,
  
  // Relationship quality
  trust: Float,                 // 0-1 trust level
  affinity: Float,              // 0-1 emotional closeness
  
  // Communication preferences
  preferred_channel: String,    // "online", "offline"
  response_rate: Float          // 0-1 how often they respond
}]->(:Agent)
```

#### FAMILY
Family relationships with specific roles and enhanced dynamics.
```cypher
(:Agent)-[:FAMILY {
  relation_type: String,        // "parent", "child", "sibling", "spouse"
  family_unit_id: String,       // Links to FamilyUnit node
  strength: Float,              // 60-100 (typically stronger)
  
  // Family dynamics
  emotional_closeness: Float,   // 0-1: emotional bond strength
  communication_frequency: String, // "daily", "weekly", "monthly", "rare"
  support_given: Float,         // 0-1: support provided
  support_received: Float,      // 0-1: support received
  
  // Family-specific
  household_member: Boolean,
  financial_dependent: Boolean,
  
  // History
  relationship_formed: DateTime,
  major_conflicts: Integer,     // Count of significant conflicts
  shared_experiences: Integer   // Count of important shared events
}]->(:Agent)
```

#### COLLEAGUE
Professional relationships.
```cypher
(:Agent)-[:COLLEAGUE {
  strength: Float,              // 40-70 typically
  department: String,
  hierarchy: String,            // "peer", "superior", "subordinate"
  
  // Work dynamics
  collaboration_frequency: String,  // "daily", "weekly", "monthly"
  project_count: Integer
}]->(:Agent)
```

#### FRIEND
Friendship relationships.
```cypher
(:Agent)-[:FRIEND {
  strength: Float,              // 30-80 variable
  friendship_type: String,      // "close", "casual", "acquaintance"
  
  // Friendship dynamics
  shared_interests: [String],
  meeting_frequency: String
}]->(:Agent)
```

### 2. Economic Relationships

#### WORKS_AT
Employment relationship.
```cypher
(:Agent)-[:WORKS_AT {
  position: String,
  department: String,
  salary: Float,
  
  // Employment details
  start_date: DateTime,
  contract_type: String,        // "permanent", "contract", "part-time"
  hours_per_week: Float
}]->(:Organization)
```

#### CUSTOMER_OF
Economic transaction relationships.
```cypher
(:Agent)-[:CUSTOMER_OF {
  since: DateTime,
  transaction_count: Integer,
  total_spent: Float,
  
  // Customer behavior
  loyalty_score: Float,
  preferred_products: [String]
}]->(:Organization)
```

### 3. Spatial Relationships

#### LOCATED_AT
Current location of agent.
```cypher
(:Agent)-[:LOCATED_AT {
  arrival_time: DateTime,
  planned_duration: Integer,    // minutes
  activity: String              // "working", "shopping", "socializing"
}]->(:Location)
```

#### LIVES_AT
Home location.
```cypher
(:Agent)-[:LIVES_AT {
  since: DateTime,
  ownership: String             // "owner", "renter"
}]->(:Location)
```

### 4. Communication Relationships

#### SENT_MESSAGE
Message sending tracking.
```cypher
(:Agent)-[:SENT_MESSAGE {
  timestamp: DateTime,
  channel: String,              // "direct", "broadcast"
  status: String                // "delivered", "read", "ignored"
}]->(:Message)
```

#### RECEIVED_MESSAGE
Message reception tracking.
```cypher
(:Message)-[:RECEIVED_BY {
  timestamp: DateTime,
  read_at: DateTime,
  reaction: String              // "positive", "negative", "neutral"
}]->(:Agent)
```

### 5. Influence Relationships

#### INFLUENCES
Social influence relationships.
```cypher
(:Agent)-[:INFLUENCES {
  influence_strength: Float,    // 0-1
  domain: String,               // "political", "consumer", "social"
  
  // Influence metrics
  successful_influences: Integer,
  total_attempts: Integer
}]->(:Agent)
```

### 6. Life Event Relationships

#### EXPERIENCED
Links agents to their life events.
```cypher
(:Agent)-[:EXPERIENCED {
  impact_score: Float,          // 0-1: how much it affected them
  recovery_time_days: Integer,
  changed_life_trajectory: Boolean,
  
  // Coping
  coping_strategy: String,      // "social_support", "isolation", "professional_help"
  support_network_size: Integer
}]->(:LifeEvent)
```

#### TRIGGERED
Causal chains between life events.
```cypher
(:LifeEvent)-[:TRIGGERED {
  causality_strength: Float,    // 0-1: how directly it caused the next event
  time_delay_days: Integer
}]->(:LifeEvent)
```

#### INFLUENCED_BY
Social influence on life events.
```cypher
(:LifeEvent)-[:INFLUENCED_BY {
  influence_type: String,       // "peer_pressure", "family_expectation", "social_norm"
  influence_strength: Float     // 0-1
}]->(:Agent)
```

### 7. Goal Relationships

#### PURSUES
Agent actively pursuing a goal.
```cypher
(:Agent)-[:PURSUES {
  commitment_level: Float,      // 0-1: dedication to goal
  time_allocated_weekly: Float, // Hours per week
  
  // Progress tracking
  milestones_completed: Integer,
  milestones_total: Integer,
  last_progress_date: DateTime
}]->(:Goal)
```

#### SHARES_GOAL
Multiple agents pursuing same goal.
```cypher
(:Goal)-[:SHARED_BY {
  cooperation_level: Float,     // 0-1: how much they cooperate
  competition_level: Float,     // 0-1: how much they compete
  
  // Coordination
  coordinated_efforts: Boolean,
  conflict_areas: [String]
}]->(:Agent)
```

### 8. Professional Network Relationships

#### MENTORS
Professional mentorship relationships.
```cypher
(:Agent)-[:MENTORS {
  since: DateTime,
  field: String,                // Area of mentorship
  
  // Mentorship quality
  influence_on_career: Float,   // 0-1: career impact
  meeting_frequency: String,    // "weekly", "monthly", "quarterly"
  mentorship_style: String      // "directive", "supportive", "delegating"
}]->(:Agent)
```

#### PROFESSIONAL_NETWORK
Extended professional connections.
```cypher
(:Agent)-[:PROFESSIONAL_NETWORK {
  context: String,              // How they met
  strength: Float,              // 0-100: connection strength
  
  // Network value
  mutual_benefit_score: Float,  // 0-1: reciprocal value
  referral_count: Integer,
  
  // Interaction
  last_interaction: DateTime,
  interaction_type: String      // "in-person", "online", "conference"
}]->(:Agent)
```

### 9. Family Unit Relationships

#### BELONGS_TO
Links agents to their family unit.
```cypher
(:Agent)-[:BELONGS_TO {
  role: String,                 // "parent", "child", "head"
  joined_date: DateTime,
  
  // Participation
  involvement_level: Float,     // 0-1: family participation
  decision_making_power: Float  // 0-1: influence in family decisions
}]->(:FamilyUnit)
```

## Indexes and Constraints

### Unique Constraints
```cypher
CREATE CONSTRAINT agent_id_unique ON (a:Agent) ASSERT a.id IS UNIQUE;
CREATE CONSTRAINT org_id_unique ON (o:Organization) ASSERT o.id IS UNIQUE;
CREATE CONSTRAINT location_id_unique ON (l:Location) ASSERT l.id IS UNIQUE;
CREATE CONSTRAINT life_event_id_unique ON (e:LifeEvent) ASSERT e.id IS UNIQUE;
CREATE CONSTRAINT goal_id_unique ON (g:Goal) ASSERT g.id IS UNIQUE;
CREATE CONSTRAINT family_unit_id_unique ON (f:FamilyUnit) ASSERT f.id IS UNIQUE;
```

### Indexes for Performance
```cypher
CREATE INDEX agent_type_idx FOR (a:Agent) ON (a.type);
CREATE INDEX agent_location_idx FOR (a:Agent) ON (a.current_location);
CREATE INDEX agent_active_idx FOR (a:Agent) ON (a.active);
CREATE INDEX agent_life_stage_idx FOR (a:Agent) ON (a.life_stage);
CREATE INDEX agent_stress_level_idx FOR (a:Agent) ON (a.stress_level);
CREATE INDEX relationship_strength_idx FOR ()-[r:KNOWS]-() ON (r.strength);
CREATE INDEX message_timestamp_idx FOR (m:Message) ON (m.timestamp);
CREATE INDEX life_event_category_idx FOR (e:LifeEvent) ON (e.category);
CREATE INDEX life_event_occurred_idx FOR (e:LifeEvent) ON (e.occurred_at);
CREATE INDEX goal_status_idx FOR (g:Goal) ON (g.status);
CREATE INDEX goal_category_idx FOR (g:Goal) ON (g.category);
```

### Composite Indexes
```cypher
CREATE INDEX agent_type_active_idx FOR (a:Agent) ON (a.type, a.active);
CREATE INDEX agent_occupation_age_idx FOR (a:Agent) ON (a.occupation, a.age);
CREATE INDEX agent_personality_idx FOR (a:Agent) ON (a.personality_extraversion, a.personality_openness);
CREATE INDEX life_event_agent_category_idx FOR (e:LifeEvent) ON (e.agent_id, e.category);
```

## Data Integrity Rules

1. **Relationship Symmetry**: Some relationships (KNOWS, FRIEND) should be bidirectional
2. **Strength Constraints**: Relationship strength must be 0-100
3. **Temporal Consistency**: last_interaction <= current_time
4. **Location Exclusivity**: Agent can only be LOCATED_AT one place at a time
5. **Hierarchy Consistency**: COLLEAGUE relationships must maintain valid hierarchy

## Migration Mapping

Current AgentSociety → Neo4j mapping:

| AgentSociety | Neo4j |
|--------------|-------|
| `agent.id` | `Agent.id` |
| `status["friends"]` | `KNOWS` relationships |
| `status["relationships"][id]` | `KNOWS.strength` |
| `status["relation_types"][id]` | Specific relationship types |
| `status["chat_histories"]` | `Message` nodes + relationships |
| `status["position"]` | `LOCATED_AT` relationship |
| `profile["personality"]` | `Agent.personality` (legacy) + Big Five traits |
| `profile["name"]` | `Agent.name` |
| `profile["age"]` | `Agent.age` |
| `profile["occupation"]` | `Agent.occupation` |
| N/A (new) | `Agent.personality_*` (Big Five traits) |
| N/A (new) | `Agent.values` (JSON) |
| N/A (new) | `Agent.mental_state_*` attributes |
| N/A (new) | `LifeEvent` nodes |
| N/A (new) | `Goal` nodes |
| N/A (new) | `FamilyUnit` nodes |