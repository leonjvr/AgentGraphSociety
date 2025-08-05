# Migration Strategy Specification

## Overview

This document outlines the strategy for migrating from the current dictionary-based relationship system to the Neo4j graph-based system, ensuring zero downtime and data integrity.

## Migration Principles

1. **Zero Downtime**: System remains operational during migration
2. **Data Integrity**: No relationship data lost
3. **Incremental Migration**: Migrate in phases, not all at once
4. **Rollback Capability**: Can revert at any stage
5. **Backward Compatibility**: Old code continues to work

## Migration Architecture

```
┌─────────────────────────────────────────┐
│         Current State                   │
│  ┌─────────────┐                       │
│  │   Memory    │  (Primary Storage)     │
│  │   System    │                       │
│  └─────────────┘                       │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│      Dual-Write Phase                   │
│  ┌─────────────┐    ┌────────────┐     │
│  │   Memory    │ ←→ │   Neo4j    │     │
│  │   System    │    │   Graph    │     │
│  └─────────────┘    └────────────┘     │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│        Target State                     │
│                     ┌────────────┐      │
│  (Cache Only) ←─────│   Neo4j    │      │
│                     │   Graph    │      │
│                     └────────────┘      │
└─────────────────────────────────────────┘
```

## Phase 1: Preparation (Week 1)

### 1.1 Infrastructure Setup

```python
# Docker Compose addition
"""
neo4j:
  image: neo4j:5.15
  environment:
    - NEO4J_AUTH=neo4j/password
    - NEO4J_PLUGINS=["apoc", "graph-data-science"]
  ports:
    - "7474:7474"  # Browser
    - "7687:7687"  # Bolt
  volumes:
    - neo4j_data:/data
    - neo4j_logs:/logs
"""
```

### 1.2 Schema Creation

```cypher
// Create constraints and indexes
CREATE CONSTRAINT agent_id_unique IF NOT EXISTS ON (a:Agent) ASSERT a.id IS UNIQUE;
CREATE INDEX agent_type_idx IF NOT EXISTS FOR (a:Agent) ON (a.type);
CREATE INDEX agent_active_idx IF NOT EXISTS FOR (a:Agent) ON (a.active);
CREATE INDEX relationship_strength_idx IF NOT EXISTS FOR ()-[r:KNOWS]-() ON (r.strength);
```

### 1.3 Migration Tools Development

```python
# migration_tools.py
class MigrationManager:
    """Manages the migration process."""
    
    def __init__(self, agentsociety_engine, neo4j_client):
        self.engine = agentsociety_engine
        self.graph = neo4j_client
        self.migration_state = self._load_migration_state()
        
    async def migrate_batch(self, agent_ids: List[int], batch_size: int = 100):
        """Migrate a batch of agents."""
        for i in range(0, len(agent_ids), batch_size):
            batch = agent_ids[i:i+batch_size]
            await self._migrate_agents(batch)
            await self._checkpoint(batch)
```

## Phase 2: Data Migration (Week 2)

### 2.1 Agent Node Migration

```python
async def migrate_agents_to_graph(simulation, graph_client, batch_size=1000):
    """Migrate all agents to Neo4j."""
    
    # Get all agent IDs
    all_agents = await simulation.filter(types=(Agent,))
    
    # Progress tracking
    total = len(all_agents)
    migrated = 0
    
    for i in range(0, total, batch_size):
        batch = all_agents[i:i+batch_size]
        
        # Prepare batch data
        batch_data = []
        for agent_id in batch:
            agent_data = await extract_agent_data(simulation, agent_id)
            batch_data.append(agent_data)
        
        # Batch insert to Neo4j
        await graph_client.batch_create_agents(batch_data)
        
        migrated += len(batch)
        logger.info(f"Migrated {migrated}/{total} agents")
        
        # Checkpoint
        await save_checkpoint({"last_batch": i, "migrated": migrated})
```

### 2.2 Relationship Migration

```python
async def migrate_relationships_to_graph(simulation, graph_client):
    """Migrate all relationships to Neo4j."""
    
    citizen_ids = await simulation.filter(types=(SocietyAgent,))
    
    for agent_id in citizen_ids:
        # Get relationship data from memory
        friends = await simulation.get_status(agent_id, "friends")
        relationships = await simulation.get_status(agent_id, "relationships")
        relation_types = await simulation.get_status(agent_id, "relation_types")
        
        # Create relationships in graph
        for friend_id in friends:
            rel_type = relation_types.get(friend_id, "KNOWS")
            strength = relationships.get(friend_id, 50)
            
            await graph_client.create_relationship(
                agent1_id=agent_id,
                agent2_id=friend_id,
                rel_type=rel_type,
                properties={
                    "strength": strength,
                    "since": datetime.now(),
                    "migrated": True
                }
            )
```

### 2.3 Data Validation

```python
class MigrationValidator:
    """Validate migration data integrity."""
    
    async def validate_agent_migration(self, agent_id: int) -> bool:
        """Validate single agent migration."""
        # Get data from both sources
        memory_data = await self.get_memory_data(agent_id)
        graph_data = await self.get_graph_data(agent_id)
        
        # Compare core attributes
        for attr in ["name", "age", "occupation", "gender"]:
            if memory_data.get(attr) != graph_data.get(attr):
                logger.error(f"Mismatch in {attr} for agent {agent_id}")
                return False
                
        return True
    
    async def validate_relationships(self, agent_id: int) -> bool:
        """Validate relationship migration."""
        memory_friends = set(await self.engine.get_status(agent_id, "friends"))
        
        graph_friends = set()
        query = """
        MATCH (a:Agent {id: $agent_id})-[r]-(b:Agent)
        RETURN b.id as friend_id
        """
        results = await self.graph.query(query, {"agent_id": agent_id})
        graph_friends = {r["friend_id"] for r in results}
        
        if memory_friends != graph_friends:
            logger.error(f"Friend mismatch for agent {agent_id}")
            return False
            
        return True
```

## Phase 3: Dual-Write Implementation (Week 3)

### 3.1 Write Wrapper Implementation

```python
class DualWriteWrapper:
    """Wrapper to write to both memory and graph."""
    
    def __init__(self, memory_system, graph_client):
        self.memory = memory_system
        self.graph = graph_client
        self.write_mode = "dual"  # "memory_only", "dual", "graph_primary"
        
    async def update_relationship(self, agent1_id: int, agent2_id: int, 
                                update_data: Dict):
        """Update relationship in both systems."""
        
        # Always write to memory for now
        if self.write_mode in ["memory_only", "dual"]:
            await self._update_memory_relationship(agent1_id, agent2_id, update_data)
        
        # Write to graph if enabled
        if self.write_mode in ["dual", "graph_primary"]:
            try:
                await self._update_graph_relationship(agent1_id, agent2_id, update_data)
            except Exception as e:
                logger.error(f"Graph write failed: {e}")
                if self.write_mode == "graph_primary":
                    raise  # Fail if graph is primary
```

### 3.2 Read Strategy Implementation

```python
class HybridReadStrategy:
    """Strategy for reading from memory and/or graph."""
    
    def __init__(self, memory_system, graph_client):
        self.memory = memory_system
        self.graph = graph_client
        self.read_mode = "memory_primary"  # "memory_primary", "graph_primary", "graph_only"
        
    async def get_relationships(self, agent_id: int) -> List[Dict]:
        """Get relationships with fallback strategy."""
        
        if self.read_mode == "memory_primary":
            # Try memory first
            try:
                return await self._get_from_memory(agent_id)
            except Exception:
                logger.warning("Memory read failed, falling back to graph")
                return await self._get_from_graph(agent_id)
                
        elif self.read_mode == "graph_primary":
            # Try graph first
            try:
                relationships = await self._get_from_graph(agent_id)
                # Update memory cache
                await self._update_memory_cache(agent_id, relationships)
                return relationships
            except Exception:
                logger.warning("Graph read failed, falling back to memory")
                return await self._get_from_memory(agent_id)
```

## Phase 4: Gradual Cutover (Week 4)

### 4.1 Feature Flag System

```python
class FeatureFlags:
    """Control migration features."""
    
    def __init__(self):
        self.flags = {
            "use_graph_for_friend_selection": False,
            "use_graph_for_influence": False,
            "use_graph_for_analytics": True,
            "write_to_graph": True,
            "graph_as_primary": False
        }
        
    def is_enabled(self, feature: str, agent_id: int = None) -> bool:
        """Check if feature is enabled, with optional per-agent control."""
        
        # Global flag
        if feature not in self.flags:
            return False
            
        # Can implement percentage rollout
        if agent_id and self.get_rollout_percentage(feature) < 100:
            return self._is_in_rollout(agent_id, feature)
            
        return self.flags[feature]
```

### 4.2 Monitoring and Metrics

```python
class MigrationMetrics:
    """Track migration progress and health."""
    
    def __init__(self):
        self.metrics = {
            "memory_reads": 0,
            "graph_reads": 0,
            "memory_writes": 0,
            "graph_writes": 0,
            "read_failures": 0,
            "write_failures": 0,
            "latency_memory_ms": [],
            "latency_graph_ms": []
        }
        
    async def record_operation(self, operation: str, system: str, 
                             success: bool, latency_ms: float):
        """Record operation metrics."""
        key = f"{system}_{operation}s"
        self.metrics[key] += 1
        
        if not success:
            self.metrics[f"{operation}_failures"] += 1
            
        if latency_ms:
            self.metrics[f"latency_{system}_ms"].append(latency_ms)
            
    def get_health_score(self) -> float:
        """Calculate system health score."""
        total_ops = sum([
            self.metrics["memory_reads"],
            self.metrics["graph_reads"],
            self.metrics["memory_writes"],
            self.metrics["graph_writes"]
        ])
        
        if total_ops == 0:
            return 1.0
            
        failure_rate = (
            self.metrics["read_failures"] + 
            self.metrics["write_failures"]
        ) / total_ops
        
        return 1.0 - failure_rate
```

## Phase 5: Cleanup (Week 5)

### 5.1 Memory System Cleanup

```python
async def cleanup_memory_relationships(simulation, graph_client):
    """Remove relationship data from memory after verification."""
    
    citizen_ids = await simulation.filter(types=(SocietyAgent,))
    
    for agent_id in citizen_ids:
        # Verify data exists in graph
        if await verify_agent_in_graph(agent_id, graph_client):
            # Clear memory relationship data
            await simulation.update_status(agent_id, "friends", [])
            await simulation.update_status(agent_id, "relationships", {})
            await simulation.update_status(agent_id, "relation_types", {})
            
            # Mark as migrated
            await simulation.update_status(agent_id, "relationships_migrated", True)
```

### 5.2 Code Cleanup

Remove dual-write code and migration utilities:

```python
# Before cleanup
class SocialBlock:
    def __init__(self):
        self.dual_writer = DualWriteWrapper(memory, graph)
        
# After cleanup  
class SocialBlock:
    def __init__(self):
        self.graph_client = graph_client
```

## Rollback Plan

### Rollback Triggers
1. Graph performance degradation >50%
2. Data integrity issues detected
3. Critical bugs in graph integration
4. User-reported issues spike

### Rollback Steps

```python
class RollbackManager:
    """Manage rollback procedures."""
    
    async def rollback_to_memory(self):
        """Rollback to memory-only system."""
        
        # 1. Stop writes to graph
        await self.set_write_mode("memory_only")
        
        # 2. Sync latest data from graph to memory
        await self.sync_graph_to_memory()
        
        # 3. Switch reads to memory
        await self.set_read_mode("memory_only")
        
        # 4. Disable graph features
        await self.disable_all_graph_features()
        
        # 5. Notify monitoring
        await self.notify_rollback_complete()
```

## Migration Checklist

- [ ] Neo4j infrastructure deployed
- [ ] Schema created and indexes built
- [ ] Migration tools tested
- [ ] Backup of current data completed
- [ ] Agent nodes migrated
- [ ] Relationships migrated
- [ ] Data validation passed
- [ ] Dual-write implemented
- [ ] Monitoring in place
- [ ] Performance benchmarks met
- [ ] Feature flags configured
- [ ] Rollback plan tested
- [ ] Documentation updated
- [ ] Team trained on new system
- [ ] Gradual rollout completed
- [ ] Memory cleanup done
- [ ] Migration marked complete