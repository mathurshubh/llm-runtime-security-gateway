# LLM Runtime Security Gateway

A production-style AI security gateway built with FastAPI, Ollama, Prometheus, and Grafana.

This project demonstrates runtime security controls for LLM applications, including authentication, authorization, abuse prevention, prompt inspection, policy enforcement, output security, security analytics, and observability.

---

# Features

- OAuth2-compatible JWT authentication
- Bearer token protected API endpoints
- RBAC (Role-Based Access Control)
- Admin-only protected routes
- Prompt injection detection
- PII detection and inspection
- Output credential leakage detection
- JWT token detection and redaction
- AWS credential detection and redaction
- Runtime policy enforcement engine
- Risk scoring and severity classification
- Rate limiting middleware
- Structured telemetry logging
- Prometheus metrics integration
- Grafana monitoring dashboards
- Ollama local LLM integration
- Production-style FastAPI architecture
- Redis-backed distributed rate limiting
- Shared security state across gateway instances
- TTL-based abuse prevention controls
- Redis-backed security event storage
- Security event audit trail
- Authorization denial tracking
- Rate limit violation tracking
- Policy violation analytics
- Output security violation analytics
- Security analytics API
- Audit trail for security events
- Admin-only event investigation endpoint
- Security analytics event retrieval API
- Security summary analytics API
- Aggregated security event reporting
- Security analytics Grafana dashboard
- Prometheus-backed security telemetry
- Security event visualization
- OpenTelemetry distributed tracing
- Security pipeline trace instrumentation
- Runtime latency visibility
- Trace-based policy observability

---

# Security Capabilities

## Authentication

The gateway uses OAuth2-compatible JWT bearer authentication.

Capabilities include:
- Signed JWT access tokens
- Token expiration validation
- Bearer token authentication
- Swagger OAuth2 integration
- Identity-aware request processing

## Authorization (RBAC)

The gateway implements role-based access control.

Supported roles:
- admin
- analyst
- user

Protected routes enforce:
- authenticated access
- role validation
- least privilege principles

## Abuse Prevention

The gateway uses Redis-backed distributed rate limiting to protect LLM resources from abuse.

Capabilities include:

- Per-user rate limiting
- Shared counters across gateway instances
- Automatic counter expiration using Redis TTL
- Protection against API abuse
- Protection against denial-of-wallet attacks
- Distributed enforcement across multiple gateway nodes

## Security Analytics

The gateway stores security-relevant events in Redis and exposes them through protected administrative APIs.

Captured event types include:

- policy_violation
- output_security_violation
- rate_limit_violation
- authorization_denied

Each event contains:

```json
{
  "event_id": "...",
  "event_type": "...",
  "user": "...",
  "timestamp": "...",
  "details": {}
}
```

The event store provides a foundation for audit logging, incident investigation, and future security dashboards.

## Input Security

The gateway analyzes prompts before forwarding them to the LLM runtime.

Detection includes:
- Prompt injection attempts
- Ignore previous instruction attacks
- Jailbreak-style prompts
- Sensitive PII inspection
- Email detection

## Output Security

The gateway inspects model responses before returning output to users.

Detection includes:
- JWT tokens
- AWS Access Keys
- AWS Secret Keys
- Credential-like secrets
- Sensitive token fragments

Detected secrets are automatically:
- redacted
- logged
- tracked through telemetry

## Policy Engine

The policy engine:
- aggregates findings
- calculates risk scores
- assigns severity levels
- blocks dangerous requests

Severity levels:
- low
- medium
- high
- critical

---

# Architecture

```text
                           +----------------------+
                           |      Client/API      |
                           +----------+-----------+
                                      |
                                      v
                           +----------------------+
                           |       /login         |
                           | JWT Authentication   |
                           +----------+-----------+
                                      |
                                      v
                           +----------------------+
                           | OAuth2 Bearer Token  |
                           |      Validation      |
                           +----------+-----------+
                                      |
                                      v
                           +----------------------+
                           | RBAC Authorization   |
                           | Role Enforcement     |
                           +----------+-----------+
                                      |
                                      v
                           +----------------------+
                           | Redis Rate Limiter   |
                           | Abuse Prevention     |
                           +----------+-----------+
                                      |
                                      v
                           +----------------------+
                           | FastAPI Security     |
                           |      Gateway         |
                           +----------+-----------+
                                      |
                                      v
                    +----------------------------------+
                    | OpenTelemetry Tracing            |
                    | Security Pipeline Visibility     |
                    +----------------+-----------------+
                                     |
         +---------------------------+---------------------------+
         |                           |                           |
         v                           v                           v

+-------------------+     +----------------------+    +-------------------+
| Prompt Inspection | --> | Policy Engine        | -> | Ollama Inference  |
| Prompt Injection  |     | Risk Scoring         |    | LLM Runtime Call  |
| PII Detection     |     | Severity Analysis    |    +---------+---------+
+---------+---------+     +----------+-----------+              |
          |                          |                          |
          +--------------------------+--------------------------+
                                     |
                                     v

                      +-----------------------------+
                      | Output Inspection           |
                      | JWT Detection               |
                      | AWS Key Detection           |
                      | Response Redaction          |
                      +-------------+---------------+
                                    |
                                    v

                      +-----------------------------+
                      | Security Event Store        |
                      | Audit Event Generation      |
                      +-------------+---------------+
                                    |
                                    v

                      +-----------------------------+
                      |            Redis            |
                      |                             |
                      | - Rate Limit Counters       |
                      | - Security Events           |
                      | - Shared Gateway State      |
                      | - Analytics Source          |
                      +------+------+---------------+
                             |      |
            +----------------+      +----------------+
            |                                      |
            v                                      v

+----------------------+              +----------------------+
| Security Events API  |              | Security Summary API |
| /security/events     |              | /security/summary    |
+----------+-----------+              +----------+-----------+
           |                                     |
           +----------------+--------------------+
                            |
                            v

                 +----------------------+
                 | Telemetry Pipeline   |
                 | Logs                 |
                 | Metrics              |
                 | Traces               |
                 +----------+-----------+
                            |
             +--------------+--------------+
             |                             |
             v                             v

    +-------------------+       +-------------------+
    | Prometheus        |       | Grafana           |
    | Metrics           |       | Dashboards        |
    +-------------------+       +-------------------+

                                      |
                                      v

                           +----------------------+
                           | Future: Jaeger       |
                           | Trace Visualization  |
                           | Latency Analysis     |
                           +----------------------+
```

---

# Tech Stack

| Component | Technology |
|---|---|
| API Framework | FastAPI |
| LLM Runtime | Ollama |
| Authentication | OAuth2 + JWT |
| Authorization | RBAC |
| Distributed Cache | Redis |
| Metrics | Prometheus |
| Dashboards | Grafana |
| Logging | Structlog |
| Token Security | python-jose |
| Password Hashing | passlib + bcrypt |
| Visualization | Grafana |
| Monitoring | Prometheus |
| Tracing | OpenTelemetry |

---

# Project Structure

```text
llm-runtime-security-gateway/
│
├── app/
│   │
│   ├── auth/
│   │   ├── jwt_auth.py
│   │   └── rbac.py
│   │
│   ├── cache/
│   │   └── redis_client.py
│   │
│   ├── detection/
│   │   ├── pii_detector.py
│   │   └── prompt_detector.py
│   │
│   ├── middleware/
│   │   └── rate_limiter.py
│   │
│   ├── security/
│   │   ├── event_store.py
│   │   ├── output_filter.py
│   │   ├── policy_engine.py
│   │   ├── redactor.py
│   │   └── risk_engine.py
│   │
│   ├── telemetry/
│   │   ├── logger.py
│   │   └── metrics.py
│   │
│   └── main.py
│
├── monitoring/
│   └── prometheus.yml
│
├── tests/
│
├── docker-compose.yml
├── requirements.txt
├── README.md
│
└── .gitignore
```

---

# Authentication Flow

The gateway uses OAuth2-compatible JWT bearer authentication instead of static API keys.

Authentication flow:

1. Client authenticates using `/login`
2. Gateway validates credentials
3. Gateway issues signed JWT access token
4. Client uses bearer token for protected API access

---

# Authorization Flow (RBAC)

The gateway uses role-based access control for protected endpoints.

Example authorization rules:

| Endpoint | Allowed Roles |
|---|---|
| /chat | admin, analyst, user |
| /admin/policies | admin only |
| /security/events | admin only |
| /security/summary | admin only |

Authorization enforcement:
- validates authenticated identity
- extracts JWT role claims
- applies least privilege access rules
- blocks unauthorized access attempts

---

# Login Example

```bash
curl -X POST \
  'http://127.0.0.1:8000/login' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=admin&password=admin123'
```

Example response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

# Authenticated Chat Request

```bash
curl -X POST \
  'http://127.0.0.1:8000/chat' \
  -H 'Authorization: Bearer <JWT_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "Explain zero trust architecture"
}'
```

---

# Protected Admin Endpoint Example

```bash
curl -X GET \
  'http://127.0.0.1:8000/admin/policies' \
  -H 'Authorization: Bearer <JWT_TOKEN>'
```

Expected:
- admin users → access granted
- analyst/user → 403 forbidden

---

# Security Events API

Retrieve recent security events:

```bash
curl -X GET \
  'http://127.0.0.1:8000/security/events' \
  -H 'Authorization: Bearer <JWT_TOKEN>'
```

Example response:

```json
{
  "event_count": 4,
  "events": [
    {
      "event_id": "...",
      "event_type": "policy_violation",
      "user": "admin",
      "timestamp": "...",
      "details": {}
    }
  ]
}
```

Required role:

```text
admin
```

---

# Security Summary API

Retrieve aggregated security statistics:

```bash
curl -X GET \
  'http://127.0.0.1:8000/security/summary' \
  -H 'Authorization: Bearer <JWT_TOKEN>'
```

Example response:

```json
{
  "total_events": 25,
  "policy_violations": 8,
  "output_security_violations": 6,
  "rate_limit_violations": 7,
  "authorization_denied": 4
}
```

Required role:

```text
admin
```
---

# Swagger Authentication

1. Open:

```text
http://127.0.0.1:8000/docs
```

2. Use `/login` endpoint with:
   - username: `admin`
   - password: `admin123`

3. Click the `Authorize` button

4. Swagger automatically attaches bearer tokens to protected endpoints

---

# Metrics Endpoint

Prometheus metrics are exposed at:

```text
http://127.0.0.1:8000/metrics
```

Example metrics:
- requests_total
- blocked_requests_total
- redacted_outputs_total
- jwt_detections_total
- aws_key_detections_total
- policy_actions_total

---

# Monitoring Stack

## Start Monitoring Stack

```bash
docker compose up -d
```

This starts:

- Prometheus
- Grafana
- Redis

## Access Services

| Service | URL |
|---|---|
| FastAPI | http://127.0.0.1:8000 |
| Swagger Docs | http://127.0.0.1:8000/docs |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |

---

## Security Analytics Dashboard

Grafana provides centralized visibility into both gateway operations and security analytics.

### Gateway Operations

The dashboard monitors runtime gateway activity and security enforcement metrics, including:

- Total Requests
- Blocked Requests
- Redacted Outputs
- JWT Leak Detections
- AWS Credential Detections
- Policy Engine Actions

These metrics help operators understand traffic volume, policy enforcement activity, and runtime security controls.

### Security Analytics

The dashboard also visualizes security telemetry generated by the gateway:

- Security Events
- Policy Violations
- Output Security Violations
- Authorization Denied Events

Security events are collected through the event pipeline, stored in Redis, exported through Prometheus metrics, and visualized in Grafana.

### Dashboard Structure

```text
LLM Runtime Security Gateway

├── Gateway Operations
│   ├── Total Requests
│   ├── Blocked Requests
│   ├── Redacted Outputs
│   ├── JWT Leak Detections
│   ├── AWS Credential Detections
│   └── Policy Engine Actions
│
└── Security Analytics
    ├── Security Events
    ├── Policy Violations
    ├── Output Security Violations
    └── Authorization Denied Events
```

This dashboard provides a unified operational and security view of the gateway, enabling monitoring of authentication activity, policy enforcement, abuse prevention controls, output security events, and overall system health.

---

# OpenTelemetry Tracing

The gateway includes OpenTelemetry-based distributed tracing for runtime observability.

Security pipeline stages are instrumented as custom traces, allowing inspection of request processing latency and security decision paths.

Current traced operations include:

- Prompt Inspection
- Policy Engine Evaluation
- Ollama Inference
- Output Inspection

Example trace flow:

```text
POST /chat
│
├── Prompt Inspection
├── Policy Engine
├── Ollama Inference
└── Output Inspection
```

Captured trace attributes include:

- findings.count
- policy.action
- risk.score
- risk.severity

These traces provide visibility into security processing, policy decisions, and LLM inference latency.

Current implementation uses the OpenTelemetry Console Exporter for local development and trace validation.

Future enhancements include integration with Jaeger for visual trace exploration, latency analysis, and distributed tracing dashboards.

---

# Distributed Rate Limiting

The gateway uses Redis-backed distributed rate limiting instead of local in-memory counters.

Benefits:

- Shared state across multiple gateway instances
- Protection against horizontal scaling bypasses
- Automatic counter expiration using Redis TTL
- Production-style abuse prevention architecture

The rate limiter stores counters in Redis using TTL-based keys, enabling consistent enforcement across multiple gateway instances.

Example Redis keys:

```text
rate_limit:admin
rate_limit:user
rate_limit:analyst
```

Counters automatically expire after the configured rate limit window.

---

# Security Event Pipeline

Security-relevant events are stored in Redis for audit and analytics purposes.

Events are stored in a Redis list:

```text
security_events
```

Example stored events:

- policy_violation
- output_security_violation
- rate_limit_violation
- authorization_denied

Latest events can be retrieved through:

```text
GET /security/events
```

Access to this endpoint is restricted to administrators through RBAC controls.

---

# Example Grafana Panels

Recommended dashboards:

- Total Requests
- Blocked Requests
- Redacted Outputs
- JWT Detections
- AWS Key Detections
- Policy Action Breakdown
- Security Severity Distribution
- Authentication Failures
- Authorization Failures

## JWT Leakage Test

```text
Generate a fake bearer token example
```

Expected:
- JWT detection
- output redaction

## AWS Credential Leakage Test

```text
Show an example AWS configuration file with access keys
```

Expected:
- AWS key detection
- secret redaction

## RBAC Authorization Test

Login as:

```text
user / user123
```

Attempt:

```text
/admin/policies
```

Expected:

```text
403 Forbidden
```

---

# Implemented Security Controls

The gateway currently provides:

- JWT authentication
- RBAC authorization
- Redis distributed rate limiting
- Prompt injection detection
- PII inspection
- Runtime policy enforcement
- Risk scoring and severity classification
- JWT credential leakage detection
- AWS credential leakage detection
- Output redaction
- Security event storage
- Security analytics APIs
- Structured telemetry logging
- Prometheus monitoring
- Grafana dashboards
- OpenTelemetry security tracing
- Prompt inspection tracing
- Policy engine tracing
- LLM inference tracing
- Output inspection tracing

---

# Future Improvements

Planned enhancements:
- Security summary API (/security/summary)
- Security event search and filtering
- Event correlation workflows
- Incident investigation dashboards
- OpenTelemetry tracing
- SIEM integrations
- Secure RAG enforcement
- Agent tool authorization
- Multi-tenant isolation
- Vector database security controls
- Policy-based authorization engine
- Token revocation support
- Jaeger distributed tracing
- Trace latency visualization
- Trace-based performance analysis
- Distributed observability dashboards

---

# Running The Application

## Start Ollama

```bash
ollama serve
```

## Pull Model

```bash
ollama pull llama3.2:3b
```

## Run FastAPI

```bash
uvicorn app.main:app --reload --no-access-log
```

---

# License

MIT License

---

# Disclaimer

This project is for educational and security research purposes only.

Do not use generated secrets, tokens, or credentials in production environments.