# Configuration System Specification

## Overview

This document specifies the configuration system for AgentGraphSociety with Neo4j integration, psychological modeling, behavioral economics, and information access features. The configuration supports multiple deployment scenarios including local Docker, cloud Neo4j, and various feature toggles.

## Configuration Structure

The configuration uses a hierarchical YAML/JSON structure with environment variable override support.

### 1. Main Configuration File

**File**: `config/agentsociety.yaml` (or `.json`)

```yaml
# AgentGraphSociety Configuration
version: "2.0"
environment: "development"  # development, staging, production

# Core System Configuration
system:
  name: "AgentGraphSociety"
  debug: true
  log_level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  timezone: "UTC"
  random_seed: null  # Set for reproducible simulations

# Neo4j Database Configuration
neo4j:
  enabled: true
  
  # Connection Settings
  connection:
    # Option 1: Direct connection
    uri: "bolt://localhost:7687"
    # Option 2: Docker connection
    docker:
      enabled: false
      container_name: "agentsociety-neo4j"
      image: "neo4j:5.15-enterprise"
      ports:
        bolt: 7687
        http: 7474
        https: 7473
    # Option 3: Neo4j Aura (cloud)
    aura:
      enabled: false
      uri: "${NEO4J_AURA_URI}"
      
  # Authentication
  auth:
    username: "${NEO4J_USERNAME:-neo4j}"
    password: "${NEO4J_PASSWORD}"
    
  # Database Configuration
  database:
    name: "agentsociety"
    
  # Connection Pool Settings
  pool:
    max_connection_lifetime: 3600  # seconds
    max_connection_pool_size: 100
    connection_acquisition_timeout: 60  # seconds
    
  # Performance Settings
  performance:
    query_timeout: 30  # seconds
    batch_size: 1000
    cache_enabled: true
    cache_ttl: 3600  # seconds
    
  # Graph Data Science (GDS) Settings
  gds:
    enabled: true
    memory_estimation: true
    algorithms:
      pagerank:
        enabled: true
        dampingFactor: 0.85
        maxIterations: 20
      community_detection:
        enabled: true
        algorithm: "louvain"  # louvain, label_propagation
      pathfinding:
        enabled: true
        algorithm: "dijkstra"  # dijkstra, astar

# Psychological Modeling Configuration
psychology:
  enabled: true
  
  # Personality System
  personality:
    model: "big_five"  # Currently only big_five supported
    
    # Distribution parameters for population
    distributions:
      openness:
        type: "beta"
        alpha: 5
        beta: 5
      conscientiousness:
        type: "beta"
        alpha: 5
        beta: 5
      extraversion:
        type: "beta"
        alpha: 4
        beta: 6  # Slightly introverted population
      agreeableness:
        type: "beta"
        alpha: 6
        beta: 4  # Slightly agreeable population
      neuroticism:
        type: "beta"
        alpha: 5
        beta: 5
    
    # Personality-behavior correlation strengths
    behavior_correlations:
      risk_taking_openness: 0.6
      social_seeking_extraversion: 0.8
      routine_preference_conscientiousness: 0.7
      stress_susceptibility_neuroticism: 0.8
      cooperation_agreeableness: 0.7
  
  # Mental Health System
  mental_health:
    enabled: true
    update_frequency: "daily"  # daily, hourly, continuous
    
    # Baseline levels
    baseline:
      stress_level: 0.3
      life_satisfaction: 0.7
      self_esteem: 0.7
      resilience: 0.6
    
    # Recovery rates
    recovery:
      stress_recovery_rate: 0.05  # Daily recovery
      depression_recovery_rate: 0.02
      burnout_recovery_rate: 0.03
    
    # Intervention thresholds
    intervention_thresholds:
      high_stress: 0.8
      low_satisfaction: 0.3
      depression_risk: 0.7
  
  # Cognitive Biases
  cognitive_biases:
    enabled: true
    
    # Individual bias strengths (can be overridden per agent)
    default_strengths:
      confirmation_bias: 0.4
      anchoring_bias: 0.5
      availability_heuristic: 0.5
      loss_aversion: 0.6
      social_proof: 0.5
      sunk_cost_fallacy: 0.5
      framing_effect: 0.4
      overconfidence: 0.4
    
    # Bias modulation by context
    context_modulation:
      stress_amplification: 0.3  # Biases stronger under stress
      age_reduction: 0.01  # Biases reduce slightly with age
      education_reduction: 0.2  # Education reduces some biases

# Life Dynamics Configuration
life_dynamics:
  enabled: true
  
  # Life Stages
  life_stages:
    transitions:
      childhood_to_young_adult: 18
      young_adult_to_early_career: 25
      early_career_to_established: 35
      established_to_midlife: 45
      midlife_to_pre_retirement: 55
      pre_retirement_to_retirement: 65
      retirement_to_elderly: 75
    
    # Stage-specific behavior modifiers
    stage_modifiers:
      young_adult:
        risk_tolerance: 1.3
        social_need: 1.4
        career_focus: 1.2
      established:
        family_focus: 1.5
        financial_planning: 1.3
        risk_tolerance: 0.8
      retirement:
        social_need: 1.2
        health_focus: 1.5
        risk_tolerance: 0.6
  
  # Life Events
  life_events:
    enabled: true
    
    # Event probabilities (annual)
    base_probabilities:
      marriage: 0.05
      divorce: 0.02
      child_birth: 0.03
      job_change: 0.1
      job_loss: 0.05
      major_illness: 0.02
      house_purchase: 0.04
      retirement: 0.02
    
    # Event cascade settings
    cascade_enabled: true
    max_cascade_depth: 3
    cascade_delay_days: [30, 180]  # Random delay between min and max
  
  # Goals System
  goals:
    enabled: true
    max_active_goals: 5
    
    # Goal categories and priorities
    categories:
      career:
        base_priority: 0.7
        personality_modifiers:
          conscientiousness: 0.3
          openness: 0.2
      family:
        base_priority: 0.8
        personality_modifiers:
          agreeableness: 0.3
          tradition_value: 0.2
      financial:
        base_priority: 0.6
        personality_modifiers:
          conscientiousness: 0.4
          security_value: 0.3
      personal:
        base_priority: 0.5
        personality_modifiers:
          openness: 0.4
          autonomy_value: 0.3

# Behavioral Economics Configuration
behavioral_economics:
  enabled: true
  
  # Bounded Rationality
  bounded_rationality:
    cognitive_load_threshold: 0.7
    information_processing_limit: 7  # Miller's law
    decision_quality_degradation: 0.5  # Quality loss at max load
  
  # Prospect Theory
  prospect_theory:
    # Probability weighting
    probability_weighting_gamma: 0.61
    
    # Value function parameters
    gain_alpha: 0.88
    loss_beta: 0.88
    loss_aversion_lambda: 2.25
  
  # Temporal Discounting
  temporal_discounting:
    base_discount_rate: 0.1  # Annual
    present_bias_beta: 0.7
    personality_modulation:
      conscientiousness_effect: -0.3  # More patient
      neuroticism_effect: 0.2  # Less patient
  
  # Social Economics
  social_economics:
    fairness_preference_base: 0.5
    reciprocity_strength: 0.6
    inequality_aversion:
      advantageous: 0.5  # Guilt from having more
      disadvantageous: 1.0  # Envy from having less

# Information Access System Configuration
information_access:
  enabled: true
  
  # MCP Server Configuration
  mcp_servers:
    # Global MCP servers (available to all agents)
    global:
      market_data:
        uri: "mcp://market-data-server:8080"
        auth_required: false
        cache_ttl: 300  # 5 minutes
      news_feed:
        uri: "mcp://news-server:8080"
        auth_required: false
        cache_ttl: 3600  # 1 hour
    
    # Profession-specific MCP servers
    professional:
      hairdresser:
        salon_management:
          uri: "mcp://salon-systems:8080"
          auth_required: true
          data_types: ["appointments", "inventory", "finances"]
        beauty_trends:
          uri: "mcp://beauty-intel:8080"
          auth_required: true
          data_types: ["trends", "techniques", "products"]
      
      doctor:
        medical_records:
          uri: "mcp://ehr-system:8080"
          auth_required: true
          encryption_required: true
          data_types: ["patient_records", "prescriptions"]
        medical_research:
          uri: "mcp://medical-db:8080"
          auth_required: true
          data_types: ["research", "protocols", "guidelines"]
  
  # Information Sharing Rules
  sharing_rules:
    relationship_based:
      spouse:
        financial: 
          min_relationship_strength: 80
          share_level: "summary"
        health:
          min_relationship_strength: 70
          share_level: "full"
      business_partner:
        business_financial:
          min_relationship_strength: 0  # Always share
          share_level: "relevant"
        personal:
          min_relationship_strength: 90
          share_level: "limited"
    
    # Professional access rules
    professional_access:
      doctor_patient:
        medical_history: "full"
        personal_life: "relevant_only"
      hairdresser_client:
        style_preferences: "full"
        personal_info: "limited"
  
  # Privacy Settings
  privacy:
    default_sharing: "none"  # none, limited, summary, full
    audit_access: true  # Log all information access
    consent_required: true  # Require consent for sharing
    data_retention_days: 365

# Agent Population Configuration
population:
  # Initial population settings
  initial_count: 1000
  
  # Demographics
  demographics:
    age_distribution:
      type: "normal"
      mean: 40
      std: 15
      min: 18
      max: 85
    
    gender_distribution:
      male: 0.49
      female: 0.49
      other: 0.02
    
    occupation_distribution:
      # Professional
      doctor: 0.02
      lawyer: 0.02
      teacher: 0.05
      engineer: 0.08
      
      # Service
      hairdresser: 0.03
      restaurant_owner: 0.02
      retail_worker: 0.1
      
      # Other
      office_worker: 0.3
      manual_laborer: 0.15
      unemployed: 0.05
      retired: 0.15
      student: 0.03
  
  # Social Network Generation
  social_network:
    # Initial connections
    friends_per_agent:
      min: 2
      max: 15
      distribution: "power_law"
    
    # Family generation
    family_generation:
      marriage_rate: 0.5
      children_per_family:
        min: 0
        max: 4
        distribution: "poisson"
        lambda: 1.8
    
    # Professional networks
    professional_connections:
      same_profession_bias: 0.7
      connection_probability: 0.1

# Migration Configuration
migration:
  # Migration from old system
  from_legacy:
    enabled: false
    preserve_ids: true
    
    # Personality generation for existing agents
    personality_generation:
      method: "random"  # random, infer_from_behavior, default
      
    # Life stage assignment
    life_stage_assignment:
      method: "age_based"  # age_based, random
    
    # Batch settings
    batch_size: 1000
    parallel_workers: 4
  
  # Feature rollout
  feature_rollout:
    strategy: "percentage"  # percentage, whitelist, gradual
    
    neo4j:
      enabled_percentage: 100
      
    psychology:
      enabled_percentage: 100
      
    behavioral_economics:
      enabled_percentage: 50
      
    information_access:
      enabled_percentage: 25

# Performance Configuration
performance:
  # Caching
  caching:
    enabled: true
    provider: "redis"  # redis, memory
    
    redis:
      host: "localhost"
      port: 6379
      db: 0
      password: "${REDIS_PASSWORD}"
    
    ttl_settings:
      agent_data: 300  # 5 minutes
      relationships: 600  # 10 minutes
      graph_queries: 3600  # 1 hour
      mcp_data: 1800  # 30 minutes
  
  # Parallel Processing
  parallel_processing:
    enabled: true
    max_workers: 8
    chunk_size: 100
  
  # Resource Limits
  resource_limits:
    max_memory_gb: 16
    max_cpu_percent: 80
    query_timeout_seconds: 30

# Monitoring and Logging
monitoring:
  # Metrics Collection
  metrics:
    enabled: true
    provider: "prometheus"  # prometheus, datadog, cloudwatch
    
    export_interval: 60  # seconds
    
    endpoints:
      prometheus:
        port: 9090
        path: "/metrics"
  
  # Logging
  logging:
    # Log files
    file:
      enabled: true
      path: "logs/agentsociety.log"
      rotation: "daily"  # daily, size, time
      retention_days: 30
      
    # Structured logging
    structured:
      enabled: true
      format: "json"  # json, logfmt
      
    # Log levels per module
    module_levels:
      neo4j: "INFO"
      psychology: "DEBUG"
      behavioral_economics: "INFO"
      information_access: "INFO"
      
  # Alerting
  alerting:
    enabled: true
    
    channels:
      email:
        enabled: false
        smtp_server: "${SMTP_SERVER}"
        recipients: ["admin@agentsociety.com"]
      
      slack:
        enabled: false
        webhook_url: "${SLACK_WEBHOOK}"
    
    # Alert rules
    rules:
      - name: "high_memory_usage"
        condition: "memory_usage > 90%"
        severity: "critical"
        
      - name: "slow_queries"
        condition: "query_time > 5s"
        severity: "warning"
        
      - name: "agent_errors"
        condition: "error_rate > 5%"
        severity: "error"

# Development Settings
development:
  # Debug features
  debug:
    enabled: true
    verbose_logging: true
    query_explain: true
    
  # Testing
  testing:
    seed_data: true
    deterministic_random: true
    time_acceleration: 10  # 10x speed for testing
    
  # Development tools
  tools:
    neo4j_browser: true
    api_documentation: true
    performance_profiler: true
```

### 2. Environment-Specific Overrides

**File**: `config/environments/production.yaml`

```yaml
# Production-specific overrides
environment: "production"

system:
  debug: false
  log_level: "WARNING"

neo4j:
  connection:
    aura:
      enabled: true
      uri: "${NEO4J_PRODUCTION_URI}"
  
  performance:
    query_timeout: 60
    cache_ttl: 7200  # 2 hours in production

psychology:
  mental_health:
    update_frequency: "hourly"  # More responsive in production

performance:
  caching:
    provider: "redis"
    redis:
      host: "${REDIS_CLUSTER_ENDPOINT}"
      
monitoring:
  alerting:
    enabled: true
    channels:
      email:
        enabled: true
      slack:
        enabled: true
```

### 3. Docker Compose Integration

**File**: `docker-compose.yaml`

```yaml
version: '3.8'

services:
  neo4j:
    image: neo4j:5.15-enterprise
    environment:
      - NEO4J_AUTH=${NEO4J_USERNAME}/${NEO4J_PASSWORD}
      - NEO4J_ACCEPT_LICENSE_AGREEMENT=yes
      - NEO4J_dbms_memory_pagecache_size=2G
      - NEO4J_dbms_memory_heap_max__size=2G
      - NEO4JLABS_PLUGINS=["graph-data-science"]
    ports:
      - "7474:7474"  # HTTP
      - "7687:7687"  # Bolt
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
      - ./config/neo4j.conf:/conf/neo4j.conf
    networks:
      - agentsociety
  
  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - agentsociety
  
  agentsociety:
    build: .
    environment:
      - CONFIG_FILE=/app/config/agentsociety.yaml
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USERNAME=${NEO4J_USERNAME}
      - NEO4J_PASSWORD=${NEO4J_PASSWORD}
      - REDIS_HOST=redis
      - REDIS_PASSWORD=${REDIS_PASSWORD}
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
    depends_on:
      - neo4j
      - redis
    networks:
      - agentsociety

volumes:
  neo4j_data:
  neo4j_logs:
  redis_data:

networks:
  agentsociety:
    driver: bridge
```

### 4. Configuration Loading System

```python
class ConfigurationManager:
    """Manages configuration loading and validation."""
    
    def __init__(self, config_path: str = "config/agentsociety.yaml"):
        self.config_path = config_path
        self.config = {}
        self.env_overrides = {}
        
    def load_configuration(self) -> Dict[str, Any]:
        """Load configuration with environment overrides."""
        # Load base configuration
        self.config = self._load_yaml(self.config_path)
        
        # Load environment-specific overrides
        env = os.getenv("AGENTSOCIETY_ENV", "development")
        env_config_path = f"config/environments/{env}.yaml"
        if os.path.exists(env_config_path):
            env_config = self._load_yaml(env_config_path)
            self.config = self._deep_merge(self.config, env_config)
        
        # Apply environment variable overrides
        self._apply_env_overrides()
        
        # Validate configuration
        self._validate_configuration()
        
        return self.config
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides."""
        # Neo4j overrides
        if neo4j_uri := os.getenv("NEO4J_URI"):
            self._set_nested(self.config, "neo4j.connection.uri", neo4j_uri)
        
        if neo4j_user := os.getenv("NEO4J_USERNAME"):
            self._set_nested(self.config, "neo4j.auth.username", neo4j_user)
            
        if neo4j_pass := os.getenv("NEO4J_PASSWORD"):
            self._set_nested(self.config, "neo4j.auth.password", neo4j_pass)
    
    def _validate_configuration(self):
        """Validate configuration completeness and consistency."""
        # Check required fields
        required_fields = [
            "neo4j.auth.password",
            "system.name",
            "population.initial_count"
        ]
        
        for field in required_fields:
            if not self._get_nested(self.config, field):
                raise ConfigurationError(f"Required field missing: {field}")
        
        # Validate value ranges
        if self.config["population"]["initial_count"] < 1:
            raise ConfigurationError("Population must be at least 1")
        
        # Validate feature dependencies
        if self.config["life_dynamics"]["enabled"]:
            if not self.config["psychology"]["enabled"]:
                raise ConfigurationError(
                    "Life dynamics requires psychology to be enabled"
                )
```

### 5. Feature Toggle System

```python
class FeatureToggle:
    """Manage feature toggles for gradual rollout."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.rollout_config = config.get("migration", {}).get("feature_rollout", {})
        
    def is_enabled_for_agent(self, feature: str, agent_id: int) -> bool:
        """Check if feature is enabled for specific agent."""
        if not self._is_feature_enabled_globally(feature):
            return False
            
        strategy = self.rollout_config.get("strategy", "percentage")
        
        if strategy == "percentage":
            percentage = self.rollout_config.get(feature, {}).get("enabled_percentage", 0)
            # Use consistent hashing for stable assignment
            return (agent_id % 100) < percentage
            
        elif strategy == "whitelist":
            whitelist = self.rollout_config.get(feature, {}).get("whitelist", [])
            return agent_id in whitelist
            
        elif strategy == "gradual":
            # Gradually enable over time
            start_date = self.rollout_config.get(feature, {}).get("start_date")
            full_rollout_days = self.rollout_config.get(feature, {}).get("days", 30)
            return self._calculate_gradual_rollout(start_date, full_rollout_days, agent_id)
            
        return False
    
    def _is_feature_enabled_globally(self, feature: str) -> bool:
        """Check if feature is enabled at all."""
        feature_map = {
            "neo4j": "neo4j.enabled",
            "psychology": "psychology.enabled",
            "behavioral_economics": "behavioral_economics.enabled",
            "information_access": "information_access.enabled"
        }
        
        config_path = feature_map.get(feature)
        if not config_path:
            return False
            
        return self._get_nested(self.config, config_path, False)
```

### 6. Dynamic Configuration Updates

```python
class DynamicConfigManager:
    """Allow runtime configuration updates without restart."""
    
    def __init__(self, config_manager: ConfigurationManager):
        self.config_manager = config_manager
        self.update_handlers = {}
        self.last_update_check = time.time()
        
    def register_update_handler(self, path: str, handler: Callable):
        """Register handler for configuration updates."""
        self.update_handlers[path] = handler
        
    async def check_for_updates(self):
        """Check for configuration updates periodically."""
        current_time = time.time()
        if current_time - self.last_update_check < 60:  # Check every minute
            return
            
        # Check if config file was modified
        if self._config_file_modified():
            await self._reload_configuration()
            
        # Check for remote configuration updates (if enabled)
        if self.config_manager.config.get("configuration", {}).get("remote_updates"):
            await self._check_remote_updates()
            
        self.last_update_check = current_time
    
    async def _reload_configuration(self):
        """Reload configuration and notify handlers."""
        old_config = self.config_manager.config.copy()
        new_config = self.config_manager.load_configuration()
        
        # Find changes and notify handlers
        changes = self._find_changes(old_config, new_config)
        for path, (old_value, new_value) in changes.items():
            if handler := self.update_handlers.get(path):
                await handler(old_value, new_value)
```

## Usage Examples

### 1. Basic Setup

```python
# Load configuration
config_manager = ConfigurationManager()
config = config_manager.load_configuration()

# Initialize Neo4j connection
neo4j_client = Neo4jClient(
    uri=config["neo4j"]["connection"]["uri"],
    username=config["neo4j"]["auth"]["username"],
    password=config["neo4j"]["auth"]["password"],
    database=config["neo4j"]["database"]["name"]
)

# Initialize feature toggles
feature_toggle = FeatureToggle(config)

# Create agent with features
agent = Agent(id=1001)
if feature_toggle.is_enabled_for_agent("psychology", agent.id):
    agent.enable_psychology(config["psychology"])
if feature_toggle.is_enabled_for_agent("behavioral_economics", agent.id):
    agent.enable_behavioral_economics(config["behavioral_economics"])
```

### 2. Docker Deployment

```bash
# Set environment variables
export NEO4J_USERNAME=neo4j
export NEO4J_PASSWORD=secure_password
export REDIS_PASSWORD=redis_password

# Start services
docker-compose up -d

# Check services
docker-compose ps

# View logs
docker-compose logs -f agentsociety
```

### 3. Production Deployment

```bash
# Set production environment
export AGENTSOCIETY_ENV=production
export NEO4J_PRODUCTION_URI=neo4j+s://xxxxx.databases.neo4j.io
export NEO4J_USERNAME=neo4j
export NEO4J_PASSWORD=production_password

# Run with production config
python -m agentsociety.main --config config/agentsociety.yaml
```

This configuration system provides:

1. **Flexible deployment options** - Local, Docker, or cloud Neo4j
2. **Feature toggles** - Gradual rollout of new features
3. **Environment overrides** - Different settings for dev/staging/prod
4. **Dynamic updates** - Change configuration without restart
5. **Performance tuning** - Caching, pooling, and optimization settings
6. **Comprehensive monitoring** - Metrics, logging, and alerting

The system is designed to be both powerful for complex deployments and simple for getting started with sensible defaults.