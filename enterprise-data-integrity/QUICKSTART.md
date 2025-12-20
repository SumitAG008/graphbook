# Quick Start Guide - 5 Minutes to First Report

This guide will get you from zero to your first data quality report in 5 minutes.

## Prerequisites

- Docker & Docker Compose installed
- OR: Python 3.11+, Node 18+, PostgreSQL, Redis

## Option 1: Docker (Fastest - Recommended)

### 1. Start the Application

```bash
# Start all services
docker-compose up -d

# Wait 30 seconds for services to start
# Check logs if needed
docker-compose logs -f
```

### 2. Open the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 3. Run Your First Check

1. **Upload CSV**
   - Go to http://localhost:3000
   - Click "Choose File"
   - Select `docs/sample_employee_data.csv`
   - Wait for upload (you'll see columns detected)

2. **Select Rules**
   - All rules are selected by default
   - You'll see:
     - Duplicate Employees
     - Missing Mandatory Fields
     - Invalid Email Addresses
     - Manager Hierarchy Loops
     - Invalid Country Codes

3. **Run Check**
   - Click "Run Data Quality Check"
   - You'll be redirected to the Run screen
   - Wait for processing (5-10 seconds)

4. **View Results**
   - See total issues found
   - Browse issues by severity
   - Read recommendations for each issue

5. **Generate Report**
   - Click "Generate PDF Report"
   - Download the executive summary PDF

## Option 2: Local Development

### Backend

```bash
cd backend

# Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up database
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# Create tables
python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"

# Start server
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Then follow step 3 above to run your first check.

## Understanding the Sample Data

The `docs/sample_employee_data.csv` file contains intentional data quality issues:

- **Duplicate:** Employee E003 appears twice
- **Missing Email:** Employee E005 has no email
- **Invalid Email:** Employee E006 has malformed email
- **Invalid Country:** Employee E007 has invalid country code "XX"
- **Hierarchy Loop:** Employee E018 reports to E018 (themselves)
- **Missing Email:** Employee E017 has incomplete email

These issues will be detected by the rules engine!

## What You'll See

### Upload Screen
- File upload with preview
- Column detection
- Rule selection checkboxes

### Run Screen
- Real-time progress
- Summary metrics (records, issues, rules passed/failed)
- Issues table with severity, recommendations
- PDF report generation

### Dashboard Screen
- Integration health overview
- Recent runs history
- Connector status

## Next Steps

1. **Try your own data**
   - Upload your CSV file
   - Map columns to standard fields
   - Run checks

2. **Explore API**
   - Visit http://localhost:8000/docs
   - Try API endpoints directly
   - Build custom integrations

3. **Review business plan**
   - See `docs/BUSINESS_PLAN.md`
   - Understand the SaaS model
   - Explore monetization strategy

## Troubleshooting

### Docker issues

```bash
# Restart all services
docker-compose down
docker-compose up -d

# Check logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Reset database
docker-compose down -v
docker-compose up -d
```

### Local development issues

**Database connection error:**
- Check PostgreSQL is running: `pg_isready`
- Verify credentials in `.env`
- Ensure database exists

**Frontend not connecting to backend:**
- Check backend is running on port 8000
- Verify CORS settings in backend
- Check browser console for errors

**Module import errors:**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

## Support

- Read full README: `README.md`
- Review business plan: `docs/BUSINESS_PLAN.md`
- Check API docs: http://localhost:8000/docs

---

**You're ready to prevent data quality issues!** 🚀
