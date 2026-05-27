# PharmaSignal AI 🏥

> **Enterprise-grade AI platform for pharmacovigilance signal detection and adverse event review automation**

[![CI/CD Pipeline](https://github.com/raju-AI-portfolio/pharmasignal-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/raju-AI-portfolio/pharmasignal-ai/actions)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![Azure](https://img.shields.io/badge/Azure-PaaS%20%2B%20IaaS-0078D4.svg)](https://azure.microsoft.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-7C3AED.svg)](https://langchain-ai.github.io/langgraph)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 Table of Contents

- [Business Problem](#business-problem)
- [Solution Overview](#solution-overview)
- [Architecture](#architecture)
- [Microservices](#microservices)
- [AI Agent Workflow](#ai-agent-workflow)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Infrastructure](#infrastructure)
- [CI/CD Pipeline](#cicd-pipeline)
- [Compliance and Governance](#compliance-and-governance)
- [Skills Demonstrated](#skills-demonstrated)

---

## 🏥 Business Problem

Pharmaceutical companies receive **thousands of adverse event reports daily** from multiple channels — call centers, CRM systems, mobile apps, clinical trials, and regulatory databases like FDA FAERS. Each report must be:

- **Classified** within 15 calendar days if serious (ICH E2B requirement)
- **Analysed** for safety signals using statistical methods
- **Documented** with a regulatory-compliant safety narrative
- **Reviewed** by a qualified pharmacovigilance professional (QPPV)
- **Submitted** to regulatory authorities (FDA, EMA)

Today this process is **manual, slow, and expensive**:

| Metric | Manual Process | PharmaSignal AI |
|--------|---------------|-----------------|
| Time per report | 30 minutes | 3 minutes |
| Scientists needed (500 reports/day) | 20–25 FTEs | 3–5 FTEs |
| Risk of missing 15-day deadline | High | Near zero |
| Narrative quality consistency | Variable | Standardised |
| Audit trail completeness | Manual logs | Automated |

---

## 💡 Solution Overview

PharmaSignal AI is a **multi-agent AI platform** that automates the end-to-end pharmacovigilance workflow while maintaining full human oversight for regulatory compliance.

```
Adverse event report arrives
         ↓
Multi-channel intake (FDA / CRM / Call center / Mobile / Clinical trials)
         ↓
5 AI agents process in sequence:
  Triage → Medical → Signal → Narrative → Escalation
         ↓
Human reviewer approves / rejects / escalates
         ↓
Automatic notification to QPPV if escalated
         ↓
Full audit trail logged for regulatory inspection
```

---

## 🏛 Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA INGESTION CHANNELS                       │
│  FDA FAERS │ Call Center │ CRM Export │ Mobile App │ Clinical    │
│  (API pull)│ (REST API)  │ (CSV drop) │ (Event Hub)│ (FHIR/HL7) │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│              AZURE CLOUD PLATFORM (PaaS) — Sweden Central        │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │  Ingestion   │  │  RAG Service │  │   Azure OpenAI      │   │
│  │  Service     │→ │  AI Search   │→ │   GPT-4o            │   │
│  │  FastAPI     │  │  Embeddings  │  │   Embeddings        │   │
│  └──────┬───────┘  └──────────────┘  └─────────────────────┘   │
│         │                                                        │
│  ┌──────▼──────────────────────────────────────────────────┐    │
│  │         MULTI-AGENT ORCHESTRATOR (LangGraph)             │    │
│  │  Triage → Medical → Signal → Narrative → Escalation     │    │
│  └──────────────────────────┬───────────────────────────────┘   │
│                             │                                    │
│  ┌──────────────┐  ┌────────┴─────┐  ┌──────────────────────┐  │
│  │  PostgreSQL  │  │  Cosmos DB   │  │   Azure Key Vault    │  │
│  │  Reports DB  │  │  Agent memory│  │   Secrets + RBAC     │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│              HUMAN-IN-THE-LOOP REVIEW LAYER                      │
│  Review Queue │ React Dashboard │ Approve/Reject/Escalate        │
│  Audit Trail  │ QPPV Email      │ 21 CFR Part 11 compliance      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Microservices

The platform is built as **5 independent microservices**, each with its own responsibility, database connection, and deployment unit.

| Service | Port | Responsibility | Tech |
|---------|------|---------------|------|
| **Ingestion Service** | 8001 | Multi-channel AE report intake | FastAPI, PostgreSQL |
| **RAG Service** | 8002 | Regulatory document search | FastAPI, ChromaDB, Azure AI Search |
| **Agent Orchestrator** | 8003 | 5-agent LangGraph workflow | FastAPI, LangGraph, Azure OpenAI |
| **Human Review API** | 8004 | Review queue, HITL decisions, audit trail | FastAPI, PostgreSQL |
| **Notification Service** | 8005 | Email alerts to QPPV and safety team | FastAPI, SMTP/SendGrid |

---

## 🤖 AI Agent Workflow

The core of PharmaSignal AI is a **LangGraph state machine** orchestrating 5 specialist agents. Each agent has its own system prompt, tools, memory scope, and output schema.

```
New adverse event report
         │
         ▼
┌─────────────────┐
│  Triage Agent   │ → Classifies severity (SERIOUS/NON-SERIOUS)
│                 │   using ICH E2B criteria
└────────┬────────┘
         │ if SERIOUS
         ▼
┌─────────────────┐  ┌─────────────────┐
│  Medical Agent  │  │  Signal Agent   │  ← run in parallel
│                 │  │                 │
│  RAG search     │  │  PRR/ROR stats  │
│  PubMed context │  │  Signal detect  │
└────────┬────────┘  └────────┬────────┘
         └────────────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │ Narrative Agent │ → Writes ICH E2B compliant
         │                 │   safety narrative (7 sections)
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │Escalation Agent │ → Risk score 0–100
         │                 │   AUTO-CLOSE / FLAG / ESCALATE
         └────────┬────────┘
                  │
         ┌────────┴────────┐
         ▼                 ▼
    Auto-close         Human review
    (score < 40)       queue (score ≥ 40)
```

### Agent Routing Logic

| Risk Score | Decision | Action |
|-----------|----------|--------|
| 0 – 39 | AUTO-CLOSE | Automatically documented and closed |
| 40 – 70 | FLAG | Safety scientist review within 7 days |
| 71 – 100 | ESCALATE | Immediate QPPV notification + 24hr deadline |

---

## 🛠 Tech Stack

### AI & Agents
| Component | Technology |
|-----------|-----------|
| Agent orchestration | LangGraph (state machine) |
| LLM | Azure OpenAI GPT-4o |
| Embeddings | Azure OpenAI text-embedding-ada-002 |
| RAG framework | LangChain |
| Vector store (local) | ChromaDB |
| Vector store (cloud) | Azure AI Search |

### Backend & APIs
| Component | Technology |
|-----------|-----------|
| API framework | FastAPI |
| Database ORM | SQLAlchemy |
| HTTP client | httpx |
| Email | aiosmtplib / SendGrid |

### Cloud & Infrastructure
| Component | Technology |
|-----------|-----------|
| Cloud provider | Microsoft Azure (Sweden Central) |
| Container platform | Azure Container Apps (PaaS) |
| Orchestration | Azure Kubernetes Service / AKS (IaaS) |
| Database | Azure PostgreSQL Flexible Server |
| Secret management | Azure Key Vault + Managed Identity |
| Container registry | Azure Container Registry |
| Observability | Azure Monitor + Log Analytics |
| IaC | Terraform |
| CI/CD | GitHub Actions |

### Frontend
| Component | Technology |
|-----------|-----------|
| Framework | React + TypeScript |
| HTTP client | Axios |
| Styling | Custom CSS |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Docker Desktop
- uv (Python package manager)
- Node.js 18+ (for frontend)

### Local Development Setup

**1. Clone the repository**
```bash
git clone https://github.com/raju-AI-portfolio/pharmasignal-ai.git
cd pharmasignal-ai
```

**2. Start PostgreSQL**
```bash
docker run --name pharma-postgres \
  -e POSTGRES_DB=pharmasignal \
  -e POSTGRES_USER=pharma \
  -e POSTGRES_PASSWORD=localdev \
  -p 5432:5432 -d postgres:16-alpine
```

**3. Start MailHog (local email)**
```bash
docker run -d --name pharma-mailhog \
  -p 1025:1025 -p 8025:8025 mailhog/mailhog
```

**4. Configure environment variables**

Create `.env` files in each service directory. See `.env.example` files for required variables:
```
AZURE_OPENAI_ENDPOINT=https://your-resource.services.ai.azure.com/
AZURE_OPENAI_KEY=your-key
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_API_VERSION=2024-12-01-preview
DATABASE_URL=postgresql://pharma:localdev@localhost:5432/pharmasignal
```

**5. Start all services**
```bash
# Terminal 1 — Ingestion service
cd services/ingestion && uv run uvicorn main:app --reload --port 8001

# Terminal 2 — RAG service
cd services/rag && uv run uvicorn main:app --reload --port 8002

# Terminal 3 — Agent orchestrator
cd services/orchestrator && uv run uvicorn main:app --reload --port 8003

# Terminal 4 — Human review API
cd services/review-api && uv run uvicorn main:app --reload --port 8004

# Terminal 5 — Notification service
cd services/notifications && uv run uvicorn main:app --reload --port 8005

# Terminal 6 — React frontend
cd frontend && npm install && npm start
```

**6. Verify all services are healthy**
```bash
curl http://localhost:8001/api/v1/health
curl http://localhost:8002/api/v1/health
curl http://localhost:8003/api/v1/health
curl http://localhost:8004/api/v1/health
curl http://localhost:8005/api/v1/health
```

**7. Ingest sample data and index documents**
```bash
# Ingest FDA FAERS reports
curl -X POST "http://localhost:8001/api/v1/ingest?limit=10"

# Index regulatory documents
curl -X POST "http://localhost:8002/api/v1/index"
```

**8. Run the agent workflow**
```bash
# Analyse a specific report
curl -X POST "http://localhost:8003/api/v1/analyse/5801206-7"

# Save result to review queue
RESULT=$(curl -s -X POST "http://localhost:8003/api/v1/analyse/5801206-7")
curl -X POST "http://localhost:8004/api/v1/cases" \
  -H "Content-Type: application/json" -d "$RESULT"
```

**9. Open the dashboard**

Navigate to [http://localhost:3000](http://localhost:3000)

---

## 📁 Project Structure

```
pharmasignal-ai/
├── services/
│   ├── ingestion/          # Multi-channel AE report intake
│   │   ├── app/
│   │   │   ├── api/        # FastAPI routes
│   │   │   ├── models/     # SQLAlchemy models
│   │   │   └── services/   # FDA client, file parser
│   │   ├── Dockerfile
│   │   └── main.py
│   ├── rag/                # RAG knowledge service
│   │   ├── app/
│   │   │   ├── api/
│   │   │   └── services/   # Document loader, embedder, vector store
│   │   ├── Dockerfile
│   │   └── main.py
│   ├── orchestrator/       # LangGraph multi-agent workflow
│   │   ├── app/
│   │   │   ├── agents/     # 5 specialist agents
│   │   │   ├── models/     # LangGraph state definition
│   │   │   └── services/   # Workflow builder
│   │   ├── Dockerfile
│   │   └── main.py
│   ├── review-api/         # Human review + audit trail
│   │   ├── app/
│   │   │   ├── api/
│   │   │   └── models/     # ReviewCase, AuditLog
│   │   ├── Dockerfile
│   │   └── main.py
│   └── notifications/      # Email notification service
│       ├── app/
│       │   ├── api/
│       │   └── services/   # Email templates
│       └── main.py
├── frontend/               # React TypeScript dashboard
│   └── src/
│       ├── components/     # CaseQueue, CaseDetail
│       └── api.ts
├── infrastructure/
│   ├── terraform/          # Azure IaC
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── k8s/                # Kubernetes manifests
│       ├── ingestion/
│       ├── rag/
│       ├── orchestrator/
│       ├── review-api/
│       └── shared/
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions CI/CD
├── docker-compose.yml
└── README.md
```

---

## 📡 API Documentation

Each service exposes a Swagger UI at `/docs`:

| Service | Swagger UI |
|---------|-----------|
| Ingestion | http://localhost:8001/docs |
| RAG | http://localhost:8002/docs |
| Orchestrator | http://localhost:8003/docs |
| Review API | http://localhost:8004/docs |
| Notifications | http://localhost:8005/docs |

### Key Endpoints

```
POST /api/v1/ingest              # Fetch reports from FDA FAERS
POST /api/v1/intake              # Submit report from any channel
POST /api/v1/intake/file         # Ingest from CSV file drop
POST /api/v1/index               # Index regulatory documents
POST /api/v1/search              # Search regulatory knowledge base
POST /api/v1/analyse/{report_id} # Run 5-agent workflow
GET  /api/v1/cases               # Get review queue
POST /api/v1/cases/{id}/review   # Submit human decision
GET  /api/v1/audit/{id}          # Get full audit trail
POST /api/v1/notify              # Send notification
```

---

## ☁️ Infrastructure

### Azure Resources (Terraform managed)

| Resource | Type | Purpose |
|----------|------|---------|
| pharmasignal-rg | Resource Group | Container for all resources |
| pharmasignalregistry | Container Registry | Docker image storage |
| pharmasignal-env | Container App Environment | Microservices hosting |
| pharmasignal-db | PostgreSQL Flexible Server | Primary database |
| pharmasignal-kv | Key Vault | Secrets management |
| pharmasignal-logs | Log Analytics Workspace | Observability |

### Deploy Infrastructure

```bash
cd infrastructure/terraform
terraform init
terraform plan -var-file="terraform.tfvars"
terraform apply -var-file="terraform.tfvars"
```

### Kubernetes Deployment (AKS)

```bash
# Create namespace
kubectl apply -f infrastructure/k8s/shared/namespace.yaml

# Deploy secrets
kubectl apply -f infrastructure/k8s/shared/secrets.yaml

# Deploy all services
kubectl apply -f infrastructure/k8s/ingestion/deployment.yaml
kubectl apply -f infrastructure/k8s/rag/deployment.yaml
kubectl apply -f infrastructure/k8s/orchestrator/deployment.yaml
kubectl apply -f infrastructure/k8s/review-api/deployment.yaml

# Verify pods are running
kubectl get pods -n pharmasignal
```

---

## 🔄 CI/CD Pipeline

The pipeline has 5 stages with automated gates:

```
PR Gate         Build           Dev Deploy      Staging         Production
─────────       ─────────       ──────────      ───────         ──────────
pytest          Docker build    Terraform       Manual          2-person
linting         5 services      apply           approval        approval
Trivy scan      Push to ACR     Smoke tests     Integration     Blue-green
Checkov IaC     SHA + SemVer    k6 load test    tests           deploy AKS
                                                Agent e2e       Health check
                                                test            Auto-rollback
```

Every production deployment is logged to Azure Monitor for **21 CFR Part 11** audit trail compliance.

---

## 🔒 Compliance and Governance

### Regulatory Standards

| Standard | Implementation |
|----------|---------------|
| ICH E2B | Automated narrative generation with all 7 required sections |
| 21 CFR Part 11 | Full audit trail on every action, electronic signatures |
| GDPR | Patient data pseudonymised, right to erasure supported |
| HIPAA | PHI never logged, encrypted at rest and in transit |
| GxP | Two-person production approval, change control documented |

### Security Controls

- **Zero-trust networking** — All services use Managed Identity, no passwords
- **Secrets management** — Azure Key Vault for all credentials
- **Container security** — Trivy scan on every image build
- **IaC security** — Checkov scan on every Terraform change
- **No direct push to main** — Branch protection enforced

### Human-in-the-Loop Governance

Every case with risk score ≥ 40 requires human review before any regulatory action. The system **cannot** automatically submit to regulators — a qualified human must approve. This is enforced at the architecture level, not just policy.

---

## 📊 Skills Demonstrated

This project demonstrates the full Senior AI Solution Architect skill stack:

| Skill Area | Technologies |
|-----------|-------------|
| **Multi-agent AI** | LangGraph state machine, 5 specialist agents, parallel execution, shared memory |
| **RAG architecture** | Azure AI Search, ChromaDB, chunking strategy, hybrid search, re-ranking |
| **LLM integration** | Azure OpenAI, prompt engineering, structured output, tool calling |
| **MLOps** | Model registry, experiment tracking, deployment patterns |
| **Microservices** | 5 bounded services, API contracts, independent deployment |
| **Cloud architecture** | Azure PaaS + IaaS, Container Apps, AKS, PostgreSQL, Key Vault |
| **DevOps** | GitHub Actions CI/CD, blue-green deployment, auto-rollback |
| **Infrastructure as Code** | Terraform modules, remote state, environment separation |
| **Kubernetes** | AKS, Deployments, HPA, KEDA, NetworkPolicy, Secrets |
| **Security** | Zero-trust, Managed Identity, Key Vault, Trivy, Checkov |
| **Observability** | Azure Monitor, OpenTelemetry, distributed tracing, SLOs |
| **AI Governance** | HITL workflow, risk scoring, audit trail, responsible AI |
| **Domain expertise** | Pharmacovigilance, ICH E2B, GDPR, 21 CFR Part 11 |

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Raju Kumar**
- GitHub: [@raju-AI-portfolio](https://github.com/raju-AI-portfolio)
- Project: [PharmaSignal AI](https://github.com/raju-AI-portfolio/pharmasignal-ai)

---

> *"Designed to demonstrate enterprise-grade AI architecture for regulated industries — combining multi-agent AI, cloud-native microservices, and human-in-the-loop governance to solve a real pharmacovigilance challenge."*
