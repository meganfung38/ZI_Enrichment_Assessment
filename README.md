# ZoomInfo Quality Assessment API

A Flask API for assessing the quality and reliability of ZoomInfo-enriched lead data with AI-powered confidence scoring and explanations.

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

✅ **New AI-Powered Confidence Scoring**
- **OpenAI Integration**: Advanced lead quality assessment with confidence scores (0-100)
- **Smart Explanations**: Clear bullet-point rationale with emoji indicators (✅ ⚠️ ❌)
- **Data Corrections & Inferences**: AI suggests fixes and fills missing data gaps
- **Email Domain Analysis**: Automatic extraction and validation of email domains

✅ **Enhanced Lead Analysis**
- **Extended Quality Flags**: Improved detection of suspicious enrichment patterns
- **Email Domain Extraction**: New `email_domain` field for all lead queries
- **Unicode Support**: Proper emoji display in JSON responses
- **Comprehensive Data Validation**: Cross-field consistency checks

✅ **Dependencies Updated**
- **Flask**: Updated to v3.1.1 (latest stable) - improved performance and security
- **simple-salesforce**: Updated to v1.12.6 - enhanced JWT support, Bulk2.0 features, OAuth2 endpoints
- **python-dotenv**: Updated to v1.0.1 - latest bug fixes
- **OpenAI**: Updated to v1.90.0+ - latest API features and improvements

## Key Features

🧠 **AI-Powered Quality Assessment**
- Confidence scoring from 0-100 based on data completeness, consistency, and flags
- Actionable explanations with clear visual indicators
- Automated data correction suggestions
- Intelligent inference for missing fields

🔍 **Advanced Lead Analysis**
- Automated quality flags for ZoomInfo-enriched data
- `not_in_TAM` detection for large companies missing enrichment
- `suspicious_enrichment` detection for potentially incorrect data
- Email domain validation and corporate vs. free email detection

🚀 **Modern Architecture**
- Flask 3.1.1 with application factory pattern
- Modular service layer design
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

# Get AI-powered confidence assessment (NEW!)
curl http://localhost:5000/lead/00Q5e00000ABC123/confidence
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
│   └── openai_service.py           # OpenAI confidence scoring
└── routes/                         # 🛣️  API route definitions
    └── api_routes.py               # All API endpoints
```

---

**For complete setup instructions and API documentation, see [docs/README.md](docs/README.md)** 