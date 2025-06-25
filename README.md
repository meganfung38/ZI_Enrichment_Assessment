# ZoomInfo Quality Assessment API

A Flask API for assessing the quality and reliability of ZoomInfo-enriched lead data.

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

## Latest Updates

✅ **Dependencies Updated (January 2025)**
- **Flask**: Updated to v3.1.1 (latest stable) - improved performance and security
- **simple-salesforce**: Updated to v1.12.6 - enhanced JWT support, Bulk2.0 features, OAuth2 endpoints
- **python-dotenv**: Updated to v1.0.1 - latest bug fixes
- **OpenAI**: Updated to v1.90.0+ - latest API features and improvements

## Documentation

📚 **Full documentation is available in the [`docs/`](docs/) folder:**

- **[API Documentation](docs/README.md)** - Complete setup guide, API reference, and examples
- **[Project Requirements](docs/project_breakdown.md)** - Detailed project overview and specifications

## Features

🔍 **Lead Quality Analysis**
- Automated quality flags for ZoomInfo-enriched data
- `not_in_TAM` detection for large companies missing enrichment
- `suspicious_enrichment` detection for potentially incorrect data

🚀 **Modern Architecture**
- Flask 3.1.1 with application factory pattern
- Modular service layer design
- OpenAI integration for confidence scoring
- Comprehensive error handling and logging

## Project Structure

```
ZI_Enrichment_Assessment/
├── app.py                    # Main Flask application
├── docs/                     # 📚 Documentation
├── config/                   # ⚙️  Configuration files
├── services/                 # 🔧 Business logic services
└── routes/                   # 🛣️  API route definitions
```

---

**For complete setup instructions and API documentation, see [docs/README.md](docs/README.md)** 