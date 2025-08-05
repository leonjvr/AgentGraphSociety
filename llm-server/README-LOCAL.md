# Local Testing Guide - LLM Server

This guide is for testing the LLM server locally with modified ports to avoid conflicts.

## Modified Ports

To avoid conflicts with common services, we use these ports for local testing:

| Service | Standard Port | Local Test Port | Access URL |
|---------|--------------|-----------------|------------|
| LLM Gateway API | 8080 | **8180** | http://localhost:8180 |
| Redis | 6379 | **6479** | localhost:6479 |
| Prometheus | 9090 | **9190** | http://localhost:9190 |
| Grafana | 3000 | **3100** | http://localhost:3100 |
| Ollama | 11434 | 11434 | http://localhost:11434 |

## Quick Start for Local Testing

1. **Run the test script:**
   ```bash
   cd llm-server
   ./test-local.sh
   ```

2. **Or manually start:**
   ```bash
   cd llm-server
   docker-compose up -d
   ```

3. **Wait for models to download** (first run only):
   ```bash
   docker-compose logs -f model-downloader
   ```

## Testing the API

### Health Check
```bash
curl http://localhost:8180/health
```

### List Available Models
```bash
curl -H "X-API-Key: default-key-change-in-production" http://localhost:8180/models
```

### Generate Text
```bash
curl -X POST http://localhost:8180/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: default-key-change-in-production" \
  -d '{
    "model": "phi-2",
    "prompt": "Hello, how are you?",
    "temperature": 0.7,
    "max_tokens": 50
  }'
```

### Generate with Agent Profile
```bash
curl -X POST http://localhost:8180/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: default-key-change-in-production" \
  -d '{
    "model": "phi-2",
    "prompt": "What do you think about the weather?",
    "agent_profile": {
      "agent_id": 1001,
      "name": "Sarah",
      "occupation": "hairdresser",
      "personality": {
        "openness": 0.8,
        "extraversion": 0.9
      }
    }
  }'
```

## Monitoring

- **Grafana Dashboard**: http://localhost:3100 (admin/admin)
- **Prometheus Metrics**: http://localhost:9190
- **API Documentation**: http://localhost:8180/docs

## Troubleshooting

### Port Conflicts
If you get port conflict errors:

1. Check what's using the ports:
   ```bash
   lsof -i :8180
   lsof -i :6479
   lsof -i :9190
   lsof -i :3100
   ```

2. Stop conflicting services or modify `docker-compose.yml` to use different ports

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f llm-gateway
docker-compose logs -f ollama
```

### Stop Services
```bash
docker-compose down
```

### Remove All Data
```bash
docker-compose down -v
```

## Update AgentGraphSociety Config

When testing locally, update your `agentsociety.yaml`:

```yaml
llm:
  provider: "gateway"
  
  gateway:
    base_url: "http://localhost:8180"  # Note: port 8180 for local testing
    api_key: "default-key-change-in-production"
    timeout: 30
    retry_attempts: 3
```

## Production Deployment

For production, revert to standard ports by editing `docker-compose.yml` or use the original configuration in the main README.