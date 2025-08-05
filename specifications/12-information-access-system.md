# Information Access System Specification

## Overview

This document specifies the information access and knowledge management system for AgentGraphSociety, enabling agents to have private information domains, professional knowledge, and role-based data access. Each agent can have their own MCP (Model Context Protocol) servers or data sources that only they (and authorized agents) can access.

## Core Concepts

### 1. Information Domains

Information is organized into domains representing different types of knowledge and data:

```python
class InformationDomain:
    """Represents a specific domain of information."""
    
    def __init__(self):
        self.domain_id: str
        self.domain_type: str  # "professional", "personal", "public", "restricted"
        self.owner_id: int  # Agent who owns this domain
        self.access_level: str  # "private", "shared", "public"
        self.data_sources: List[DataSource]
        self.update_frequency: str  # "real-time", "daily", "weekly"
        
class DataSource:
    """A specific source of information within a domain."""
    
    def __init__(self):
        self.source_id: str
        self.source_type: str  # "mcp", "database", "api", "file", "stream"
        self.connection_info: Dict[str, Any]
        self.data_schema: Dict[str, Any]
        self.refresh_policy: RefreshPolicy
```

### 2. Agent Information Profile

Each agent has an information profile defining what they know and can access:

```python
class AgentInformationProfile:
    """Defines an agent's information access and knowledge."""
    
    def __init__(self):
        # Owned domains (full access)
        self.owned_domains: List[InformationDomain]
        
        # Professional knowledge
        self.professional_knowledge: ProfessionalKnowledge
        
        # Shared access (from relationships)
        self.shared_access: List[SharedAccess]
        
        # Public information awareness
        self.public_info_subscriptions: List[str]
        
        # Information processing capability
        self.info_processing_capacity: float  # 0-1
        self.info_update_frequency: str
        
class ProfessionalKnowledge:
    """Domain-specific professional knowledge."""
    
    def __init__(self):
        self.profession: str
        self.expertise_level: float  # 0-1
        self.specializations: List[str]
        self.knowledge_domains: Dict[str, float]  # domain -> expertise
        self.professional_network_access: List[str]
```

## Implementation Architecture

### 1. MCP Integration for Agents

Each agent can have their own MCP servers providing specialized information:

```python
class AgentMCPManager:
    """Manages MCP connections for individual agents."""
    
    def __init__(self, agent_id: int):
        self.agent_id = agent_id
        self.mcp_servers: Dict[str, MCPServer] = {}
        self.access_permissions: Dict[str, AccessPermission] = {}
        
    async def register_mcp_server(self, 
                                  server_name: str,
                                  server_config: MCPConfig,
                                  access_level: str = "private"):
        """Register an MCP server for this agent."""
        server = await self._create_mcp_connection(server_config)
        self.mcp_servers[server_name] = server
        self.access_permissions[server_name] = AccessPermission(
            owner_id=self.agent_id,
            access_level=access_level,
            shared_with=[]
        )
    
    async def query_mcp(self, 
                       server_name: str, 
                       query: str,
                       requesting_agent_id: int) -> Any:
        """Query an MCP server with access control."""
        # Check permissions
        if not self._has_access(server_name, requesting_agent_id):
            raise AccessDeniedException(
                f"Agent {requesting_agent_id} lacks access to {server_name}"
            )
        
        # Execute query
        server = self.mcp_servers[server_name]
        return await server.query(query)
```

### 2. Information Access Patterns

Different patterns for how agents access and share information:

```python
class InformationAccessPatterns:
    
    @staticmethod
    async def professional_access(agent: Agent, info_type: str) -> Information:
        """Access professional information based on role."""
        if agent.occupation == "hairdresser":
            return await HairdresserInfoAccess.get_info(agent, info_type)
        elif agent.occupation == "doctor":
            return await MedicalInfoAccess.get_info(agent, info_type)
        # ... other professions
    
    @staticmethod
    async def relationship_based_access(agent1: Agent, 
                                      agent2: Agent,
                                      info_domain: str) -> Optional[Information]:
        """Share information based on relationship."""
        relationship = await agent1.get_relationship_with(agent2)
        
        if relationship.type == "spouse" and relationship.strength > 80:
            # High trust - share financial info
            return await agent1.share_private_info(info_domain, level="high")
        elif relationship.type == "business_partner":
            # Share business-related info only
            return await agent1.share_private_info(info_domain, level="business")
        else:
            return None

class HairdresserInfoAccess:
    """Specialized information access for hairdressers."""
    
    @staticmethod
    async def get_info(agent: Agent, info_type: str) -> Information:
        if info_type == "business_financials":
            # Access private business MCP
            return await agent.mcp_manager.query_mcp(
                "salon_business_data",
                "SELECT revenue, expenses, appointments FROM business_data"
            )
        elif info_type == "market_trends":
            # Access industry MCP
            return await agent.mcp_manager.query_mcp(
                "beauty_industry_trends",
                "GET_TRENDS style_preferences, pricing, competition"
            )
        elif info_type == "client_preferences":
            # Access client database
            return await agent.mcp_manager.query_mcp(
                "client_management",
                "SELECT preferences, history FROM clients"
            )
```

### 3. Information Privacy and Sharing

```python
class InformationPrivacyManager:
    """Manages information privacy and sharing rules."""
    
    def __init__(self):
        self.sharing_rules: Dict[str, SharingRule] = {}
        self.access_logs: List[AccessLog] = []
        
    def can_access(self, 
                   requesting_agent: Agent,
                   target_agent: Agent,
                   info_domain: str) -> bool:
        """Check if requesting agent can access target's information."""
        
        # Owner always has access
        if requesting_agent.id == target_agent.id:
            return True
            
        # Check explicit permissions
        if self._has_explicit_permission(requesting_agent, target_agent, info_domain):
            return True
            
        # Check relationship-based access
        relationship = self._get_relationship(requesting_agent, target_agent)
        if self._relationship_grants_access(relationship, info_domain):
            return True
            
        # Check professional access (e.g., doctor-patient)
        if self._has_professional_access(requesting_agent, target_agent, info_domain):
            return True
            
        return False
    
    def _relationship_grants_access(self, 
                                   relationship: Relationship,
                                   info_domain: str) -> bool:
        """Determine if relationship allows information access."""
        
        access_matrix = {
            "spouse": {
                "financial": lambda r: r.strength > 80,
                "health": lambda r: r.strength > 70,
                "professional": lambda r: r.strength > 60
            },
            "business_partner": {
                "business_financial": lambda r: True,
                "personal_financial": lambda r: False,
                "professional": lambda r: True
            },
            "friend": {
                "financial": lambda r: False,
                "health": lambda r: r.strength > 90,
                "professional": lambda r: r.strength > 70
            }
        }
        
        if relationship.type in access_matrix:
            if info_domain in access_matrix[relationship.type]:
                return access_matrix[relationship.type][info_domain](relationship)
        
        return False
```

### 4. Professional Knowledge Systems

Different professions have different information needs and access:

```python
class ProfessionalInformationSystems:
    """Define information systems for different professions."""
    
    PROFESSION_INFO_MAPPING = {
        "hairdresser": {
            "mcp_servers": [
                {
                    "name": "salon_business_data",
                    "type": "business_financial",
                    "data": ["appointments", "revenue", "inventory", "staff"]
                },
                {
                    "name": "beauty_industry_trends", 
                    "type": "market_intelligence",
                    "data": ["styles", "products", "pricing", "competition"]
                },
                {
                    "name": "client_management",
                    "type": "customer_data",
                    "data": ["preferences", "history", "allergies", "contact"]
                }
            ],
            "public_subscriptions": ["fashion_trends", "local_events"],
            "professional_network": "beauty_professionals_network"
        },
        
        "doctor": {
            "mcp_servers": [
                {
                    "name": "patient_records",
                    "type": "medical_records",
                    "data": ["history", "medications", "allergies", "conditions"]
                },
                {
                    "name": "medical_research",
                    "type": "research_database",
                    "data": ["treatments", "studies", "protocols", "guidelines"]
                },
                {
                    "name": "practice_management",
                    "type": "business_medical",
                    "data": ["appointments", "billing", "insurance", "staff"]
                }
            ],
            "public_subscriptions": ["medical_news", "health_alerts"],
            "professional_network": "medical_professionals_network"
        },
        
        "restaurant_owner": {
            "mcp_servers": [
                {
                    "name": "restaurant_operations",
                    "type": "business_operations",
                    "data": ["sales", "inventory", "staff", "schedules"]
                },
                {
                    "name": "supplier_network",
                    "type": "supply_chain",
                    "data": ["prices", "availability", "quality", "delivery"]
                },
                {
                    "name": "customer_analytics",
                    "type": "customer_behavior",
                    "data": ["preferences", "reviews", "frequency", "spending"]
                }
            ],
            "public_subscriptions": ["food_trends", "health_regulations"],
            "professional_network": "restaurant_association"
        }
    }
```

## Neo4j Integration

### 1. Information Domain Nodes

```cypher
(:InformationDomain {
  id: String,
  owner_agent_id: Integer,
  domain_type: String,      // "professional", "personal", "shared"
  domain_name: String,      // "salon_finances", "medical_practice"
  
  // Access control
  access_level: String,     // "private", "restricted", "public"
  requires_permission: Boolean,
  
  // Data characteristics
  data_categories: [String],
  update_frequency: String,
  last_updated: DateTime,
  
  // MCP configuration
  mcp_server_id: String,
  mcp_config: String        // JSON configuration
})
```

### 2. Information Access Relationships

```cypher
// Agent owns information domain
(:Agent)-[:OWNS_INFORMATION {
  acquired_date: DateTime,
  access_rights: String,    // "full", "read", "write"
  can_share: Boolean,
  can_delegate: Boolean
}]->(:InformationDomain)

// Agent has access to information
(:Agent)-[:HAS_ACCESS_TO {
  access_level: String,     // "full", "partial", "read_only"
  granted_by: Integer,      // Agent ID who granted access
  granted_date: DateTime,
  expires_date: DateTime,
  
  // Access conditions
  purpose: String,          // "business", "personal", "professional"
  restrictions: [String]    // Specific restrictions
}]->(:InformationDomain)

// Information sharing between agents
(:Agent)-[:SHARES_INFO_WITH {
  domain_id: String,
  sharing_level: String,    // "full", "partial", "summary"
  
  // Sharing conditions
  condition: String,        // "relationship_based", "professional", "temporary"
  auto_update: Boolean,     // Automatically share updates
  
  // History
  first_shared: DateTime,
  last_shared: DateTime,
  times_accessed: Integer
}]->(:Agent)

// Professional information network
(:Agent)-[:MEMBER_OF_INFO_NETWORK {
  network_name: String,     // "medical_professionals", "beauty_industry"
  membership_level: String, // "basic", "premium", "admin"
  
  // Access rights within network
  can_query: Boolean,
  can_contribute: Boolean,
  reputation_score: Float   // Trust within network
}]->(:ProfessionalNetwork)
```

### 3. Information Query Patterns

```cypher
// Find what information an agent can access
MATCH (agent:Agent {id: $agent_id})-[:OWNS_INFORMATION|HAS_ACCESS_TO]->(domain:InformationDomain)
RETURN domain.domain_name, domain.domain_type, domain.access_level

// Find who agent shares information with
MATCH (agent:Agent {id: $agent_id})-[shares:SHARES_INFO_WITH]->(other:Agent)
RETURN other.name, shares.domain_id, shares.sharing_level, shares.condition

// Find information available through relationships
MATCH (agent:Agent {id: $agent_id})-[rel:KNOWS|FAMILY|COLLEAGUE]->(other:Agent)
WHERE rel.strength > 70
MATCH (other)-[:OWNS_INFORMATION]->(domain:InformationDomain)
WHERE domain.access_level = 'restricted' 
  AND domain.domain_type IN ['personal', 'professional']
RETURN other.name, domain.domain_name, 
       CASE 
         WHEN rel.type = 'FAMILY' AND rel.strength > 80 THEN 'high'
         WHEN rel.type = 'COLLEAGUE' THEN 'professional'
         ELSE 'limited'
       END as potential_access_level
```

## Implementation Considerations

### 1. Information Update Mechanisms

```python
class InformationUpdateSystem:
    """Manages how information is updated and propagated."""
    
    async def update_professional_info(self, agent: Agent):
        """Update agent's professional information."""
        for domain in agent.owned_domains:
            if domain.domain_type == "professional":
                # Query MCP for updates
                updates = await agent.mcp_manager.query_mcp(
                    domain.data_sources[0].source_id,
                    "GET_UPDATES since:" + domain.last_updated
                )
                
                # Process updates
                await self._process_updates(agent, domain, updates)
                
                # Notify agents with shared access
                await self._notify_shared_access(agent, domain, updates)
    
    async def _process_updates(self, agent: Agent, domain: InformationDomain, updates: Any):
        """Process information updates and trigger agent responses."""
        if domain.domain_name == "salon_finances" and updates.revenue_change < -0.2:
            # Significant revenue drop - trigger concern
            await agent.process_life_event(LifeEvent(
                event_type="business_downturn",
                severity=0.6,
                immediate_impacts={"stress_level": 0.3, "financial_worry": 0.4}
            ))
```

### 2. Decision Making with Private Information

```python
class InformedDecisionMaking:
    """Make decisions using private information."""
    
    async def make_business_decision(self, agent: Agent, decision_type: str):
        """Make business decision with private information."""
        
        # Access private business data
        if agent.occupation == "hairdresser":
            financials = await agent.query_private_info("salon_business_data", 
                                                       "financial_summary")
            market_info = await agent.query_private_info("beauty_industry_trends",
                                                        "local_competition")
            
            # Decision based on private information
            if decision_type == "pricing":
                # Agent knows their costs and competition
                if financials.profit_margin < 0.2 and market_info.avg_price > financials.current_price:
                    return Decision("raise_prices", confidence=0.8)
            
            elif decision_type == "expansion":
                # Agent knows their financial position
                if financials.cash_reserves > 50000 and financials.revenue_growth > 0.1:
                    return Decision("expand_business", confidence=0.7)
```

### 3. Information Asymmetry Effects

```python
class InformationAsymmetryEffects:
    """Model effects of information asymmetry on agent interactions."""
    
    async def negotiate_with_asymmetry(self, 
                                     buyer: Agent, 
                                     seller: Agent,
                                     item: str):
        """Negotiation where agents have different information."""
        
        # Seller knows true cost and quality
        seller_info = await seller.query_private_info("inventory", f"item:{item}")
        seller_min_price = seller_info.cost * 1.3  # 30% markup minimum
        
        # Buyer only knows market price
        buyer_info = await buyer.query_public_info("market_prices", f"item:{item}")
        buyer_max_price = buyer_info.avg_price * 1.1  # Willing to pay 10% above average
        
        # Information advantage affects negotiation
        if seller_info.quality == "high" and not buyer.knows_quality:
            # Seller can command premium due to information asymmetry
            final_price = seller_min_price * 1.2
        else:
            # Standard negotiation
            final_price = (seller_min_price + buyer_max_price) / 2
        
        return NegotiationResult(final_price, success=final_price <= buyer_max_price)
```

### 4. Privacy and Trust

```python
class PrivacyTrustDynamics:
    """Manage privacy and trust in information sharing."""
    
    async def request_private_info(self, 
                                 requester: Agent,
                                 owner: Agent,
                                 info_domain: str,
                                 purpose: str) -> bool:
        """Request access to private information."""
        
        # Check relationship
        relationship = await requester.get_relationship_with(owner)
        
        # Trust calculation
        base_trust = relationship.strength / 100
        purpose_modifier = self._get_purpose_trust_modifier(purpose)
        personality_modifier = owner.personality.agreeableness * 0.3
        
        trust_score = base_trust * purpose_modifier + personality_modifier
        
        # Owner's decision based on trust and personality
        if owner.personality.openness > 0.7 and trust_score > 0.5:
            # Open personality more likely to share
            await owner.grant_info_access(requester, info_domain, "temporary")
            return True
        elif trust_score > 0.8:
            # Very high trust overrides personality
            await owner.grant_info_access(requester, info_domain, "restricted")
            return True
        else:
            return False
```

## Example Scenarios

### 1. Hairdresser Business Management

```python
# Hairdresser agent setup
hairdresser = Agent(
    id=1001,
    name="Sarah",
    occupation="hairdresser"
)

# Register private MCP servers
await hairdresser.mcp_manager.register_mcp_server(
    "salon_finances",
    MCPConfig(
        server_type="financial_database",
        connection_string="salon_db://localhost:5432",
        credentials=encrypted_credentials
    ),
    access_level="private"
)

await hairdresser.mcp_manager.register_mcp_server(
    "client_preferences",
    MCPConfig(
        server_type="crm_system",
        api_endpoint="https://salon-crm.com/api",
        api_key=encrypted_key
    ),
    access_level="private"
)

# Business decision based on private information
financial_data = await hairdresser.query_private_info("salon_finances", "monthly_summary")
if financial_data.profit_margin < 0.15:
    # Stress from business pressure
    await hairdresser.update_mental_state(stress_delta=0.2)
    
    # Consider business strategies
    decision = await hairdresser.make_business_decision("cost_reduction")
```

### 2. Information Sharing in Relationships

```python
# Spouse requests financial information
spouse = await hairdresser.get_spouse()
if spouse and await spouse.request_info_access(hairdresser, "salon_finances", "family_planning"):
    # Share summary information
    await hairdresser.share_info_with(
        spouse,
        "salon_finances",
        level="summary",  # Not full details
        duration="1_month"
    )
```

### 3. Professional Network Information

```python
# Hairdresser part of beauty professionals network
await hairdresser.join_professional_network("beauty_professionals_local")

# Query network for market information
market_trends = await hairdresser.query_network_info(
    "beauty_professionals_local",
    "trending_styles_2024"
)

# Make decisions based on network intelligence
if "sustainable_products" in market_trends.top_trends:
    await hairdresser.make_business_decision("stock_eco_products")
```

## Performance Optimization

### 1. Information Caching

```python
class InformationCache:
    """Cache frequently accessed information."""
    
    def __init__(self):
        self.cache = TTLCache(maxsize=1000, ttl=3600)  # 1 hour TTL
        self.access_patterns = defaultdict(int)
        
    async def get_info(self, agent_id: int, domain: str, query: str) -> Any:
        cache_key = f"{agent_id}:{domain}:{query}"
        
        # Track access patterns
        self.access_patterns[cache_key] += 1
        
        # Check cache
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Fetch from source
        result = await self._fetch_from_source(agent_id, domain, query)
        
        # Cache if frequently accessed
        if self.access_patterns[cache_key] > 3:
            self.cache[cache_key] = result
            
        return result
```

### 2. Batch Information Updates

```python
class BatchInfoUpdater:
    """Batch update information for multiple agents."""
    
    async def update_professional_network(self, network_name: str):
        """Update all agents in a professional network."""
        agents = await self.get_network_members(network_name)
        
        # Fetch updates once
        network_updates = await self.fetch_network_updates(network_name)
        
        # Distribute to all members based on their access level
        tasks = []
        for agent in agents:
            if agent.network_membership_level == "premium":
                tasks.append(agent.receive_info_update(network_updates.full))
            else:
                tasks.append(agent.receive_info_update(network_updates.basic))
        
        await asyncio.gather(*tasks)
```

## Testing Scenarios

### 1. Information Asymmetry Tests
- Test negotiations with different information levels
- Verify decision quality with/without key information
- Test information discovery through relationships

### 2. Privacy and Security Tests
- Verify access control enforcement
- Test information leak prevention
- Validate audit trail completeness

### 3. Performance Tests
- Test with 10K+ agents with private information
- Measure query performance with complex access rules
- Test cache effectiveness under load

### 4. Behavioral Realism Tests
- Verify agents use private information appropriately
- Test information sharing follows realistic patterns
- Validate professional knowledge affects decisions correctly