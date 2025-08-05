# Performance Considerations

## Overview

This document outlines performance optimizations and considerations for the Neo4j integration in AgentGraphSociety, ensuring the system can scale to millions of agents and billions of relationships.

## Performance Targets

### Response Time SLAs

| Operation | Target | Maximum |
|-----------|--------|---------|
| Single agent lookup | <10ms | 50ms |
| Relationship query | <20ms | 100ms |
| Friend recommendation | <50ms | 200ms |
| Community detection | <5s | 30s |
| Influence propagation | <100ms | 500ms |
| Batch update (1000 items) | <1s | 5s |

### Scale Targets

- **Agents**: 10 million nodes
- **Relationships**: 100 million edges
- **Concurrent Operations**: 10,000/second
- **Message Throughput**: 100,000/second

## Database Optimization

### 1. Index Strategy

```cypher
-- Primary Indexes
CREATE INDEX agent_id_idx FOR (a:Agent) ON (a.id);
CREATE INDEX agent_type_active_idx FOR (a:Agent) ON (a.type, a.active);
CREATE INDEX agent_location_idx FOR (a:Agent) ON (a.current_location);

-- Relationship Indexes  
CREATE INDEX rel_strength_idx FOR ()-[r:KNOWS]-() ON (r.strength);
CREATE INDEX rel_last_interaction_idx FOR ()-[r:KNOWS]-() ON (r.last_interaction);

-- Full-text Search Indexes
CREATE FULLTEXT INDEX agent_name_search FOR (a:Agent) ON EACH [a.name];
CREATE FULLTEXT INDEX agent_occupation_search FOR (a:Agent) ON EACH [a.occupation];

-- Composite Indexes for Common Queries
CREATE INDEX agent_age_occupation_idx FOR (a:Agent) ON (a.age, a.occupation);
CREATE INDEX agent_gender_education_idx FOR (a:Agent) ON (a.gender, a.education);
```

### 2. Query Optimization

#### Use Index Hints

```cypher
-- Force index usage
MATCH (a:Agent)
USING INDEX a:Agent(id)
WHERE a.id = $agent_id
RETURN a
```

#### Limit Result Sets Early

```cypher
-- Bad: Filter after expansion
MATCH (a:Agent {id: $id})-[:KNOWS*1..3]-(b:Agent)
WHERE b.age > 25
RETURN b

-- Good: Filter during expansion
MATCH (a:Agent {id: $id})-[:KNOWS*1..3]-(b:Agent)
WHERE ALL(n IN nodes(path) WHERE n.age > 25)
RETURN b
```

#### Use WITH for Query Pipelining

```cypher
-- Pipeline operations for better performance
MATCH (a:Agent {id: $agent_id})-[r:KNOWS]-(b:Agent)
WITH b, r ORDER BY r.strength DESC LIMIT 100
MATCH (b)-[:LOCATED_AT]->(l:Location)
RETURN b, l
```

### 3. Memory Configuration

```properties
# neo4j.conf optimizations
dbms.memory.heap.initial_size=8g
dbms.memory.heap.max_size=8g
dbms.memory.pagecache.size=16g
dbms.memory.off_heap.max_size=4g

# Query cache
dbms.query_cache_size=1000
cypher.query_max_allocations=10000000

# Thread pool
dbms.threads.worker_count=100
```

## Caching Strategy

### 1. Multi-Level Cache Architecture

```python
class CacheManager:
    """Multi-level caching system."""
    
    def __init__(self):
        # L1: In-memory cache (fastest, smallest)
        self.l1_cache = LRUCache(max_size=10000, ttl=60)
        
        # L2: Redis cache (fast, medium)
        self.l2_cache = RedisCache(ttl=300)
        
        # L3: Neo4j (source of truth)
        self.graph = Neo4jClient()
```

### 2. Cache Key Patterns

```python
class CacheKeys:
    """Standardized cache key patterns."""
    
    @staticmethod
    def agent_key(agent_id: int) -> str:
        return f"agent:{agent_id}"
    
    @staticmethod
    def relationships_key(agent_id: int, rel_type: str = None) -> str:
        if rel_type:
            return f"rels:{agent_id}:{rel_type}"
        return f"rels:{agent_id}:all"
    
    @staticmethod
    def community_key(agent_id: int) -> str:
        return f"community:{agent_id}"
    
    @staticmethod
    def influence_key(agent_id: int) -> str:
        return f"influence:{agent_id}"
```

### 3. Cache Warming

```python
class CacheWarmer:
    """Proactive cache warming strategies."""
    
    async def warm_social_cache(self, agent_id: int):
        """Warm cache for agent's social network."""
        # Pre-load agent data
        agent = await self.graph.get_agent(agent_id)
        await self.cache.set(f"agent:{agent_id}", agent)
        
        # Pre-load immediate relationships
        relationships = await self.graph.get_relationships(agent_id)
        await self.cache.set(f"rels:{agent_id}:all", relationships)
        
        # Pre-load friends' basic data
        for rel in relationships[:20]:  # Top 20 relationships
            friend = await self.graph.get_agent(rel['target_id'])
            await self.cache.set(f"agent:{rel['target_id']}", friend)
```

## Batch Processing

### 1. Batch Write Optimization

```python
class BatchProcessor:
    """Optimized batch processing."""
    
    def __init__(self, batch_size: int = 1000):
        self.batch_size = batch_size
        self.write_buffer = []
        self.lock = asyncio.Lock()
        
    async def add_update(self, update: Dict):
        """Add update to batch buffer."""
        async with self.lock:
            self.write_buffer.append(update)
            
            if len(self.write_buffer) >= self.batch_size:
                await self._flush()
    
    async def _flush(self):
        """Flush batch to Neo4j."""
        if not self.write_buffer:
            return
            
        # Group by operation type
        grouped = self._group_by_operation(self.write_buffer)
        
        # Execute each group in parallel
        tasks = []
        for op_type, updates in grouped.items():
            task = self._execute_batch(op_type, updates)
            tasks.append(task)
            
        await asyncio.gather(*tasks)
        self.write_buffer.clear()
```

### 2. Batch Read Optimization

```python
async def batch_get_agents(agent_ids: List[int]) -> Dict[int, Dict]:
    """Efficiently get multiple agents."""
    
    # Check cache first
    cached = {}
    missing = []
    
    for agent_id in agent_ids:
        cached_data = await cache.get(f"agent:{agent_id}")
        if cached_data:
            cached[agent_id] = cached_data
        else:
            missing.append(agent_id)
    
    # Batch fetch missing
    if missing:
        query = """
        UNWIND $agent_ids as agent_id
        MATCH (a:Agent {id: agent_id})
        RETURN a
        """
        results = await graph.query(query, {"agent_ids": missing})
        
        # Update cache
        for result in results:
            agent = result['a']
            cached[agent['id']] = agent
            await cache.set(f"agent:{agent['id']}", agent)
    
    return cached
```

## Query Patterns

### 1. Pagination Strategy

```python
async def paginate_relationships(agent_id: int, 
                               page_size: int = 100,
                               cursor: str = None) -> Dict:
    """Cursor-based pagination for relationships."""
    
    query = """
    MATCH (a:Agent {id: $agent_id})-[r]-(b:Agent)
    WHERE r.strength > 0
    AND ($cursor IS NULL OR elementId(r) > $cursor)
    RETURN r, b
    ORDER BY elementId(r)
    LIMIT $page_size
    """
    
    results = await graph.query(query, {
        "agent_id": agent_id,
        "cursor": cursor,
        "page_size": page_size
    })
    
    # Extract cursor for next page
    next_cursor = None
    if len(results) == page_size:
        next_cursor = results[-1]['elementId(r)']
    
    return {
        "data": results,
        "next_cursor": next_cursor,
        "has_more": next_cursor is not None
    }
```

### 2. Projection Optimization

```cypher
-- Only return needed fields
MATCH (a:Agent {id: $id})-[r:KNOWS]-(b:Agent)
RETURN b.id, b.name, r.strength  -- Not b{.*}
```

### 3. Aggregation Optimization

```cypher
-- Use aggregation functions efficiently
MATCH (a:Agent {id: $id})-[r]-(b:Agent)
WITH type(r) as rel_type,
     COUNT(b) as count,
     AVG(r.strength) as avg_strength,
     COLLECT(b.id)[..10] as sample_ids  -- Limit collection size
RETURN rel_type, count, avg_strength, sample_ids
```

## Connection Pooling

### 1. Pool Configuration

```python
class ConnectionPoolConfig:
    """Neo4j connection pool configuration."""
    
    # Connection pool settings
    MAX_CONNECTION_POOL_SIZE = 100
    CONNECTION_ACQUISITION_TIMEOUT = 60  # seconds
    MAX_CONNECTION_LIFETIME = 3600  # 1 hour
    CONNECTION_TIMEOUT = 30  # seconds
    
    # Retry settings
    MAX_RETRY_TIME = 30  # seconds
    INITIAL_RETRY_DELAY = 1  # second
    RETRY_DELAY_MULTIPLIER = 2.0
    RETRY_DELAY_JITTER = 0.2
```

### 2. Connection Management

```python
class ConnectionManager:
    """Manage Neo4j connections efficiently."""
    
    def __init__(self, config: ConnectionPoolConfig):
        self.driver = AsyncGraphDatabase.driver(
            config.uri,
            auth=(config.user, config.password),
            max_connection_pool_size=config.MAX_CONNECTION_POOL_SIZE,
            connection_acquisition_timeout=config.CONNECTION_ACQUISITION_TIMEOUT,
            max_connection_lifetime=config.MAX_CONNECTION_LIFETIME,
            connection_timeout=config.CONNECTION_TIMEOUT
        )
        self._health_check_task = None
        
    async def health_check(self):
        """Periodic health check of connections."""
        while True:
            try:
                async with self.driver.session() as session:
                    await session.run("RETURN 1")
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                # Implement alerting
            
            await asyncio.sleep(30)  # Check every 30 seconds
```

## Monitoring and Metrics

### 1. Performance Metrics

```python
class PerformanceMonitor:
    """Monitor Neo4j performance metrics."""
    
    def __init__(self):
        self.metrics = {
            "query_count": Counter("neo4j_queries_total"),
            "query_duration": Histogram("neo4j_query_duration_seconds"),
            "cache_hits": Counter("neo4j_cache_hits_total"),
            "cache_misses": Counter("neo4j_cache_misses_total"),
            "connection_pool_size": Gauge("neo4j_connection_pool_size"),
            "active_transactions": Gauge("neo4j_active_transactions")
        }
    
    @contextmanager
    def track_query(self, query_type: str):
        """Track query execution time."""
        start = time.time()
        self.metrics["query_count"].labels(type=query_type).inc()
        
        try:
            yield
        finally:
            duration = time.time() - start
            self.metrics["query_duration"].labels(type=query_type).observe(duration)
```

### 2. Slow Query Detection

```python
class SlowQueryDetector:
    """Detect and log slow queries."""
    
    def __init__(self, threshold_ms: float = 1000):
        self.threshold_ms = threshold_ms
        
    async def analyze_slow_queries(self):
        """Analyze slow queries from Neo4j logs."""
        query = """
        CALL dbms.listQueries() 
        YIELD query, elapsedTimeMillis, planning
        WHERE elapsedTimeMillis > $threshold
        RETURN query, elapsedTimeMillis, planning
        ORDER BY elapsedTimeMillis DESC
        """
```

## Best Practices

### 1. Query Best Practices

- **Use parameters**: Always use parameters instead of string concatenation
- **Limit early**: Apply filters as early as possible in the query
- **Profile queries**: Use `PROFILE` to understand query execution
- **Avoid cartesian products**: Be careful with multiple MATCH clauses
- **Use EXISTS**: Prefer EXISTS over pattern matching for existence checks

### 2. Transaction Best Practices

- **Keep transactions short**: Long transactions block resources
- **Batch similar operations**: Group similar updates together
- **Use write transactions sparingly**: Read transactions are cheaper
- **Handle retries**: Implement exponential backoff for failed transactions

### 3. Data Modeling Best Practices

- **Denormalize when needed**: Store frequently accessed data on nodes
- **Use relationship properties**: Store relationship-specific data on edges
- **Limit relationship types**: Too many types hurt performance
- **Consider bi-directional relationships**: For symmetric relationships

## Scalability Considerations

### 1. Horizontal Scaling

```yaml
# Neo4j cluster configuration
neo4j-cluster:
  core-servers: 3  # Minimum for HA
  read-replicas: 5  # Scale based on read load
  
  routing:
    policy: "least-connected"
    sticky-sessions: true
```

### 2. Sharding Strategy

For extreme scale (>100M nodes):

```python
class ShardingStrategy:
    """Shard agents across multiple databases."""
    
    def get_shard(self, agent_id: int) -> str:
        """Determine shard for agent."""
        # Simple modulo sharding
        shard_count = 10
        shard_id = agent_id % shard_count
        return f"neo4j-shard-{shard_id}"
    
    def get_cross_shard_query(self, agent_ids: List[int]) -> Dict[str, List[int]]:
        """Group agents by shard for cross-shard queries."""
        shards = {}
        for agent_id in agent_ids:
            shard = self.get_shard(agent_id)
            if shard not in shards:
                shards[shard] = []
            shards[shard].append(agent_id)
        return shards
```