# ZoomInfo Enrichment Quality Assessment API

A Flask API for assessing the quality and reliability of ZoomInfo-enriched lead data with AI-powered confidence scoring and Excel export capabilities.

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

## Key Features

🧠 **AI-Powered Assessment**
- OpenAI-driven confidence scoring (0-100) for ZoomInfo enrichment quality
- Intelligent corrections and inferences with redundancy validation
- Context-aware analysis using sales segment and channel data

🔍 **Comprehensive Data Analysis**
- 10+ lead fields including dual website sources and employee counts
- Automated quality flags (`not_in_TAM`, `suspicious_enrichment`)
- Cross-validation between ZoomInfo data and internal estimates

📊 **Flexible Query System**
- Support for complex SOQL queries (JOINs, UNIONs, subqueries)
- Two-step workflow: preview queries before full analysis
- Batch processing with configurable limits

📈 **Professional Excel Export**
- Color-coded confidence scores and professional formatting
- Summary statistics and individual lead breakdowns
- Sample exports available in [`docs/`](docs/) folder

⚡ **Multiple Analysis Options**
- Single lead confidence assessment
- Bulk SOQL query analysis
- Excel file upload for Lead ID batch processing

## Tech Stack

- **Backend**: Flask 3.1.1, Python 3.8+
- **Salesforce**: simple-salesforce 1.12.6
- **AI**: OpenAI API 1.90.0+
- **Excel**: openpyxl 3.1.5
- **Frontend**: Vanilla JavaScript, RingCentral-themed CSS

## Project Structure

```
ZI_Enrichment_Assessment/
├── app.py                           # Main Flask application
├── templates/ui.html                # Web interface template
├── static/                          # CSS and JavaScript assets
│   ├── css/ringcentral-theme.css
│   └── js/ui-handlers.js
├── config/                          # Configuration and dependencies
│   ├── config.py
│   ├── requirements.txt
│   └── env.example
├── services/                        # Core business logic
│   ├── salesforce_service.py        # Salesforce API integration
│   ├── openai_service.py           # AI confidence assessment
│   └── excel_service.py            # Excel export functionality
├── routes/                          # API endpoint definitions
│   └── api_routes.py
└── docs/                           # Documentation and samples
    ├── README.md                   # Detailed API documentation
    ├── project_breakdown.md
    ├── lead_data_interpretation.md
    └── sample_result.xlsx
```

## Core Services

### SalesforceService
- Lead data retrieval with 10+ fields
- Complex SOQL query support
- Quality flag computation
- Batch processing optimization

### OpenAIService
- AI-powered confidence scoring
- Intelligent corrections and inferences
- Redundancy validation to prevent duplicate suggestions
- Context-aware prompt engineering

### ExcelService
- Professional report generation
- Color-coded confidence visualization
- Summary statistics and individual lead details
- Multiple export formats (single lead, bulk analysis, Excel upload)

## API Endpoints

### Core Analysis
- `GET /lead/<id>/confidence` - Single lead AI assessment
- `POST /leads/analyze-query` - Bulk SOQL query analysis
- `POST /leads/preview-query` - Preview query results

### Excel Operations
- `POST /excel/parse` - Parse uploaded Excel file
- `POST /excel/validate-lead-ids` - Validate Lead IDs from Excel
- `POST /excel/analyze` - Analyze leads from Excel file

### Export Endpoints
- `POST /leads/export-analysis-data` - Export bulk analysis results
- `POST /leads/export-single-lead-data` - Export single lead assessment
- `POST /excel/export-analysis-with-file` - Export Excel analysis with original data

### Utilities
- `GET /test-salesforce-connection` - Test Salesforce connectivity
- `GET /test-openai-connection` - Test OpenAI API connectivity
- `GET /ui` - Web interface

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

The system analyzes 10+ core fields:

**Lead Information**: ID, Email, Channel, Segment, Size Range
**Website Sources**: Lead-provided Website, ZoomInfo Website
**ZoomInfo Data**: Company Name, Employee Count
**Computed Fields**: Email domain, Quality flags
**AI Assessment**: Confidence score, Explanations, Corrections, Inferences

## Usage Examples

### Web Interface (Recommended)
Visit `http://localhost:5000/ui` for interactive analysis

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

- **[Complete API Guide](docs/README.md)** - Detailed setup and API reference
- **[Project Overview](docs/project_breakdown.md)** - Requirements and specifications
- **[AI Methodology](docs/lead_data_interpretation.md)** - Scoring and assessment details
- **[Sample Export](docs/sample_result.xlsx)** - Example Excel output

---

For detailed API documentation and advanced usage, see [docs/README.md](docs/README.md) 