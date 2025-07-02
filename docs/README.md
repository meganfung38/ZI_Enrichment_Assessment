# ZoomInfo Enrichment Quality Assessment API Documentation

A Flask API for assessing the quality and reliability of ZoomInfo-enriched lead data with OpenAI-powered confidence scoring and professional Excel export capabilities.

## Setup

### 1. Environment Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r config/requirements.txt

# Configure environment
cp config/env.example .env
# Edit .env with your credentials
```

### 2. Required Environment Variables
```bash
# Salesforce
SF_USERNAME=your_username
SF_PASSWORD=your_password  
SF_SECURITY_TOKEN=your_token
SF_DOMAIN=login  # or 'test' for sandbox

# OpenAI
OPENAI_API_KEY=sk-your-key-here
```

### 3. Run Application
```bash
python app.py
```

Access the web interface at `http://localhost:5000/ui`

## Architecture

### Core Services

**SalesforceService** (`services/salesforce_service.py`)
- Lead data retrieval with 10+ fields
- Complex SOQL query support with security validation
- Quality flag computation (`not_in_TAM`, `suspicious_enrichment`)
- Batch processing optimization

**OpenAIService** (`services/openai_service.py`)
- AI-powered confidence scoring (0-100)
- Intelligent corrections and inferences
- Redundancy validation to prevent duplicate suggestions
- Context-aware prompt engineering

**ExcelService** (`services/excel_service.py`)
- Professional report generation with color-coding
- Summary statistics and individual lead details
- Multiple export formats (single lead, bulk analysis, Excel upload)

### Project Structure
```
ZI_Enrichment_Assessment/
├── app.py                    # Main Flask application
├── templates/ui.html         # Web interface
├── static/                   # CSS and JavaScript
├── config/                   # Configuration files
├── services/                 # Business logic
├── routes/                   # API endpoints
└── docs/                     # Documentation
```

## API Reference

### Connection Testing
- `GET /test-salesforce-connection` - Test Salesforce connectivity
- `GET /test-openai-connection` - Test OpenAI API connectivity
- `GET /health` - Service health check

### Lead Analysis
- `GET /lead/<lead_id>` - Get basic lead data with quality flags
- `GET /lead/<lead_id>/confidence` - **AI-powered confidence assessment**

### Bulk Analysis
- `POST /leads/preview-query` - Preview SOQL query results
- `POST /leads/analyze-query` - **Bulk analysis with AI scoring**

### Excel Operations
- `POST /excel/parse` - Parse uploaded Excel file
- `POST /excel/validate-lead-ids` - Validate Lead IDs from Excel
- `POST /excel/analyze` - Analyze leads from Excel upload

### Export Endpoints
- `POST /leads/export-analysis-data` - Export bulk analysis results
- `POST /leads/export-single-lead-data` - Export single lead assessment
- `POST /excel/export-analysis-with-file` - Export Excel analysis with original data

### Web Interface
- `GET /ui` - **Interactive web interface (recommended)**

## Lead Data Fields

The system analyzes 10+ core fields for comprehensive assessment:

### Core Lead Data
- `Id` - Salesforce Lead ID
- `Email` - Lead email address
- `First_Channel__c` - Lead source channel
- `SegmentName` - Sales segment (SMB, Mid-Market, Enterprise)
- `LS_Company_Size_Range__c` - Internal size estimate

### Website Sources (Cross-Validation)
- `Website` - Lead-provided website
- `ZI_Website__c` - ZoomInfo-enriched website

### ZoomInfo Enrichment Data
- `ZI_Company_Name__c` - ZoomInfo company name
- `ZI_Employees__c` - ZoomInfo employee count

### Computed Analysis
- `email_domain` - Extracted email domain
- `not_in_TAM` - Quality flag for missing enrichment on large companies
- `suspicious_enrichment` - Quality flag for potentially incorrect data

### AI Assessment Output
- `confidence_score` - Overall reliability rating (0-100)
- `explanation_bullets` - Clear explanations with emoji indicators
- `corrections` - High-confidence fixes (≥80% confidence)
- `inferences` - Lower-confidence guesses (≥40% confidence)

## SOQL Query Support

### Supported Query Types

**Simple Queries**
```sql
WHERE Email LIKE '%@gmail.com'
WHERE ZI_Employees__c > 100
SELECT Id FROM Lead WHERE Company = 'Acme Corp'
```

**Complex Queries with JOINs**
```sql
SELECT Lead.Id FROM Lead 
JOIN Account ON Lead.AccountId = Account.Id 
WHERE Account.Industry = 'Technology'
```

**UNION Queries**
```sql
SELECT Id FROM Lead WHERE ZI_Employees__c > 100
UNION ALL
SELECT Id FROM Lead WHERE Email LIKE '%@enterprise.com'
```

**Subqueries**
```sql
SELECT Id FROM Lead 
WHERE AccountId IN (
    SELECT Id FROM Account WHERE AnnualRevenue > 1000000
)
```

### Security Restrictions
- Must return Lead IDs only
- No direct access to non-Lead objects
- Dangerous SQL operations blocked (DELETE, UPDATE, etc.)

## Usage Examples

### Web Interface (Recommended)
The interactive web interface at `/ui` provides the easiest way to:
- Test single lead assessments
- Run bulk SOQL query analysis
- Upload and analyze Excel files
- Export results to professional Excel reports

### API Examples

**Single Lead Assessment**
```bash
curl http://localhost:5000/lead/00Q5e00000ABC123/confidence
```

**Bulk Analysis**
```bash
curl -X POST http://localhost:5000/leads/analyze-query \
  -H "Content-Type: application/json" \
  -d '{
    "soql_query": "WHERE Email LIKE '\''%@gmail.com'\''", 
    "max_analyze": 10,
    "include_ai_assessment": true
  }'
```

**Preview Query**
```bash
curl -X POST http://localhost:5000/leads/preview-query \
  -H "Content-Type: application/json" \
  -d '{
    "soql_query": "WHERE ZI_Employees__c > 100",
    "preview_limit": 50
  }'
```

## Response Examples

### Single Lead Confidence Assessment
```json
{
  "status": "success",
  "message": "Lead confidence assessment completed successfully",
  "lead_data": {
    "Id": "00Q5e00000ABC123",
    "Email": "john.doe@acme.com",
    "SegmentName": "Enterprise",
    "ZI_Company_Name__c": "Acme Corporation",
    "ZI_Employees__c": 1500,
    "not_in_TAM": false,
    "suspicious_enrichment": false
  },
  "confidence_assessment": {
    "confidence_score": 85,
    "explanation_bullets": [
      "✅ Email domain matches company domain.",
      "✅ Employee count aligns with Enterprise segment.",
      "⚠️ No website data available for validation."
    ],
    "corrections": {},
    "inferences": {
      "ZI_Website__c": "https://acme.com"
    }
  }
}
```

### Bulk Analysis Response
```json
{
  "status": "success",
  "message": "Analysis completed successfully",
  "data": {
    "summary": {
      "leads_analyzed": 25,
      "leads_with_issues": 8,
      "issue_percentage": "32%",
      "avg_confidence_score": 73.2,
      "ai_assessments_successful": 25
    },
    "leads": [
      {
        "Id": "00Q5e00000ABC123",
        "Email": "user@company.com",
        "confidence_assessment": {
          "confidence_score": 85,
          "explanation_bullets": ["..."],
          "corrections": {},
          "inferences": {}
        }
      }
    ]
  }
}
```

## Excel Export Features

The API generates professional Excel reports with:

- **Color-coded confidence scores** (Red: 0-59, Yellow: 60-79, Green: 80-100)
- **Comprehensive data** (10+ lead fields + AI assessment outputs)
- **Summary statistics** (total leads, issue percentages, averages)
- **Professional formatting** (bordered tables, proper sizing)
- **Individual lead breakdowns** with detailed AI explanations

**Sample Reports:**
- [`sample_result.xlsx`](sample_result.xlsx) - Bulk analysis example
- View actual export format and styling

## Error Handling

All endpoints return standardized JSON responses:

**Success Response**
```json
{
  "status": "success",
  "message": "Operation completed successfully",
  "data": { /* response data */ }
}
```

**Error Response**
```json
{
  "status": "error",
  "message": "Descriptive error message"
}
```

## Development

### Adding New Features
1. **Business Logic**: Add to appropriate service in `services/`
2. **API Endpoints**: Add routes to `routes/api_routes.py`
3. **Configuration**: Add options to `config/config.py`
4. **Frontend**: Update `static/js/ui-handlers.js` for web interface

### Testing
- Use `/test-salesforce-connection` and `/test-openai-connection` for connectivity
- Use `/ui` for interactive testing
- Check `/health` for service status

---

For project overview and requirements, see [project_breakdown.md](project_breakdown.md)  
For AI methodology details, see [lead_data_interpretation.md](lead_data_interpretation.md) 