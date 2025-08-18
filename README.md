# ZoomInfo Enrichment Quality Assessment API

A Flask API for assessing the quality and reliability of ZoomInfo-enriched lead data with AI-powered confidence scoring and professional Excel export capabilities.

## Quick Start

```bash
# Install dependencies
pip install -r config/requirements.txt

# Set up environment
cp config/env.example .env
# Edit .env with your Salesforce and OpenAI credentials

# Run the application
python app.py
```

Access the web interface at `http://localhost:5000/ui`

## Demo

📹 **[Watch the API Demo](https://drive.google.com/file/d/1G5kbyXztMqzkW44-von2Jbu0ZlHpYQ92/view?usp=sharing)** - Complete walkthrough of the tool's features and workflow

## Key Features

🧠 **Hybrid Scoring System**
- **Rule-Based Assessment**: Joseph's system provides acquisition and enrichment completeness scores
- **AI Coherence Analysis**: OpenAI-driven coherence scoring for data consistency and reliability
- **Weighted Final Score**: 15% acquisition + 15% enrichment + 70% AI coherence for balanced assessment
- Intelligent corrections and inferences with advanced redundancy validation
- Context-aware analysis using sales segment and channel data
- Smart duplicate detection to prevent redundant suggestions
- Free email domain validation and website accessibility verification

📊 **Enhanced Excel Workflow**
- **Partial Validation Support**: Analysis proceeds even with some invalid Lead IDs
- **Visual Invalid ID Flagging**: Invalid Lead ID rows highlighted in light red for easy review
- **Comprehensive Validation Summary**: Shows exact count of valid vs invalid Lead IDs
- **Graceful Error Handling**: No data loss - all original Excel data preserved in export

🔍 **Comprehensive Data Analysis**
- **Joseph's Rule-Based Scoring**: Acquisition completeness (9 fields) and enrichment completeness (6 fields)
- **AI Coherence Assessment**: Data consistency and reliability validation with external knowledge
- Automated quality flags (`not_in_TAM`, `suspicious_enrichment`)
- Cross-validation between ZoomInfo data and internal estimates
- Robust Lead ID handling (15 ↔ 18 character conversion)
- Enhanced data type validation with reference dataset integration

📊 **Three Analysis Methods**
- **Single Lead Assessment**: Hybrid scoring with detailed explanations for all three components
- **SOQL Query Analysis**: Bulk processing with complex query support and weighted final scores
- **Excel File Upload**: Batch analysis with hybrid scoring and comprehensive Excel export

📈 **Professional Excel Export**
- **Four-Score System**: Acquisition Score, Enrichment Score, AI Coherence Score, Final Confidence Score
- RingCentral-branded reports with color-coded scoring (Joseph's scores in purple/orange, AI scores in blue)
- Complete lead data export including FirstName, LastName, Phone, Country, Title, Industry
- Summary statistics and individual lead breakdowns with detailed explanations
- **Invalid Lead ID Highlighting**: Light red background for easy identification and review
- **Complete Data Preservation**: All original Excel data maintained with hybrid analysis appended

⚡ **Enhanced User Experience**
- Step-by-step workflow with validation at each stage
- Real-time progress feedback and detailed error handling
- Responsive web interface with modern UI/UX design
- Comprehensive debug logging for troubleshooting

## Tech Stack

- **Backend**: Flask 3.1.1, Python 3.8+
- **Salesforce**: simple-salesforce 1.12.6 with optimized batch processing
- **AI**: OpenAI API 1.90.0+ with intelligent prompt engineering
- **Excel**: openpyxl 3.1.5 with advanced formatting and theming
- **Frontend**: Vanilla JavaScript, RingCentral-themed CSS

## Project Structure

```
ZI_Enrichment_Assessment/
├── app.py                           # Main Flask application (MVC pattern)
├── templates/
│   └── ui.html                      # Web interface template
├── static/                          # Frontend assets
│   ├── css/
│   │   └── ringcentral-theme.css    # Professional brand styling
│   └── js/
│       └── ui-handlers.js           # Interactive UI logic
├── config/                          # Configuration and dependencies
│   ├── config.py                    # Environment and settings
│   ├── requirements.txt             # Python dependencies
│   └── env.example                  # Configuration template
├── services/                        # Core business logic
│   ├── salesforce_service.py        # SF API with batch optimization
│   ├── openai_service.py           # AI coherence assessment  
│   ├── excel_service.py            # Professional report generation
│   ├── joseph_wrapper.py           # Integration adapter for Joseph's system
│   └── joseph_system/              # Rule-based scoring system
│       ├── acquisition_completeness_score.py
│       ├── enrichment_completeness_score.py
│       ├── completeness_dependency_loader.py
│       ├── PhoneValidation_BrianChiosi.py
│       ├── coherence_score.py       # (not used in integration)
│       └── dependencies/           # Reference CSV files
├── routes/                          # API endpoint definitions
│   └── api_routes.py               # RESTful API with export endpoints
└── docs/                           # Documentation and samples
    ├── README.md                   # Detailed technical documentation
    ├── project_breakdown.md        # Requirements and specifications
    ├── lead_data_interpretation.md # AI methodology and scoring
    └── batch_processing_implementation.md # Batch processing details
```

## Core Services

### SalesforceService
- Lead data retrieval with expanded field set (FirstName, LastName, Phone, etc.)
- Complex SOQL query support with security validation
- Quality flag computation and Joseph's system integration
- Optimized batch processing for large datasets

### JosephScoringWrapper
- **Acquisition Completeness**: Rule-based scoring for 9 original lead data fields
- **Enrichment Completeness**: Weighted scoring for 6 ZoomInfo enrichment fields
- Data transformation and integration with reference datasets
- Segment-aware scoring logic with dependency loading

### OpenAIService  
- **AI Coherence Assessment**: Data consistency and reliability validation
- Intelligent corrections and inferences with external knowledge requirements
- Advanced redundancy validation to prevent duplicate suggestions
- Contextual prompt engineering with mandatory external validation

### ExcelService
- **Four-Score Export System**: Acquisition, Enrichment, AI Coherence, Final Confidence
- RingCentral-branded reports with differentiated color coding
- Expanded data export (27 columns including personal/business fields)
- Robust Lead ID matching (15 ↔ 18 character handling)

## API Endpoints

### Analysis Endpoints
- `GET /lead/<id>/confidence` - Single lead hybrid assessment (rule-based + AI)
- `POST /leads/analyze-query` - Bulk SOQL query analysis with weighted scoring
- `POST /excel/analyze` - Excel file upload analysis with four-score system

### Export Endpoints (Cached Results)
- `POST /leads/export-analysis-data` - Export bulk analysis results
- `POST /leads/export-single-lead-data` - Export single lead assessment
- `POST /excel/export-analysis-with-file` - Export Excel analysis with original data

### Excel Workflow
- `POST /excel/parse` - Parse uploaded Excel file
- `POST /excel/validate-lead-ids` - Validate Lead IDs with Salesforce
- `POST /excel/export-analysis-with-file` - Export combined results

### Utilities
- `GET /test-salesforce-connection` - Test SF connectivity
- `GET /test-openai-connection` - Test OpenAI API connectivity  
- `GET /ui` - Interactive web interface

## Configuration

Required environment variables in `.env`:

```bash
# Salesforce
SF_USERNAME=your_username
SF_PASSWORD=your_password
SF_SECURITY_TOKEN=your_token
SF_DOMAIN=login  # or 'test' for sandbox

# OpenAI
OPENAI_API_KEY=sk-your-key-here
```

## Lead Data Fields

The system analyzes 11+ core fields with cross-validation:

**Personal Data**: ID, FirstName, LastName, Phone, Country, Title, Industry  
**Lead Information**: Email, Channel, Segment, Size Range  
**Website Sources**: Lead Website vs ZoomInfo Website  
**Company Sources**: Lead Company vs ZoomInfo Company Name  
**ZoomInfo Data**: Employee Count, Enrichment Quality  
**Computed Fields**: Email domain, Quality flags  
**Hybrid Assessment**: Acquisition score, Enrichment score, AI coherence, Final confidence

## Scoring System Overview

### 1. **Acquisition Completeness Score (Rule-Based)**
Joseph's system evaluates 9 original lead data fields:
- **Personal Data**: First Name, Last Name, Phone, State, Country  
- **Business Data**: Email Domain, Industry, Company, Website
- **Methodology**: Weighted scoring using reference datasets for validation
- **Output**: Percentage score (0-100) indicating data completeness quality

### 2. **Enrichment Completeness Score (Rule-Based)**  
Joseph's system evaluates 6 ZoomInfo enrichment fields:
- **ZI Data**: Company Name, Website, State, Country, Employee Count
- **Methodology**: Segment-aware weighted scoring with completeness validation
- **Dependencies**: Reference datasets for domain validation and industry cross-walk
- **Output**: Percentage score (0-100) indicating enrichment quality

### 3. **AI Coherence Score (AI-Powered)**
OpenAI assessment of data consistency and reliability:
- **Focus**: Cross-field validation, external knowledge verification, logical consistency
- **Methodology**: GPT-4o analysis with mandatory external validation requirements
- **Features**: Corrections, inferences, redundancy validation, external knowledge citation
- **Output**: Confidence score (0-100) with detailed explanations

### 4. **Final Confidence Score (Weighted Combination)**
Balanced assessment combining all components:
- **Formula**: (Acquisition × 15%) + (Enrichment × 15%) + (AI Coherence × 70%)
- **Rationale**: Emphasizes AI coherence while incorporating rule-based completeness
- **Output**: Overall confidence rating reflecting data quality and reliability

## Usage Examples

### Web Interface (Recommended)
Visit `http://localhost:5000/ui` for interactive analysis with:
- Single lead hybrid assessment with toggle-based results display
- Bulk SOQL query analysis with weighted final scores
- Excel file upload with four-score system and comprehensive export
- Professional export with alternating lead backgrounds for easy review

### API Usage
```bash
# Single lead assessment
curl http://localhost:5000/lead/00Q5e00000ABC123/confidence

# Bulk analysis  
curl -X POST http://localhost:5000/leads/analyze-query \
  -H "Content-Type: application/json" \
  -d '{"soql_query": "WHERE Email LIKE '\''%@gmail.com'\''", "max_analyze": 10}'
```

## Documentation

- **[API Demo Video](https://drive.google.com/file/d/1G5kbyXztMqzkW44-von2Jbu0ZlHpYQ92/view?usp=sharing)** - Complete walkthrough and usage examples
- **[Technical Documentation](docs/README.md)** - Complete API reference and setup
- **[Project Specifications](docs/project_breakdown.md)** - Requirements and architecture
- **[AI Methodology](docs/lead_data_interpretation.md)** - Scoring and assessment details  
- **[Sample Exports](https://docs.google.com/spreadsheets/d/1y-y4aXOqWRyQstc8c1il3suKUsz_t2He/edit?usp=sharing&ouid=113726783832302437979&rtpof=true&sd=true)** - Example Excel reports (RingCentral employees only)

---

For detailed API documentation and advanced usage, see [docs/README.md](docs/README.md) 