# GyanX_Scalable_Backend_System-

<img width="778" height="649" alt="image" src="https://github.com/user-attachments/assets/a31c5962-a752-4aa7-9cb9-10e67f753ebd" />


Theek hai, banata hoon — live URL ki jagah tumhara Linode IP 172.104.37.127 use kar raha hoon.

README.md
markdown# SpeakOps Backend

Scalable AI/compute backend deployed on Akamai Linode using Kubernetes (LKE).  
Handles API requests, AI/compute workloads, and moderate-to-high user traffic.

## Live Endpoint

```
POST http://172.104.37.127/generate-response
```

API Docs: `http://172.104.37.127/docs`  
Health Check: `http://172.104.37.127/health`

## Architecture

```
Internet
   ↓
Cloudflare (WAF + DDoS protection)
   ↓
Nginx Ingress (rate limiting + HTTPS termination)
   ↓
Kubernetes Service (ClusterIP)
   ↓
FastAPI Pods (HPA: min 2 → max 10 replicas)
   ↓
Redis (response cache)   PostgreSQL (persistent storage)
```

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI + Uvicorn |
| Language | Python 3.11 |
| Container | Docker |
| Orchestration | Kubernetes — LKE |
| Auto Scaling | HPA (CPU 70%, Memory 80%) |
| Cache | Redis 7 |
| Database | PostgreSQL 16 |
| Infra as Code | Terraform (Linode provider) |
| CI/CD | GitHub Actions |
| Cloud Provider | Akamai Linode |

## Project Structure

```
speakops-backend/
├── app/
│   ├── main.py          # FastAPI app, routes
│   ├── auth.py          # API key validation
│   ├── cache.py         # Redis cache logic
│   ├── ai.py            # AI/compute processing
│   └── config.py        # Environment config
├── k8s/
│   ├── deployment.yaml  # App + Redis deployments
│   ├── service.yaml     # ClusterIP services
│   ├── hpa.yaml         # HorizontalPodAutoscaler
│   ├── ingress.yaml     # Nginx ingress + routing
│   ├── configmap.yaml   # Non-secret config
│   └── secret.yaml      # API keys + DB credentials
├── infra/
│   ├── terraform/       # LKE cluster + Firewall
│   └── nginx/           # Nginx rate limit config
├── stress-test/
│   └── index.html       # Browser-based load tester
├── tests/
│   └── test_main.py     # Pytest test suite
├── .github/workflows/
│   └── deploy.yml       # CI/CD pipeline
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Local Development

```bash
# 1. clone
git clone https://github.com/shubham12gupta/speakops-backend
cd speakops-backend

# 2. setup env
cp .env.example .env
# edit .env — set API_KEY and other values

# 3. run
docker-compose up --build

# API → http://localhost/generate-response
# Docs → http://localhost/docs
```

## API Usage

```bash
curl -X POST http://172.104.37.127/generate-response \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"prompt": "explain kubernetes HPA"}'
```

Response:
```json
{
  "response": "...",
  "model": "mock",
  "latency_ms": 52,
  "cache_hit": false,
  "request_id": "a1b2c3d4"
}
```

## Deployment — LKE

```bash
# 1. provision infra
cd infra/terraform
terraform init
terraform apply -var="linode_token=YOUR_TOKEN"

# 2. set kubeconfig
export KUBECONFIG=infra/terraform/kubeconfig.yaml

# 3. deploy
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/ingress.yaml

# 4. verify
kubectl get pods
kubectl get hpa
kubectl get ingress
```

## Scalability

**Stateless design** — no session data stored on app servers.  
All state lives in Redis (cache) and PostgreSQL (persistent).  
Any pod can serve any request — horizontal scaling works cleanly.

**Auto scaling** — HPA watches CPU and memory:
- CPU > 70% → scale up (max +2 pods per 60s)
- Memory > 80% → scale up
- Scale down after 5 min stabilization window (prevents thrashing)
- Min 2 pods always running — zero downtime

**Caching** — Redis caches identical prompt responses for 60s.  
Reduces redundant AI compute load on repeated traffic.

## Security

| Layer | Implementation |
|---|---|
| Authentication | `X-API-Key` header on every request |
| Rate limiting | Nginx — 100 req/min per IP, burst 20 |
| Secrets | Kubernetes Secrets — never in code |
| HTTPS | cert-manager + Let's Encrypt (Ingress) |
| Firewall | Linode Cloud Firewall — ports 22/80/443 only |
| Headers | X-Frame-Options, X-Content-Type-Options, XSS-Protection |

## Stress Test

Open `stress-test/index.html` in browser.  
Set endpoint to `http://172.104.37.127/generate-response`  
Run load from 1K to 20K concurrent requests.

## CI/CD

Push to `main` → GitHub Actions:
1. Run pytest suite
2. Build Docker image → push to GHCR
3. `kubectl set image` rolling deploy to LKE
4. Wait for rollout confirmation

## If Traffic Grows to 100,000 Users/Day

**What breaks first:** PostgreSQL — single instance read throughput becomes the bottleneck at ~10x load.

**Redesign:**
- Add PostgreSQL read replicas — writes to primary, reads distributed
- Redis cache hit rate target: 60–70% — reduces DB load significantly  
- Move AI workloads to async queue (SQS-style) — decouple API latency from compute
- Upgrade LKE node pool — `g6-standard-2` → `g6-standard-4`
- Akamai CDN caching for cacheable GET responses

Bas GitHub pe push karo:
bashgit add README.md
git commit -m "add README"
git push origin main
