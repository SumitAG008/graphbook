# Enterprise Data Integrity Control Room

**Preventing HR/Finance integration failures and bad data before they hit payroll, reporting, or compliance.**

## What This Application Does

Enterprise Data Integrity Control Room is a SaaS application that continuously monitors and validates data quality across HR, Finance, and IT systems. It helps companies:

- **Check data quality** - Detect duplicates, missing fields, mismatched IDs
- **Monitor integration health** - Track job failures, delays, retries
- **Detect anomalies** - Identify sudden spikes, drops, inconsistencies
- **Produce auditable reports** - Generate executive summaries for stakeholders
- **Recommend fixes** - Provide actionable recommendations and generate tickets

## Business Value

### Who Pays for This
- **HR Operations / HRIT** - Managing SuccessFactors, Employee Central
- **Integration Teams** - Running CPI/PI, Boomi, MuleSoft
- **Data Teams** - Operating Databricks, data lakes, analytics
- **Internal Audit / Compliance** - Maintaining SOX-like controls

### Why They Pay
- **Prevent payroll errors** - Bad data = wrong salaries, missed bonuses
- **Reduce compliance risk** - Avoid SOX violations, audit findings
- **Stop integration failures** - One bad record breaks downstream processes
- **Build executive confidence** - Clean reports, audit trails, data trust

## The 4 Core Modules (MVP)

### Module 1: Connectors
- CSV upload with field mapping
- API integration (coming soon)
- Manual mapping UI
- Works as standalone "assessment tool"

### Module 2: Data Quality Rules Engine ⭐ Core Value
**Pre-built Rules:**
- Duplicate employee detection
- Missing mandatory fields checker
- Invalid email validation
- Manager hierarchy loop detection
- Invalid country code validation

**Output:** Issues list + severity + affected records + recommendations

### Module 3: Integration Health Monitor
- Scheduled checks for connector health
- Success rate, latency, last success tracking
- Failure rate monitoring
- Alerting (email/Teams webhook - coming soon)

**Output:** Health dashboard + incident log

### Module 4: Recommendations + Reports
- "What changed since last week" summaries
- Executive-friendly PDF reports
- Recommended fixes with priority
- Excel/CSV export

## Technical Architecture

### Backend (FastAPI + Python)
- **Database:** PostgreSQL (runs, issues, tenants, audit trail)
- **Caching:** Redis (for Celery job queue)
- **Scheduler:** APScheduler (periodic checks)
- **Models:** Tenant, User, Connector, Rule, Run, Issue, Alert, Report

### Frontend (React + TypeScript)
- **UI Framework:** Material-UI (MUI)
- **Router:** React Router
- **HTTP Client:** Axios
- **Charts:** Recharts

### Data Layer (Future)
- **Neo4j:** Org graph, manager chain relationships (v2)
- **Qdrant:** Embeddings for "similar incidents" search (v2)

## Quick Start

### Prerequisites
- Docker & Docker Compose
- OR: Python 3.11+, Node 18+, PostgreSQL 15+, Redis 7+

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repo-url>
cd enterprise-data-integrity

# Start all services
docker-compose up -d

# Backend will be available at http://localhost:8000
# Frontend will be available at http://localhost:3000
# API docs at http://localhost:8000/docs
```

### Option 2: Local Development

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run migrations (creates tables)
python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"

# Start the server
uvicorn app.main:app --reload

# API will be available at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Frontend will be available at http://localhost:3000
```

## Using the Application

### Screen 1: Upload & Configure
1. Upload a CSV file with your data (HR, Finance, etc.)
2. View detected columns and row count
3. Select which data quality rules to execute

### Screen 2: Run & View Issues
1. Data quality check runs automatically
2. View results summary (records, issues, rules passed/failed)
3. Browse issues table with severity, affected records, recommendations
4. Generate executive PDF report

### Screen 3: Dashboard
1. Monitor overall integration health
2. View recent runs and trends
3. Track connector health metrics
4. Identify anomalies and failures

## Sample Data

A sample CSV file is provided in `/docs/sample_employee_data.csv` for testing:

```csv
employee_id,first_name,last_name,email,country_code,manager_id,department
E001,John,Doe,john.doe@example.com,US,,Engineering
E002,Jane,Smith,jane.smith@example.com,GB,E001,Engineering
```

## API Endpoints

### Connectors
- `POST /api/v1/connectors/upload-csv` - Upload CSV file
- `GET /api/v1/connectors/` - List connectors
- `GET /api/v1/connectors/{id}/health` - Get connector health

### Rules
- `GET /api/v1/rules/available` - Get available rules
- `GET /api/v1/rules/` - List configured rules

### Runs
- `POST /api/v1/runs/` - Create and execute run
- `GET /api/v1/runs/` - List recent runs
- `GET /api/v1/runs/{id}` - Get run details
- `GET /api/v1/runs/{id}/issues` - Get issues for run

### Reports
- `POST /api/v1/reports/generate` - Generate PDF report
- `GET /api/v1/reports/download/{filename}` - Download report
- `GET /api/v1/reports/trends` - Get trend analysis

### Health Monitoring
- `GET /api/v1/health-monitor/dashboard` - Get health dashboard
- `GET /api/v1/health-monitor/connector/{id}` - Get connector health
- `GET /api/v1/health-monitor/incidents` - Get recent incidents

## Business Model

### Phase 1: Consulting ($15K-$50K per engagement)
**Deliverable:** 30-Day Data Integrity Assessment
- Baseline data health score
- Top 20 issues + impact analysis
- Integration failure hotspots
- Remediation roadmap

### Phase 2: SaaS Subscription ($2K-$10K/month per department)
**Features:**
- Continuous monitoring + alerts
- Monthly executive reports
- Audit trail + compliance documentation
- Recommended fixes + ticket generation

## Roadmap

### v1.0 (MVP) ✅ Current Version
- CSV upload
- 5 built-in data quality rules
- Manual run execution
- Executive PDF reports
- Basic health monitoring
- Issues tracking

### v2.0 (Q2 2024)
- API connectors (SuccessFactors, Workday, SAP)
- AI-powered anomaly detection
- Neo4j org hierarchy validation
- Email/Teams alerting
- Scheduled automatic runs
- Trend analysis dashboard

### v3.0 (Q3 2024)
- Ticket automation (Jira, ServiceNow)
- Self-healing workflows
- Custom rule builder
- Multi-tenant management
- Role-based access control

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload
MAX_UPLOAD_SIZE=52428800  # 50MB
UPLOAD_DIR=/tmp/uploads

# Scheduler
ENABLE_SCHEDULER=true
```

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests (coming soon)
cd frontend
npm test
```

## License

Proprietary - All rights reserved

## Support

For questions or support:
- Email: support@example.com
- Documentation: https://docs.example.com
- GitHub Issues: https://github.com/your-org/enterprise-data-integrity/issues

---

**Built with ❤️ for enterprise data quality and integration teams**
