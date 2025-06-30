# ZoomInfo Enrichment Quality Assessment API

A Flask API for assessing the quality and reliability of ZoomInfo-enriched lead data with AI-powered confidence scoring, explanations, and Excel export capabilities.

## Quick Start

```bash
# Install dependencies (updated to latest versions)
pip install -r config/requirements.txt

# Set up environment
cp config/env.example .env
# Edit .env with your Salesforce and OpenAI credentials

# Run the application
python app.py
```

## Latest Updates (January 2025)

✅ **Excel Export Functionality**
- **Professional Excel Reports**: Download analysis results in formatted XLSX files
- **Summary Statistics**: Comprehensive overview at the top of each report
- **Visual Formatting**: Color-coded confidence scores and quality flags
- **Batch & Single Lead Export**: Export both multi-lead analysis and individual assessments

✅ **Enhanced Analyze-Query Endpoint**
- **Performance Optimized**: 10x faster execution for multi-lead analysis
- **Streamlined UI**: Removed unnecessary options, always includes AI confidence scoring
- **Two-Step Process**: Preview queries before running full analysis
- **Smart Export Controls**: Export buttons only enabled after successful analysis

✅ **AI-Powered ZoomInfo Enrichment Assessment**
- **OpenAI Integration**: Advanced ZoomInfo enrichment quality assessment with confidence scores (0-100)
- **Smart Explanations**: Clear bullet-point rationale with emoji indicators (✅ ⚠️ ❌)
- **Data Corrections & Inferences**: AI suggests fixes and fills missing enrichment gaps
- **Email Domain Analysis**: Automatic extraction and validation of email domains

✅ **Enhanced Lead Analysis**
- **Extended Quality Flags**: Improved detection of suspicious ZoomInfo enrichment patterns
- **Email Domain Extraction**: New `email_domain` field for all lead queries
- **Unicode Support**: Proper emoji display in JSON responses
- **Comprehensive Data Validation**: Cross-field consistency checks for enrichment reliability

✅ **Dependencies Updated**
- **Flask**: Updated to v3.1.1 (latest stable) - improved performance and security
- **simple-salesforce**: Updated to v1.12.6 - enhanced JWT support, Bulk2.0 features, OAuth2 endpoints
- **python-dotenv**: Updated to v1.0.1 - latest bug fixes
- **OpenAI**: Updated to v1.90.0+ - latest API features and improvements
- **openpyxl**: Added v3.1.5 - Excel file generation and formatting

## Key Features

📊 **Excel Export & Reporting**
- Professional XLSX reports with formatted tables and summary statistics
- Color-coded confidence scores (Green: 80+, Yellow: 60-79, Red: <60)
- Visual highlighting for quality flags and enrichment issues
- Automated file naming with timestamps for easy organization

🧠 **AI-Powered ZoomInfo Enrichment Assessment**
- Confidence scoring from 0-100 based on enrichment completeness, consistency, and flags
- Actionable explanations with clear visual indicators for enrichment reliability
- Automated data correction suggestions for ZoomInfo fields
- Intelligent inference for missing enrichment data

🔍 **Advanced ZoomInfo Analysis**
- Automated quality flags specifically for ZoomInfo-enriched data
- `not_in_TAM` detection for large companies missing ZoomInfo enrichment
- `suspicious_enrichment` detection for potentially incorrect ZoomInfo data
- Email domain validation and corporate vs. free email detection
- **Flexible SOQL Query Support**: JOINs, UNIONs, and complex queries allowed if they return Lead IDs

⚡ **Performance & User Experience**
- Optimized multi-lead analysis with 10x performance improvement
- Two-step preview process for query validation
- Smart UI controls that enable features only when appropriate
- Web interface for easy testing and analysis

🚀 **Modern Architecture**
- Flask 3.1.1 with application factory pattern
- Modular service layer design with Excel export capabilities
- OpenAI integration for confidence scoring
- Comprehensive error handling and logging
- Unicode-safe JSON responses

## Quick API Examples

```bash
# Test connections
curl http://localhost:5000/test-openai-connection
curl http://localhost:5000/test-salesforce-connection

# Get basic lead data with quality flags
curl http://localhost:5000/lead/00Q5e00000ABC123

# Get AI-powered ZoomInfo enrichment assessment
curl http://localhost:5000/lead/00Q5e00000ABC123/confidence

# Export single lead assessment to Excel
curl http://localhost:5000/lead/00Q5e00000ABC123/confidence/export -o lead_assessment.xlsx

# Analyze multiple leads from SOQL query (via web UI at /ui)
# Supports complex queries with JOINs and UNIONs that return Lead IDs
# POST /leads/analyze-query - Bulk ZoomInfo enrichment analysis
# POST /leads/analyze-query/export - Export bulk analysis to Excel
```

## Documentation

📚 **Full documentation is available in the [`docs/`](docs/) folder:**

- **[API Documentation](docs/README.md)** - Complete setup guide, API reference, and examples
- **[Project Requirements](docs/project_breakdown.md)** - Detailed project overview and specifications
- **[Lead Data Interpretation](docs/lead_data_interpretation.md)** - AI scoring methodology and field definitions

## Project Structure

```
ZI_Enrichment_Assessment/
├── app.py                           # Main Flask application
├── docs/                           # 📚 Documentation
│   ├── README.md                   # Complete API documentation
│   ├── project_breakdown.md        # Project requirements
│   └── lead_data_interpretation.md # AI scoring methodology
├── config/                         # ⚙️  Configuration files
│   ├── config.py                   # Application configuration
│   ├── requirements.txt            # Python dependencies
│   └── env.example                 # Environment template
├── services/                       # 🔧 Business logic services
│   ├── salesforce_service.py       # Salesforce API integration
│   ├── openai_service.py           # OpenAI confidence scoring
│   └── excel_service.py            # Excel export functionality
└── routes/                         # 🛣️  API route definitions
    └── api_routes.py               # All API endpoints
```

---

**For complete setup instructions and API documentation, see [docs/README.md](docs/README.md)** 