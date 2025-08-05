# API Specifications

## Overview

This document defines the APIs for interacting with the Neo4j graph database in AgentGraphSociety, including client interfaces, query methods, and integration points.

## Neo4j Client API

### 1. Core Client Class

```python
from neo4j import AsyncGraphDatabase
from typing import Optional, Dict, List, Any
import asyncio
from datetime import datetime

class Neo4jClient:
    """
    Async Neo4j client for AgentGraphSociety.
    
    Features:
    - Connection pooling
    - Transaction management
    - Query caching
    - Error handling
    """
    
    def __init__(self, uri: str, user: str, password: str, 
                 database: str = "neo4j", pool_size: int = 50):
        """
        Initialize Neo4j client.
        
        Args:
            uri: Neo4j connection URI (bolt://localhost:7687)
            user: Username
            password: Password
            database: Database name
            pool_size: Connection pool size
        """
        self.driver = AsyncGraphDatabase.driver(
            uri, 
            auth=(user, password),
            max_connection_pool_size=pool_size
        )
        self.database = database
        
    async def close(self):
        """Close the driver connection."""
        await self.driver.close()
        
    async def verify_connectivity(self) -> bool:
        """Verify connection to Neo4j."""
        try:
            async with self.driver.session() as session:
                result = await session.run("RETURN 1 as result")
                record = await result.single()
                return record["result"] == 1
        except Exception:
            return False
```

### 2. Agent Operations API

```python
class AgentGraphOperations:
    """Agent-specific graph operations."""
    
    def __init__(self, client: Neo4jClient):
        self.client = client
        
    # CREATE Operations
    
    async def create_agent(self, agent_data: Dict) -> str:
        """
        Create agent node in graph.
        
        Args:
            agent_data: Dictionary containing agent properties
            
        Returns:
            Neo4j node ID
            
        Example:
            node_id = await create_agent({
                "id": 123,
                "name": "John Doe",
                "age": 30,
                "occupation": "Engineer"
            })
        """
        query = """
        CREATE (a:Agent $properties)
        SET a.created_at = datetime()
        RETURN elementId(a) as node_id
        """
        
    async def batch_create_agents(self, agents: List[Dict]) -> List[str]:
        """Create multiple agents in single transaction."""
        query = """
        UNWIND $agents as agent_data
        CREATE (a:Agent)
        SET a = agent_data
        SET a.created_at = datetime()
        RETURN elementId(a) as node_id
        """
        
    # READ Operations
    
    async def get_agent(self, agent_id: int) -> Optional[Dict]:
        """Get agent by ID."""
        query = """
        MATCH (a:Agent {id: $agent_id})
        RETURN a{.*, relationships: [(a)-[r]-(b:Agent) | {
            agent_id: b.id,
            type: type(r),
            strength: r.strength
        }]}
        """
        
    async def find_agents(self, filters: Dict, 
                         limit: int = 100, 
                         skip: int = 0) -> List[Dict]:
        """Find agents matching filters."""
        # Dynamic query building based on filters
        
    # UPDATE Operations
    
    async def update_agent(self, agent_id: int, 
                          updates: Dict) -> bool:
        """Update agent properties."""
        query = """
        MATCH (a:Agent {id: $agent_id})
        SET a += $updates
        SET a.updated_at = datetime()
        RETURN a
        """
        
    async def update_agent_location(self, agent_id: int, 
                                   location: Dict) -> bool:
        """Update agent's current location."""
        query = """
        MATCH (a:Agent {id: $agent_id})
        OPTIONAL MATCH (a)-[r:LOCATED_AT]->()
        DELETE r
        WITH a
        MATCH (l:Location {id: $location_id})
        CREATE (a)-[:LOCATED_AT {arrival_time: datetime()}]->(l)
        SET a.current_location = point({
            latitude: $lat, 
            longitude: $lng
        })
        """
        
    # DELETE Operations
    
    async def delete_agent(self, agent_id: int, 
                          cascade: bool = False) -> bool:
        """Delete agent and optionally relationships."""
        if cascade:
            query = """
            MATCH (a:Agent {id: $agent_id})
            DETACH DELETE a
            """
        else:
            query = """
            MATCH (a:Agent {id: $agent_id})
            WHERE NOT (a)-[]-()
            DELETE a
            """
```

### 3. Relationship Operations API

```python
class RelationshipGraphOperations:
    """Relationship-specific graph operations."""
    
    # CREATE Operations
    
    async def create_relationship(self, agent1_id: int, agent2_id: int,
                                 rel_type: str, properties: Dict = None) -> bool:
        """
        Create relationship between agents.
        
        Args:
            agent1_id: Source agent ID
            agent2_id: Target agent ID  
            rel_type: Relationship type (KNOWS, FRIEND, FAMILY, COLLEAGUE)
            properties: Relationship properties
            
        Example:
            await create_relationship(123, 456, "FRIEND", {
                "strength": 75,
                "since": datetime.now()
            })
        """
        query = f"""
        MATCH (a:Agent {{id: $agent1_id}}), (b:Agent {{id: $agent2_id}})
        CREATE (a)-[r:{rel_type} $properties]->(b)
        RETURN r
        """
        
    async def create_bidirectional_relationship(self, agent1_id: int, 
                                              agent2_id: int,
                                              rel_type: str, 
                                              properties: Dict = None) -> bool:
        """Create relationship in both directions."""
        
    # READ Operations
    
    async def get_relationships(self, agent_id: int,
                               rel_types: List[str] = None,
                               min_strength: float = 0) -> List[Dict]:
        """
        Get agent's relationships.
        
        Returns:
            List of relationships with properties and target agent info
        """
        type_filter = ""
        if rel_types:
            type_filter = f"WHERE type(r) IN {rel_types}"
            
        query = f"""
        MATCH (a:Agent {{id: $agent_id}})-[r]-(b:Agent)
        {type_filter}
        AND r.strength >= $min_strength
        RETURN {{
            relationship: r{{.*}},
            type: type(r),
            target: b{{.*}},
            direction: CASE 
                WHEN startNode(r) = a THEN 'outgoing'
                ELSE 'incoming'
            END
        }}
        """
        
    async def get_mutual_friends(self, agent1_id: int, 
                               agent2_id: int) -> List[Dict]:
        """Get mutual connections between two agents."""
        query = """
        MATCH (a:Agent {id: $agent1_id})-[:KNOWS|FRIEND]-(mutual:Agent)
              -[:KNOWS|FRIEND]-(b:Agent {id: $agent2_id})
        RETURN DISTINCT mutual
        """
        
    # UPDATE Operations
    
    async def update_relationship_strength(self, agent1_id: int, 
                                         agent2_id: int,
                                         strength_delta: float) -> float:
        """Update relationship strength by delta."""
        query = """
        MATCH (a:Agent {id: $agent1_id})-[r]-(b:Agent {id: $agent2_id})
        SET r.strength = CASE
            WHEN r.strength + $delta > 100 THEN 100
            WHEN r.strength + $delta < 0 THEN 0
            ELSE r.strength + $delta
        END
        SET r.last_interaction = datetime()
        SET r.interaction_count = coalesce(r.interaction_count, 0) + 1
        RETURN r.strength as new_strength
        """
        
    # DELETE Operations
    
    async def remove_relationship(self, agent1_id: int, 
                                agent2_id: int,
                                rel_type: str = None) -> bool:
        """Remove specific relationship or all relationships."""
```

### 4. Query Operations API

```python
class GraphQueryOperations:
    """Complex graph queries and algorithms."""
    
    # Social Network Queries
    
    async def find_friends_of_friends(self, agent_id: int,
                                    max_depth: int = 2,
                                    exclude_existing: bool = True) -> List[Dict]:
        """Find potential friends through network."""
        query = """
        MATCH (a:Agent {id: $agent_id})-[:KNOWS|FRIEND*2..{max_depth}]-(fof:Agent)
        WHERE a <> fof
        AND ($exclude_existing = false OR NOT (a)-[]-(fof))
        WITH fof, COUNT(*) as paths
        RETURN fof, paths
        ORDER BY paths DESC
        LIMIT 20
        """
        
    async def calculate_influence_score(self, agent_id: int) -> float:
        """Calculate agent's influence using PageRank."""
        query = """
        CALL gds.pageRank.stream('social-network', {
            nodeQuery: 'MATCH (n:Agent) RETURN id(n) as id',
            relationshipQuery: 'MATCH (a:Agent)-[r:KNOWS|FRIEND]-(b:Agent) 
                               RETURN id(a) as source, id(b) as target, 
                                      r.strength/100.0 as weight'
        })
        YIELD nodeId, score
        WHERE gds.util.asNode(nodeId).id = $agent_id
        RETURN score
        """
        
    async def detect_communities(self) -> Dict[int, int]:
        """Detect communities using Louvain algorithm."""
        query = """
        CALL gds.louvain.stream('social-network', {
            relationshipWeightProperty: 'strength'
        })
        YIELD nodeId, communityId
        RETURN gds.util.asNode(nodeId).id as agent_id, 
               communityId
        """
        
    # Path Finding
    
    async def find_shortest_social_path(self, source_id: int, 
                                      target_id: int,
                                      min_strength: float = 30) -> Optional[List]:
        """Find shortest path between agents."""
        query = """
        MATCH path = shortestPath(
            (a:Agent {id: $source_id})-[r*]-(b:Agent {id: $target_id})
        )
        WHERE ALL(rel IN relationships(path) 
                 WHERE rel.strength >= $min_strength)
        RETURN [n IN nodes(path) | n.id] as agent_path,
               REDUCE(s = 1.0, rel IN relationships(path) | 
                      s * rel.strength/100) as path_strength
        """
        
    # Analytics Queries
    
    async def get_network_statistics(self, agent_id: int) -> Dict:
        """Get comprehensive network statistics for agent."""
        query = """
        MATCH (a:Agent {id: $agent_id})
        OPTIONAL MATCH (a)-[r]-(friend:Agent)
        WITH a, COUNT(DISTINCT friend) as friend_count,
             AVG(r.strength) as avg_strength
        OPTIONAL MATCH (a)-[:FAMILY]-(family:Agent)
        WITH a, friend_count, avg_strength, 
             COUNT(DISTINCT family) as family_count
        OPTIONAL MATCH (a)-[:COLLEAGUE]-(colleague:Agent)
        RETURN {
            total_connections: friend_count,
            avg_relationship_strength: avg_strength,
            family_members: family_count,
            colleagues: COUNT(DISTINCT colleague),
            clustering_coefficient: gds.alpha.triangleCount.stream(
                {nodeQuery: 'MATCH (n:Agent {id: $agent_id}) RETURN id(n) as id'}
            )
        }
        """
```

### 5. Batch Operations API

```python
class BatchOperations:
    """Batch operations for performance."""
    
    async def batch_update_relationships(self, updates: List[Dict]):
        """
        Batch update multiple relationships.
        
        Args:
            updates: List of update dictionaries containing:
                - agent1_id
                - agent2_id
                - properties
                
        Example:
            await batch_update_relationships([
                {
                    "agent1_id": 123,
                    "agent2_id": 456,
                    "properties": {"strength": 80}
                },
                ...
            ])
        """
        query = """
        UNWIND $updates as update
        MATCH (a:Agent {id: update.agent1_id})-[r]-(b:Agent {id: update.agent2_id})
        SET r += update.properties
        """
        
    async def batch_create_messages(self, messages: List[Dict]):
        """Batch create message nodes and relationships."""
```

### 6. Transaction Management API

```python
class TransactionManager:
    """Manage complex transactions."""
    
    async def execute_transaction(self, operations: List[Dict]) -> bool:
        """
        Execute multiple operations in single transaction.
        
        Example:
            await execute_transaction([
                {
                    "type": "create_agent",
                    "data": {...}
                },
                {
                    "type": "create_relationship",
                    "data": {...}
                }
            ])
        """
        async with self.driver.session() as session:
            async with session.begin_transaction() as tx:
                try:
                    for op in operations:
                        await self._execute_operation(tx, op)
                    await tx.commit()
                    return True
                except Exception as e:
                    await tx.rollback()
                    raise
```

## REST API Endpoints

### 1. Agent Endpoints

```python
# FastAPI example endpoints

@router.get("/agents/{agent_id}")
async def get_agent(agent_id: int):
    """Get agent details including relationships."""
    
@router.post("/agents")
async def create_agent(agent_data: AgentCreate):
    """Create new agent."""
    
@router.put("/agents/{agent_id}")
async def update_agent(agent_id: int, updates: AgentUpdate):
    """Update agent properties."""
    
@router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: int):
    """Delete agent."""
```

### 2. Relationship Endpoints

```python
@router.get("/agents/{agent_id}/relationships")
async def get_relationships(
    agent_id: int,
    rel_type: Optional[str] = None,
    min_strength: Optional[float] = 0
):
    """Get agent's relationships."""
    
@router.post("/relationships")
async def create_relationship(rel_data: RelationshipCreate):
    """Create new relationship."""
    
@router.put("/relationships/{agent1_id}/{agent2_id}")
async def update_relationship(
    agent1_id: int,
    agent2_id: int,
    updates: RelationshipUpdate
):
    """Update relationship properties."""
```

### 3. Analytics Endpoints

```python
@router.get("/analytics/influence/{agent_id}")
async def get_influence_score(agent_id: int):
    """Get agent's influence score."""
    
@router.get("/analytics/communities")
async def detect_communities():
    """Detect social communities."""
    
@router.get("/analytics/path/{source_id}/{target_id}")
async def find_social_path(source_id: int, target_id: int):
    """Find path between agents."""
```

## Error Handling

```python
class GraphError(Exception):
    """Base exception for graph operations."""
    
class NodeNotFoundError(GraphError):
    """Agent node not found."""
    
class RelationshipNotFoundError(GraphError):
    """Relationship not found."""
    
class ConstraintViolationError(GraphError):
    """Graph constraint violated."""
    
class TransactionError(GraphError):
    """Transaction failed."""
```

## Performance Considerations

1. **Connection Pooling**: Default 50 connections
2. **Query Timeout**: 30 seconds default
3. **Batch Size**: 1000 nodes/relationships per batch
4. **Cache TTL**: 5 minutes for read queries
5. **Index Usage**: All queries must use indexes