# AgentGraphSociety LLM Server

A dedicated LLM server for AgentGraphSociety that provides a unified API for agent text generation with caching, monitoring, and agent personality integration.

## Features

- **Ollama Integration**: Runs multiple LLMs via Ollama
- **Agent Personality Support**: Incorporates agent personalities into prompts
- **Response Caching**: Redis-based caching to reduce duplicate LLM calls
- **Batch Processing**: Generate responses for multiple agents efficiently
- **Monitoring**: Prometheus metrics and Grafana dashboards
- **Rate Limiting**: Configurable rate limits per API key
- **High Availability**: Health checks and automatic retries

## Quick Start

### 1. Clone and Setup

```bash
cd llm-server
cp .env.example .env
# Edit .env with your settings
```

### 2. Start the Server

```bash
docker-compose up -d
```

This will:
- Start Ollama and download models (mistral:7b, neural-chat:7b, phi-2)
- Launch the LLM Gateway API on port 8080
- Start Redis for caching
- Set up Prometheus and Grafana for monitoring

### 3. Verify Installation

```bash
# Check health
curl http://localhost:8080/health

# List available models
curl -H "X-API-Key: your-api-key" http://localhost:8080/models
```

### 4. Access Monitoring

- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090

## API Usage

### Generate Text

```bash
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "model": "mistral:7b-instruct",
    "prompt": "Hello, how are you?",
    "temperature": 0.7,
    "max_tokens": 200
  }'
```

### Generate with Agent Profile

```bash
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "model": "mistral:7b-instruct",
    "prompt": "What do you think about the weather today?",
    "agent_profile": {
      "agent_id": 1001,
      "name": "Sarah",
      "age": 28,
      "occupation": "hairdresser",
      "personality": {
        "openness": 0.8,
        "conscientiousness": 0.7,
        "extraversion": 0.9,
        "agreeableness": 0.8,
        "neuroticism": 0.3
      },
      "mental_state": {
        "stress_level": 0.2,
        "life_satisfaction": 0.8,
        "current_emotion": "happy"
      },
      "context": "At work in the salon"
    }
  }'
```

### Batch Generation

```bash
curl -X POST http://localhost:8080/batch/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "requests": [
      {
        "model": "mistral:7b-instruct",
        "prompt": "How was your day?",
        "agent_profile": { ... }
      },
      {
        "model": "mistral:7b-instruct",
        "prompt": "What are your plans?",
        "agent_profile": { ... }
      }
    ]
  }'
```

## Integration with AgentGraphSociety

### Configuration

Add to your `agentsociety.yaml`:

```yaml
llm:
  provider: "gateway"
  
  gateway:
    base_url: "http://your-server-ip:8080"
    api_key: "${LLM_API_KEY}"
    timeout: 30
    retry_attempts: 3
    
  models:
    default: "mistral:7b-instruct"
    emotional: "neural-chat:7b"
    fast: "phi-2"
```

### Python Client

```python
from agentsociety.llm import GatewayLLM

class AgentLLMClient:
    def __init__(self, config):
        self.llm = GatewayLLM(
            base_url=config["llm"]["gateway"]["base_url"],
            api_key=config["llm"]["gateway"]["api_key"]
        )
    
    async def generate_response(self, agent, prompt):
        """Generate response for an agent."""
        profile = {
            "agent_id": agent.id,
            "name": agent.name,
            "age": agent.age,
            "occupation": agent.occupation,
            "personality": {
                "openness": agent.personality.openness,
                "conscientiousness": agent.personality.conscientiousness,
                "extraversion": agent.personality.extraversion,
                "agreeableness": agent.personality.agreeableness,
                "neuroticism": agent.personality.neuroticism
            },
            "mental_state": {
                "stress_level": agent.stress_level,
                "life_satisfaction": agent.life_satisfaction,
                "current_emotion": agent.current_emotion
            }
        }
        
        response = await self.llm.generate(
            prompt=prompt,
            agent_profile=profile,
            model=self._select_model(agent)
        )
        
        return response.response
    
    def _select_model(self, agent):
        """Select appropriate model based on agent state."""
        if agent.stress_level > 0.8:
            return "neural-chat:7b"  # Better with emotions
        elif agent.personality.conscientiousness > 0.8:
            return "mistral:7b-instruct"  # More analytical
        else:
            return "phi-2"  # Fast default
```

## Deployment

### Production Deployment

1. **Update Environment Variables**
```bash
# Generate secure API key
openssl rand -base64 32

# Update .env
API_KEY=your-generated-key
REDIS_PASSWORD=secure-redis-password
GRAFANA_PASSWORD=secure-grafana-password
```

2. **Deploy with Docker Compose**
```bash
docker-compose -f docker-compose.yml up -d
```

3. **SSL/TLS Setup** (with Traefik)
```yaml
# Add to docker-compose.yml
traefik:
  image: traefik:v2.10
  command:
    - "--api.insecure=true"
    - "--providers.docker=true"
    - "--entrypoints.websecure.address=:443"
    - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
    - "--certificatesresolvers.letsencrypt.acme.email=your-email@example.com"
    - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
  ports:
    - "443:443"
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock
    - ./letsencrypt:/letsencrypt
```

### Scaling

For high load, you can scale the gateway:

```yaml
# docker-compose.override.yml
services:
  llm-gateway:
    deploy:
      replicas: 3
```

### GPU Support

To enable GPU acceleration for Ollama:

```yaml
services:
  ollama:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

## Monitoring

### Available Metrics

- Request count and duration
- Model usage statistics
- Cache hit/miss rates
- Error rates
- Token usage
- Active requests

### Grafana Dashboard

Import the provided dashboard from `monitoring/grafana/dashboards/llm-gateway.json` for:
- Request throughput
- Response times
- Cache effectiveness
- Model performance comparison
- Error tracking

## Performance Tuning

### Caching Strategy

```yaml
# Adjust cache TTL based on your needs
CACHE_TTL=7200  # 2 hours for stable personalities
```

### Model Selection

- **mistral:7b-instruct**: Best quality, 8GB RAM required
- **neural-chat:7b**: Good for emotional responses, 8GB RAM
- **phi-2**: Fastest, only 3GB RAM required

### Batch Processing

For large agent populations:
1. Use batch endpoint for multiple agents
2. Implement request queuing
3. Consider pre-generating common responses

## Troubleshooting

### Common Issues

1. **Out of Memory**
   - Reduce model size (use phi-2)
   - Increase Docker memory limits
   - Use quantized models

2. **Slow Response Times**
   - Enable caching
   - Use smaller models
   - Add more gateway replicas

3. **Model Download Fails**
   - Check internet connection
   - Manually pull models:
     ```bash
     docker exec -it agentsociety-ollama ollama pull mistral:7b
     ```

### Logs

```bash
# View all logs
docker-compose logs -f

# Specific service logs
docker-compose logs -f llm-gateway
docker-compose logs -f ollama
```

## API Reference

See the full API documentation at http://localhost:8080/docs when the server is running.

## Security Considerations

1. Always use API keys in production
2. Run behind a reverse proxy with SSL
3. Implement IP whitelisting if needed
4. Monitor for unusual usage patterns
5. Regularly update Docker images

## License

Part of the AgentGraphSociety project.