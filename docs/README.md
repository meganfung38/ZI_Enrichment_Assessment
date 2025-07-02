# ZoomInfo Enrichment Quality Assessment API

A Flask API for assessing the quality and reliability of ZoomInfo-enriched lead data with OpenAI-powered confidence scoring, intelligent explanations, and professional Excel export capabilities.

## Latest Updates (January 2025)

✅ **Comprehensive Lead Data Collection**
- **10 Core Field Analysis**: Email, channel, segment, size ranges, dual website sources, ZoomInfo enrichment data
- **Enhanced Cross-Validation**: Compare ZoomInfo data against internal estimates and segment classifications
- **Business Context Integration**: Sales segment and channel information for enriched assessment
- **Dual Website Validation**: Compare lead-provided vs ZoomInfo-enriched website data for consistency

✅ **Enterprise-Grade SOQL Query System**
- **Complex Query Support**: JOINs, UNIONs, subqueries allowed if they return Lead IDs
- **Result-Focused Security**: Smart validation ensures only Lead IDs are returned while enabling flexibility
- **Query Intelligence**: Handles empty queries, LIMIT conflicts, and WHERE clauses automatically
- **Business Logic Support**: Sophisticated lead filtering with multi-object relationship queries

✅ **Advanced AI-Powered Assessment**
- **Enhanced Validation Framework**: 10+ data points for comprehensive enrichment quality scoring (0-100)
- **Intelligent Cross-Checking**: Website consistency, company size agreement, segment alignment
- **Smart Corrections**: High-confidence fixes for conflicting ZoomInfo data (≥80% confidence)
- **Contextual Inferences**: Lower-confidence guesses for missing enrichment data (≥40% confidence)
- **Segment-Aware Analysis**: Use sales context and channel information for more accurate assessments
- **URL Intelligence**: Prevents redundant corrections like "example.com" → "https://example.com"
- **Mandatory Caution Rules**: Confidence scores < 100 must include specific caution/issue explanations

✅ **Professional Excel Export & Reporting**
- **Comprehensive Reports**: All 10 core fields plus 7 assessment outputs (confidence, explanations, corrections, inferences)
- **Visual Excellence**: Color-coded confidence scores, bordered tables, professional formatting
- **Summary Analytics**: Total leads, issue percentages, average confidence, trend analysis
- **Business-Ready Output**: Timestamped files with organized structure for executive reporting
- **Sample Export**: View [`sample_result.xlsx`](sample_result.xlsx) for bulk analysis report (leads with employee count > 1000)

✅ **Performance & User Experience Excellence**
- **10x Faster Execution**: Optimized batch processing and intelligent query optimization
- **Two-Step Workflow**: Preview queries before analysis for better control and validation
- **Smart UI Controls**: Context-aware interface with proper state management
- **Interactive Web Interface**: Real-time feedback and comprehensive testing capabilities

✅ **Quality Detection & Validation**
- **Advanced Quality Flags**: Enhanced `not_in_TAM` and `suspicious_enrichment` detection
- **Website Consistency Checks**: Validate alignment between multiple website sources
- **Company Size Agreement**: Cross-validate ZoomInfo employee counts with internal size estimates
- **Email Domain Intelligence**: Corporate vs. free email validation with business logic
- **Cross-Field Validation**: Advanced consistency checks across all enrichment fields

✅ **Enterprise Architecture & Dependencies**
- **Flask 3.1.1**: Latest stable framework with enhanced security and performance
- **simple-salesforce 1.12.6**: Enhanced JWT support, Bulk2.0 features, OAuth2 endpoints
- **OpenAI 1.90.0+**: Latest API features and improved response handling
- **openpyxl 3.1.5**: Professional Excel file generation and formatting
- **Modular Design**: Clean service layer separation with extensible architecture
- **Organized UI Structure**: Templates, CSS, and JavaScript properly separated following Flask best practices

## Project Structure

```
ZI_Enrichment_Assessment/
├── app.py                    # Main Flask application (clean & organized)
├── templates/                # HTML Templates
│   └── ui.html              # Interactive web UI template
├── static/                   # Static Assets
│   ├── css/
│   │   └── ringcentral-theme.css  # RingCentral brand styling
│   └── js/
│       └── ui-handlers.js    # JavaScript event handlers & functionality
├── docs/                     # Documentation
│   ├── README.md            # This file
│   ├── project_breakdown.md # Project requirements & overview
│   ├── lead_data_interpretation.md # AI scoring methodology
│   └── sample_result.xlsx   # Bulk analysis report example
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
    "Email": "lmcguire@acisolutions.net",
    "First_Channel__c": "Website",
    "SegmentName": "SMB",
    "LS_Company_Size_Range__c": "1-50",
    "Website": "acisolutions.net",
    "ZI_Website__c": "https://acisolutions.net",
    "ZI_Company_Name__c": "ACI Solutions Inc",
    "ZI_Employees__c": 24,
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
    "Email": "john.doe@gmail.com",

    "First_Channel__c": "Website",
    "SegmentName": "Enterprise",
    "LS_Company_Size_Range__c": "201-500",
    "Website": null,
    "ZI_Website__c": null,
    "ZI_Company_Name__c": "Example Corp",
    "ZI_Employees__c": 250,
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

## Comprehensive Lead Data Fields

The API collects and analyzes 10 core fields for comprehensive ZoomInfo enrichment assessment:

### **Core Lead Data (Trusted Sources)**
- `Id` - Salesforce Lead ID
- `Email` - Lead email address (provided directly by lead)
- `First_Channel__c` - Channel lead came in through (Website, Webinar, etc.)
- `SegmentName` - Sales segment classification (SMB, Mid-Market, Enterprise)
- `LS_Company_Size_Range__c` - Internal company size range estimate (1-50, 51-200, etc.)

### **Website Data Sources (Cross-Validation)**
- `Website` - Company website (lead-provided or sales rep entered)
- `ZI_Website__c` - Company website (ZoomInfo enriched)
- **Validation Logic**: Compare both sources for consistency and alignment with email domain

### **ZoomInfo Enrichment Data (To Be Validated)**
- `ZI_Company_Name__c` - Company name enriched by ZoomInfo
- `ZI_Employees__c` - Employee count enriched by ZoomInfo
- **Cross-Validation**: Compare against `LS_Company_Size_Range__c` and `SegmentName`

### **Computed Analysis Fields**
- `email_domain` - Extracted email domain for corporate vs. free email analysis
- `not_in_TAM` - Quality flag for large companies missing ZoomInfo enrichment
  - `true` when `ZI_Employees__c > 100` AND `ZI_Company_Name__c` is null/empty
  - Indicates incomplete enrichment for companies that should be in Total Addressable Market
- `suspicious_enrichment` - Quality flag for potentially incorrect ZoomInfo data
  - `true` when: free email domain + no website + company name + >100 employees
  - Suggests ZoomInfo may have incorrectly matched personal email with large company data

### **AI-Powered Assessment Results**
- `confidence_score` - Overall ZoomInfo enrichment reliability rating (0-100)
- `explanation_bullets` - 3-5 clear explanations with emoji indicators (✅ ⚠️ ❌)
- `corrections` - High-confidence fixes for conflicting ZoomInfo data (≥80% confidence)
- `inferences` - Lower-confidence guesses for missing enrichment data (≥40% confidence)

### **Enhanced Validation Capabilities**

**Website Consistency Validation:**
- Compare `Website` vs `ZI_Website__c` for alignment
- Validate both against `email_domain` if corporate domain
- Flag discrepancies for manual review

**Company Size Agreement Analysis:**
- Cross-validate `ZI_Employees__c` vs `LS_Company_Size_Range__c`
- Use `SegmentName` as additional context
- Identify significant discrepancies and determine more accurate source

**Business Context Integration:**
- Use `First_Channel__c` to understand lead source quality
- Apply `SegmentName` for segment-appropriate validation rules
- Consider sales context in confidence scoring

### **Excel Export Features**
- **Professional Formatting**: Color-coded confidence scores, bordered tables, proper column sizing
- **Summary Statistics**: Analysis overview including total leads, issue percentages, average confidence
- **Visual Indicators**: Red highlighting for quality issues, traffic light colors for confidence scores
- **Comprehensive Data**: All 10 core fields plus 7 assessment outputs (17 total columns)
- **Timestamped Files**: Automatic naming with date/time for easy organization
- **Sample Export**: View [`sample_excel.xlsx`](sample_excel.xlsx) for example output format

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

### Sample Excel Exports

The API provides two types of professional Excel reports:

**Single Lead Analysis**: **View the complete sample at [`sample_excel.xlsx`](sample_excel.xlsx)** to see:
- **Professional Business Format**: Color-coded confidence scores with traffic light system
- **Comprehensive Analysis**: All 10 core lead fields plus 7 AI assessment outputs
- **Individual Lead Focus**: Detailed assessment for single lead confidence analysis
- **Visual Excellence**: Bordered tables, proper column sizing, business-ready formatting

**Bulk Analysis Report**: **View the bulk sample at [`sample_result.xlsx`](sample_result.xlsx)** to see:
- **Multiple Lead Processing**: Bulk analysis of leads with employee count > 1000
- **Summary Statistics**: Overview including total leads, average confidence, issue percentages
- **Executive Reporting**: Business-ready format for stakeholder presentations
- **Batch Processing Results**: Demonstrates efficient handling of multiple leads simultaneously
- **Real Data Examples**: Actual ZoomInfo enrichment assessments with AI explanations

Both samples demonstrate how the API transforms raw lead data into actionable business intelligence with clear visual indicators for data quality issues.

### Project Architecture
- **Flask Application Factory Pattern**: Clean app initialization with template rendering
- **MVC Architecture**: Proper separation of templates, static assets, and application logic
- **Blueprints**: Organized route management
- **Service Layer**: Separation of business logic
- **Static Asset Organization**: CSS and JavaScript properly separated and organized
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