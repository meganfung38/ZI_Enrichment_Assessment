# ZoomInfo Enrichment Quality Assessment API

A Flask API for assessing the quality and reliability of ZoomInfo-enriched lead data with OpenAI-powered confidence scoring, intelligent explanations, and professional Excel export capabilities.

## Latest Updates (January 2025)

✅ **Professional Excel Export System**
- **New Export Endpoints**: Download analysis results as formatted XLSX files
- **Professional Formatting**: Color-coded confidence scores, bordered tables, proper column widths
- **Summary Statistics**: Comprehensive analysis overview at the top of each report
- **Visual Indicators**: Red highlighting for quality issues, green/yellow/red for confidence scores
- **Automated Naming**: Timestamped filenames for easy organization

✅ **Enhanced Analyze-Query Endpoint**
- **Performance Optimized**: 10x faster execution through batch processing and query optimization
- **Streamlined Interface**: Removed unnecessary options, always includes AI confidence scoring
- **Two-Step Workflow**: Preview queries before running full analysis for better control
- **Smart UI Controls**: Export buttons only enabled after successful analysis completion

✅ **AI-Powered ZoomInfo Enrichment Assessment**
- **Core Endpoint**: `/lead/<lead_id>/confidence` - Complete AI assessment with scores 0-100
- **Smart Explanations**: Clear bullet-point rationale with emoji indicators (✅ ⚠️ ❌)
- **Data Corrections**: AI suggests high-confidence fixes for incorrect ZoomInfo data
- **Intelligent Inferences**: AI fills gaps in missing ZoomInfo enrichment data
- **Email Domain Analysis**: Automatic extraction and corporate vs. free domain validation

✅ **Enhanced ZoomInfo Data Analysis**
- **Extended Quality Flags**: Improved `suspicious_enrichment` and `not_in_TAM` detection
- **Email Domain Field**: New `email_domain` returned for all lead queries
- **Unicode JSON Support**: Proper emoji display in API responses
- **Cross-Field Validation**: Advanced consistency checks between ZoomInfo enrichment fields
- **Flexible SOQL Queries**: Support for JOINs, UNIONs, and complex queries that return Lead IDs

✅ **Dependencies Updated to Latest Versions**
- **Flask 3.1.1** - Latest stable with improved performance and security
- **simple-salesforce 1.12.6** - Enhanced JWT support, Bulk2.0 features, OAuth2 endpoints
- **python-dotenv 1.0.1** - Latest bug fixes and stability improvements
- **OpenAI 1.90.0+** - Latest API features and improved response handling
- **openpyxl 3.1.5** - Excel file generation and professional formatting

🚀 **Technical Improvements**
- Enhanced type hints and linter error resolution
- Improved error handling and connection management
- Unicode-safe JSON serialization for international characters
- Modular Excel service architecture for extensible reporting

## Project Structure

```
ZI_Enrichment_Assessment/
├── app.py                    # Main Flask application
├── docs/                     # Documentation
│   ├── README.md            # This file
│   ├── project_breakdown.md # Project requirements & overview
│   └── lead_data_interpretation.md # AI scoring methodology
├── config/                   # Configuration files
│   ├── config.py            # Application configuration
│   ├── requirements.txt     # Python dependencies
│   └── env.example         # Example environment file
├── .env                     # Environment variables (not in git)
├── services/                # Business logic services
│   ├── __init__.py
│   ├── salesforce_service.py  # Salesforce API integration
│   ├── openai_service.py      # OpenAI API integration & confidence scoring
│   └── excel_service.py       # Excel export and formatting service
└── routes/                  # API route definitions
    ├── __init__.py
    └── api_routes.py        # All API endpoints
```

## Setup

### 1. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies (Updated Versions)
```bash
pip install -r config/requirements.txt
```

### 3. Environment Configuration
```bash
# Copy the example environment file
cp config/env.example .env

# Edit .env with your actual Salesforce credentials
```

Required environment variables:
- `SF_USERNAME`: Your Salesforce username
- `SF_PASSWORD`: Your Salesforce password  
- `SF_SECURITY_TOKEN`: Your Salesforce security token
- `SF_DOMAIN`: `login` for production, `test` for sandbox
- `OPENAI_API_KEY`: Your OpenAI API key (for confidence scoring)

### 4. Run the Application
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Root Endpoint
- **GET** `/` - API information and available endpoints

### Health Check
- **GET** `/health` - Service health status
- **GET** `/debug-config` - Configuration debugging information

### Connection Testing
- **GET** `/test-salesforce-connection` - Test Salesforce connectivity
- **GET** `/test-openai-connection` - Test OpenAI API connectivity
- **GET** `/test-openai-completion` - Test OpenAI completion generation

### Lead Data Endpoints

#### Basic Lead Data
- **GET** `/lead/<lead_id>` - Get specific lead by ID with quality flags
- **GET** `/leads?limit=100&where=<conditions>` - Query leads with filters

#### ZoomInfo Enrichment Assessment
- **GET** `/lead/<lead_id>/confidence` - **Complete AI assessment with confidence scoring**
- **GET** `/lead/<lead_id>/confidence/export` - **Export single lead assessment to Excel**

#### Bulk Analysis & Export
- **POST** `/leads/analyze-query` - **Analyze multiple leads from SOQL query with AI scoring**
  - Supports complex queries with JOINs, UNIONs, and subqueries that return Lead IDs
- **POST** `/leads/analyze-query/export` - **Export bulk analysis results to Excel**
- **POST** `/leads/preview-query` - **Preview SOQL query results before analysis**

#### Web Interface
- **GET** `/ui` - **Interactive web interface for testing and analysis**

### Example Usage

```bash
# Test connections
curl http://localhost:5000/test-salesforce-connection
curl http://localhost:5000/test-openai-connection

# Get basic lead data with quality flags and email domain
curl http://localhost:5000/lead/00Q5e00000ABC123

# Get AI-powered ZoomInfo enrichment assessment (RECOMMENDED)
curl http://localhost:5000/lead/00Q5e00000ABC123/confidence

# Export single lead assessment to Excel
curl http://localhost:5000/lead/00Q5e00000ABC123/confidence/export -o lead_assessment.xlsx

# Query leads with filters
curl "http://localhost:5000/leads?limit=50&where=Email!=null"

# Use the web interface for bulk analysis and export (EASIEST)
open http://localhost:5000/ui

# Bulk analysis via API (for programmatic use)
# Simple query
curl -X POST http://localhost:5000/leads/analyze-query \
  -H "Content-Type: application/json" \
  -d '{"soql_query": "SELECT Id FROM Lead WHERE Email LIKE '\''%@gmail.com'\''", "max_analyze": 10}'

# Complex query with JOIN
curl -X POST http://localhost:5000/leads/analyze-query \
  -H "Content-Type: application/json" \
  -d '{"soql_query": "SELECT Lead.Id FROM Lead JOIN Account ON Lead.AccountId = Account.Id WHERE Account.Industry = '\''Technology'\''", "max_analyze": 10}'

# Export bulk analysis to Excel
curl -X POST http://localhost:5000/leads/analyze-query/export \
  -H "Content-Type: application/json" \
  -d '{"soql_query": "SELECT Id FROM Lead WHERE Email LIKE '\''%@gmail.com'\''", "max_analyze": 10}' \
  -o bulk_analysis.xlsx
```

### ZoomInfo Enrichment Assessment Response Example

```json
{
  "status": "success",
  "message": "Lead confidence assessment completed successfully",
  "lead_data": {
    "Id": "00Q5e00000ABC123",
    "First_Channel__c": "Website",
    "ZI_Company_Name__c": "ACI Solutions Inc",
    "Email": "lmcguire@acisolutions.net",
    "Website": "acisolutions.net",
    "ZI_Employees__c": 24,
    "LS_Enrichment_Status__c": "true",
    "email_domain": "acisolutions.net",
    "not_in_TAM": false,
    "suspicious_enrichment": false
  },
  "confidence_assessment": {
    "confidence_score": 75,
    "explanation_bullets": [
      "✅ Email domain matches company domain.",
      "⚠️ Low employee count (24) raises credibility concerns.",
      "⚠️ Lack of website enrichment lowers completeness.",
      "⚠️ Small company size may indicate limited data availability."
    ],
    "corrections": {},
    "inferences": {}
  },
  "processing_info": {
    "salesforce_message": "Lead retrieved successfully with analysis",
    "ai_message": "Assessment generated successfully"
  }
}
```

### Basic Lead Response Example

```json
{
  "status": "success",
  "message": "Lead retrieved successfully with analysis",
  "lead": {
    "Id": "00Q5e00000ABC123",
    "First_Channel__c": "Website",
    "ZI_Company_Name__c": "Example Corp",
    "Email": "john.doe@gmail.com",
    "Website": null,
    "ZI_Employees__c": 250,
    "LS_Enrichment_Status__c": "SUCCESS",
    "email_domain": "gmail.com",
    "not_in_TAM": false,
    "suspicious_enrichment": true
  }
}
```

In this example:
- `email_domain: "gmail.com"` - **NEW**: Extracted email domain for analysis
- `not_in_TAM: false` - Company name is populated, so it's in TAM base
- `suspicious_enrichment: true` - Gmail email + no website + company name + >100 employees suggests potential enrichment issue

## Lead Fields Returned

The API returns the following ZoomInfo-related fields:

### **Core Lead Data**
- `Id` - Salesforce Lead ID
- `First_Channel__c` - First channel information
- `ZI_Company_Name__c` - ZoomInfo company name
- `Email` - Lead email address
- `Website` - Company website
- `ZI_Employees__c` - ZoomInfo employee count
- `LS_Enrichment_Status__c` - Lead enrichment status

### **Enhanced ZoomInfo Analysis Fields**
- `email_domain` - Extracted email domain for validation
- `not_in_TAM` - Boolean indicating if lead should be in RC TAM base
  - `true` when `ZI_Employees__c > 100` but `ZI_Company_Name__c` is null
  - Suggests incomplete ZoomInfo enrichment for companies that should be in Total Addressable Market
- `suspicious_enrichment` - Boolean indicating potentially incorrect ZoomInfo enrichment
  - `true` when email has free domain (gmail, yahoo, etc.) + no website + company name populated + >100 employees
  - Suggests ZoomInfo enrichment may have incorrectly associated personal email with large company

### **AI-Powered ZoomInfo Assessment Fields**
- `confidence_score` - Overall ZoomInfo enrichment confidence rating (0-100)
- `explanation_bullets` - 3-5 clear explanations with emoji indicators for enrichment reliability
- `corrections` - High-confidence fixes suggested by AI for ZoomInfo data
- `inferences` - Lower-confidence guesses for missing ZoomInfo enrichment data

### **Excel Export Features**
- **Professional Formatting**: Color-coded confidence scores, bordered tables, proper column sizing
- **Summary Statistics**: Analysis overview including total leads, issue percentages, average confidence
- **Visual Indicators**: Red highlighting for quality issues, traffic light colors for confidence scores
- **Comprehensive Data**: All lead fields, confidence assessments, explanations, corrections, and inferences
- **Timestamped Files**: Automatic naming with date/time for easy organization

## SOQL Query Support

The API supports flexible SOQL queries for bulk analysis with the following capabilities:

### ✅ **Supported Query Types**

#### **Simple Queries**
```sql
-- Basic filtering
WHERE Email LIKE '%@gmail.com'
WHERE ZI_Employees__c > 100
LIMIT 50

-- Full SELECT statements
SELECT Id FROM Lead WHERE Company = 'Acme Corp'
SELECT Lead.Id FROM Lead WHERE Email IS NOT NULL
```

#### **Complex Queries with JOINs**
```sql
-- Join with Account for filtering
SELECT Lead.Id FROM Lead 
JOIN Account ON Lead.AccountId = Account.Id 
WHERE Account.Industry = 'Technology'

-- Multiple JOINs
SELECT l.Id FROM Lead l 
JOIN Contact c ON l.Email = c.Email 
JOIN Account a ON c.AccountId = a.Id 
WHERE a.AnnualRevenue > 1000000
```

#### **UNION Queries**
```sql
-- Combine different Lead segments
SELECT Id FROM Lead WHERE ZI_Employees__c > 100
UNION ALL
SELECT Id FROM Lead WHERE Email LIKE '%@enterprise.com'

-- Complex UNION with JOINs
SELECT Lead.Id FROM Lead JOIN Account ON Lead.AccountId = Account.Id WHERE Account.Type = 'Customer'
UNION
SELECT Lead.Id FROM Lead WHERE ZI_Company_Name__c LIKE '%Fortune%'
```

#### **Subqueries**
```sql
-- Filter by related Account data
SELECT Id FROM Lead 
WHERE AccountId IN (
    SELECT Id FROM Account 
    WHERE AnnualRevenue > 1000000
)

-- Complex nested filtering
SELECT Id FROM Lead 
WHERE Id NOT IN (
    SELECT LeadId FROM Task 
    WHERE Subject LIKE '%ZoomInfo%'
)
```

### ❌ **Security Restrictions**

The following are **blocked for security**:
- **Non-Lead Objects**: `SELECT Id FROM Contact` ❌
- **Non-ID Fields**: `SELECT Name FROM Lead` ❌
- **Dangerous Operations**: `DELETE`, `UPDATE`, `INSERT`, `DROP` ❌
- **Mixed Object UNIONs**: `SELECT Id FROM Lead UNION SELECT Id FROM Contact` ❌

### **Validation Rules**

1. **Result-Focused**: Query must return Lead IDs only
2. **Lead-Centric**: Must involve Lead object in the query
3. **Security-First**: All dangerous SQL operations blocked
4. **Flexible Structure**: JOINs, UNIONs, subqueries allowed if they return Lead IDs

## Development

### Project Architecture
- **Flask Application Factory Pattern**: Clean app initialization
- **Blueprints**: Organized route management
- **Service Layer**: Separation of business logic
- **Configuration Management**: Environment-based config
- **AI Integration**: OpenAI-powered confidence scoring

### Adding New Features
1. **Services**: Add business logic to `services/`
2. **Routes**: Add API endpoints to `routes/`
3. **Configuration**: Add config options to `config/config.py`

### Error Handling
All endpoints return standardized JSON responses:
```json
{
  "status": "success|error",
  "message": "Human readable message",
  "data": {}  // Only on success
}
``` 