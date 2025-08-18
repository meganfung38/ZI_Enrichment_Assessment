# ZoomInfo Enrichment Quality Assessment API Documentation

A Flask API for assessing the quality and reliability of ZoomInfo-enriched lead data with hybrid scoring system combining rule-based completeness assessment and AI-powered coherence analysis.

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

## Demo

📹 **[Watch the Complete Demo](https://drive.google.com/file/d/1G5kbyXztMqzkW44-von2Jbu0ZlHpYQ92/view?usp=sharing)** - See the API in action with step-by-step usage examples

## Architecture

### Core Services

**SalesforceService** (`services/salesforce_service.py`)
- Lead data retrieval with expanded field set (personal and business data)
- Complex SOQL query support with security validation
- Quality flag computation and Joseph's system integration
- Optimized batch processing with robust Lead ID handling (15 ↔ 18 character conversion)

**JosephScoringWrapper** (`services/joseph_wrapper.py`)
- Rule-based acquisition completeness scoring (9 fields)
- Weighted enrichment completeness scoring (6 ZoomInfo fields)
- Data transformation and reference dataset integration
- Segment-aware scoring logic with dependency loading

**OpenAIService** (`services/openai_service.py`)
- AI coherence assessment for data consistency and reliability
- Intelligent corrections and inferences with mandatory external validation
- Advanced redundancy validation to prevent duplicate suggestions
- Contextual prompt engineering with external knowledge requirements

**ExcelService** (`services/excel_service.py`)
- Four-score export system with differentiated color coding
- Complete personal/business data export (27 columns)
- Professional RingCentral branding with score-specific formatting
- Summary statistics and detailed explanations for all scoring components

### Project Structure
```
ZI_Enrichment_Assessment/
├── app.py                    # Main Flask application (MVC pattern)
├── templates/
│   └── ui.html               # Interactive web interface
├── static/                   # Frontend assets with RingCentral theming
│   ├── css/
│   │   └── ringcentral-theme.css
│   └── js/
│       └── ui-handlers.js
├── config/                   # Configuration and environment management
├── services/                 # Core business logic services
│   ├── salesforce_service.py
│   ├── openai_service.py
│   ├── excel_service.py
│   ├── joseph_wrapper.py     # Integration adapter
│   └── joseph_system/        # Rule-based scoring system
│       ├── acquisition_completeness_score.py
│       ├── enrichment_completeness_score.py
│       ├── completeness_dependency_loader.py
│       └── dependencies/     # Reference CSV files
├── routes/                   # RESTful API endpoints with export functionality
└── docs/                     # Technical documentation and samples
```

## API Reference

### Connection Testing
- `GET /test-salesforce-connection` - Test Salesforce connectivity
- `GET /test-openai-connection` - Test OpenAI API connectivity
- `GET /health` - Service health check

### Lead Analysis
- `GET /lead/<lead_id>` - Get basic lead data with quality flags
- `GET /lead/<lead_id>/confidence` - **Hybrid assessment with rule-based and AI scoring**

### Bulk Analysis
- `POST /leads/preview-query` - Preview SOQL query results
- `POST /leads/analyze-query` - **Bulk analysis with hybrid scoring system**

### Excel Upload Workflow
- `POST /excel/parse` - Parse uploaded Excel file and extract headers
- `POST /excel/validate-lead-ids` - Validate Lead IDs with partial validation support
- `POST /excel/analyze` - **Analyze leads from Excel upload with hybrid assessment (handles invalid Lead IDs)**

### Export Endpoints (Cached Results)
- `POST /leads/export-analysis-data` - Export bulk analysis results to Excel
- `POST /leads/export-single-lead-data` - Export single lead assessment to Excel
- `POST /excel/export-analysis-with-file` - **Export Excel analysis with original data**

### Web Interface
- `GET /ui` - **Interactive web interface with step-by-step workflows**

## Lead Data Fields

The system analyzes 11+ core fields for comprehensive cross-validation:

### Core Lead Data
- `Id` - Salesforce Lead ID (15 or 18 character format)
- `Email` - Lead email address with domain extraction
- `First_Channel__c` - Lead source channel
- `SegmentName` - Sales segment (SMB, Mid-Market, Enterprise)
- `LS_Company_Size_Range__c` - Internal company size estimate

### Cross-Validation Sources
- `Website` vs `ZI_Website__c` - Lead-provided vs ZoomInfo website
- `Company` vs `ZI_Company_Name__c` - Lead-provided vs ZoomInfo company name
- `ZI_Employees__c` - ZoomInfo employee count for segment validation

### Computed Analysis
- `email_domain` - Extracted email domain for validation
- `not_in_TAM` - Quality flag for missing enrichment on large companies
- `suspicious_enrichment` - Quality flag for potentially incorrect data

### Hybrid Assessment Output
- `acquisition_completeness_score` - Rule-based scoring for original lead data (0-100)
- `enrichment_completeness_score` - Rule-based scoring for ZoomInfo enrichment (0-100)
- `confidence_score` - AI coherence assessment for data consistency (0-100)
- `final_confidence_score` - Weighted final score (15% + 15% + 70%)
- `explanation_bullets` - Clear explanations with emoji indicators and external validation
- `corrections` - High-confidence fixes with website validation
- `inferences` - Lower-confidence suggestions with accessibility checks

## Scoring System Detailed Overview

### **Acquisition Completeness Score (Rule-Based - Joseph's System)**
Evaluates completeness of original lead acquisition data:
- **Assessed Fields**: First Name, Last Name, Email Domain, Phone, State, Country, Industry, Company, Website
- **Methodology**: Weighted scoring using reference datasets (countries, territories, bad domains, industry cross-walk)
- **Validation**: Cross-references against external datasets for data quality verification
- **Output**: 0-100 percentage score indicating acquisition data completeness

### **Enrichment Completeness Score (Rule-Based - Joseph's System)**
Evaluates completeness of ZoomInfo enrichment data:
- **Assessed Fields**: ZI Company Name, ZI Website, ZI State, ZI Country, ZI Employee Count, Segment
- **Methodology**: Segment-aware weighted scoring with completeness validation logic
- **Dependencies**: Industry cross-walk, territory mappings, domain validation datasets
- **Output**: 0-100 percentage score indicating enrichment data completeness

### **AI Coherence Score (AI-Powered - OpenAI GPT-4o)**
Assesses data consistency, reliability, and logical coherence:
- **Focus**: Cross-field validation, external knowledge verification, data consistency analysis
- **Methodology**: Advanced prompt engineering with mandatory external validation requirements
- **Features**: Intelligent corrections, data inferences, redundancy prevention, external knowledge citation
- **Validation**: Website accessibility checks, free domain filtering, business logic verification
- **Output**: 0-100 confidence score with detailed explanations, corrections, and inferences

### **Final Confidence Score (Weighted Hybrid)**
Balanced assessment combining all scoring components:
- **Formula**: `(Acquisition × 0.15) + (Enrichment × 0.15) + (AI Coherence × 0.70)`
- **Rationale**: Emphasizes AI coherence assessment while incorporating rule-based completeness metrics
- **Benefits**: Balanced evaluation leveraging both rule-based precision and AI intelligence
- **Output**: Overall confidence rating (0-100) reflecting comprehensive data quality assessment

## Analysis Methods

### 1. Single Lead Assessment
Hybrid scoring combining rule-based completeness assessment with AI coherence analysis, including weighted final score.

### 2. SOQL Query Analysis  
Bulk processing supporting complex queries:
- Simple filters: `WHERE Email LIKE '%@gmail.com'`
- JOINs: `SELECT Lead.Id FROM Lead JOIN Account ON...`
- UNIONs: `SELECT Id FROM Lead WHERE... UNION ALL...`
- Subqueries: `WHERE AccountId IN (SELECT...)`

### 3. Excel File Upload
Step-by-step workflow with partial validation support:
1. **Parse** - Extract sheet names and column headers
2. **Select** - Choose sheet and Lead ID column
3. **Validate** - Verify Lead IDs with detailed valid/invalid breakdown
4. **Analyze** - Run hybrid assessment on valid leads (invalid Lead IDs preserved)
5. **Export** - Generate combined Excel report with four-score system and highlighted invalid Lead IDs

## Excel Export Features

Professional reports with RingCentral branding include:
- **Four-Score System**: Acquisition, Enrichment, AI Coherence, Final Confidence
- **Differentiated color coding** (Joseph's scores: purple/orange, AI scores: blue)
- **Complete personal/business data** (27 columns including FirstName, LastName, Phone, etc.)
- **Original data preservation** with hybrid analysis appended as new columns
- **Summary statistics** with weighted final score averages
- **Individual lead breakdowns** with detailed explanations for all components
- **Invalid Lead ID highlighting** (light red background for easy review)
- **Complete data integrity** (all original rows preserved, even invalid ones)

**Export Columns Added:**
- `First Name`, `Last Name`, `Phone`, `Country`, `Title`, `Industry` - Personal/business data
- `Acquisition_Score` - Rule-based completeness score for original data (0-100)
- `Enrichment_Score` - Rule-based completeness score for ZoomInfo data (0-100)
- `AI_Coherence_Score` - AI assessment of data consistency (0-100)
- `Final_Confidence_Score` - Weighted hybrid score (15% + 15% + 70%)
- `AI_Explanation` - Detailed explanations with external validation citations
- `AI_Corrections` - High-confidence data fixes (JSON format)
- `AI_Inferences` - Lower-confidence suggestions (JSON format)
- `AI_Not_in_TAM` - Quality flag for missing enrichment
- `AI_Suspicious_Enrichment` - Quality flag for suspicious data
- `AI_Status` - Analysis completion status (includes "Invalid Lead ID" for flagged rows)

## Enhanced Batch Processing for Large Datasets

### Overview

The system now includes optimized batch processing specifically designed to handle Excel files with 50,000+ Lead IDs efficiently while preventing Salesforce connection timeouts and API rate limiting issues.

### Key Features

#### 1. **Multi-Level Batching Strategy**
- **Salesforce Queries**: Processes leads in configurable batches (default: 150 leads per batch)
- **AI Processing**: Sub-batches AI assessments (default: 50 leads per sub-batch) to manage OpenAI rate limits
- **Connection Management**: Automatically refreshes Salesforce connections between batches
- **Error Recovery**: Continues processing even if individual batches fail

#### 2. **Automatic Dataset Detection**
- **Small Datasets** (≤1000 leads): Uses standard processing for optimal speed
- **Large Datasets** (>1000 leads): Automatically switches to batch-optimized processing
- **Configurable Threshold**: Customize via `LARGE_DATASET_THRESHOLD` environment variable

#### 3. **Performance Optimizations**
```
Processing Pipeline for 50k Leads:
Excel Upload → Validation (150/batch) → Salesforce Data (150/batch) → AI Processing (50/batch) → Export
```

#### 4. **Progress Tracking & Monitoring**
- Real-time batch completion tracking
- Performance metrics (leads/second, avg batch time)
- Success/failure rates per batch
- Detailed logging for troubleshooting

### API Endpoints

#### Standard Excel Analysis
```
POST /excel/analyze
```
- Automatically detects dataset size
- Uses batch optimization for >1000 leads
- Maintains backward compatibility

#### Batch-Optimized Analysis
```
POST /excel/analyze-batch-optimized
```
- Explicit batch processing with configurable parameters
- Form parameters:
  - `batch_size`: Salesforce batch size (50-200, default: 200)
  - `ai_batch_size`: AI processing batch size (10-100, default: 50)

### Configuration Options

Environment variables for fine-tuning batch processing:

```bash
# Salesforce batch size (recommended: 100-150 for stability)
BATCH_SIZE_SALESFORCE=150

# AI processing batch size (recommended: 25-50 for rate limiting)
BATCH_SIZE_AI=50

# Lead ID validation batch size
BATCH_SIZE_VALIDATION=150

# Threshold for using batch optimization
LARGE_DATASET_THRESHOLD=1000

# Delays between batches (milliseconds)
BATCH_DELAY_MS=50
AI_BATCH_DELAY_MS=100
```

### Performance Metrics

#### Expected Processing Times (50k Leads)
- **Validation**: ~5-8 minutes (150 leads/batch)
- **Salesforce Data Retrieval**: ~10-15 minutes (150 leads/batch) 
- **AI Processing**: ~45-60 minutes (50 leads/batch, respecting rate limits)
- **Total**: ~60-80 minutes for complete analysis

#### Resource Management
- **Memory**: Processes in chunks to prevent memory exhaustion
- **API Limits**: Built-in rate limiting and exponential backoff
- **Connection Stability**: Automatic connection refresh between batches
- **Error Handling**: Graceful degradation with partial results

### Batch Processing Benefits

1. **Prevents Timeouts**: No single operation exceeds Salesforce timeout limits
2. **Rate Limit Compliance**: Respects both Salesforce and OpenAI API limits  
3. **Memory Efficient**: Processes data in chunks without loading entire dataset
4. **Fault Tolerant**: Continues processing even if individual batches fail
5. **Progress Visibility**: Real-time tracking of processing status
6. **Scalable**: Handles datasets from 1K to 100K+ leads efficiently

### Best Practices

#### For 50k+ Lead Processing:
- Use `BATCH_SIZE_SALESFORCE=100` for maximum stability
- Set `AI_BATCH_DELAY_MS=200` to be conservative with OpenAI rate limits
- Monitor processing via console logs for progress tracking
- Consider processing during off-peak hours for optimal API performance

#### Error Recovery:
- Failed batches are logged but don't stop overall processing
- Invalid Lead IDs are tracked separately and included in final export
- Connection failures trigger automatic reconnection attempts

## Usage Examples

### Web Interface (Recommended)
The interactive interface at `/ui` provides:
- **Single Lead**: Enter Lead ID for instant confidence assessment
- **Bulk Analysis**: Write SOQL queries with preview before full analysis
- **Excel Upload**: Drag-and-drop workflow with partial validation and visual error flagging
- **Professional Export**: Download branded Excel reports with invalid Lead ID highlighting

### API Examples

**Single Lead Assessment**
```bash
curl http://localhost:5000/lead/00Q5e00000ABC123/confidence
```

**Bulk Analysis with Export**
```bash
# 1. Run analysis
curl -X POST http://localhost:5000/leads/analyze-query \
  -H "Content-Type: application/json" \
  -d '{"soql_query": "WHERE Email LIKE '\''%@gmail.com'\''", "max_analyze": 10}'

# 2. Export results (using cached data)
curl -X POST http://localhost:5000/leads/export-analysis-data \
  -H "Content-Type: application/json" \
  -d '{"analysis_results": [...], "summary_data": {...}}'
```

## Response Format

All endpoints return standardized JSON:

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

## Key Enhancements

### Advanced AI Assessment
- **Redundancy Validation**: Prevents duplicate corrections and inferences
- **Context-Aware Scoring**: Uses segment and channel data for accurate assessment
- **Smart Company Matching**: Detects when ZoomInfo and lead company names are equivalent
- **Data Quality Filtering**: Blocks free email domains and validates website accessibility
- **Enhanced Data Types**: Rejects vague employee counts and enforces proper formatting

### Robust Data Handling
- **Lead ID Conversion**: Automatic 15 ↔ 18 character Salesforce ID handling
- **Batch Optimization**: Efficient processing for large datasets
- **Error Recovery**: Graceful handling of missing or invalid data
- **Partial Validation**: Analysis proceeds with valid Lead IDs while preserving invalid ones
- **Visual Error Flagging**: Invalid Lead IDs clearly marked for review in exports

### Professional Export
- **Cached Results**: Export endpoints use stored analysis data for consistency
- **Brand Compliance**: RingCentral colors and professional formatting
- **Data Integrity**: Original Excel data preserved with AI analysis appended
- **Invalid Lead ID Highlighting**: Light red background for easy identification and review
- **Complete Data Preservation**: All original rows maintained, including invalid Lead IDs

### Enhanced UX
- **Step-by-Step Workflows**: Clear validation at each stage
- **Real-Time Feedback**: Progress indicators and detailed error messages
- **Responsive Design**: Modern interface with intuitive navigation

---

**Additional Resources:**
- **[API Demo Video](https://drive.google.com/file/d/1G5kbyXztMqzkW44-von2Jbu0ZlHpYQ92/view?usp=sharing)** - Complete walkthrough and usage examples
- **[Project Overview](project_breakdown.md)** - Requirements and specifications
- **[AI Methodology](lead_data_interpretation.md)** - Scoring and assessment details
- **[Sample Exports](https://docs.google.com/spreadsheets/d/1y-y4aXOqWRyQstc8c1il3suKUsz_t2He/edit?usp=sharing&ouid=113726783832302437979&rtpof=true&sd=true)** - Example Excel reports (RingCentral employees only) 