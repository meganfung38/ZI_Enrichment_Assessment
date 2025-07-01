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

✅ **Enhanced AI Assessment & Validation**
- **Intelligent URL Handling**: Prevents redundant corrections/inferences for URL formatting differences
- **Advanced Cross-Validation**: Enhanced rules prevent AI from making meaningless formatting corrections
- **Mandatory Caution Requirements**: Confidence scores < 100 must include specific caution/issue explanations
- **Smart Domain Extraction**: AI extracts core domains before making any website-related inferences

✅ **Enhanced Data Collection & Validation**
- **Expanded Lead Data**: Now collects 10 core fields including segment info, company size ranges, and dual website sources
- **Advanced Cross-Validation**: Compare ZoomInfo data against internal estimates and segment classifications
- **Website Consistency Checks**: Validate alignment between lead-provided and ZoomInfo-enriched website data
- **Company Size Agreement**: Cross-validate ZoomInfo employee counts with internal size range estimates

✅ **Flexible SOQL Query System**
- **Complex Query Support**: JOINs, UNIONs, subqueries allowed if they return Lead IDs
- **Result-Focused Validation**: Security-first approach while enabling sophisticated lead filtering
- **Enterprise-Grade Flexibility**: Support for multi-object queries and complex business logic
- **Smart Query Building**: Handles empty queries, LIMIT conflicts, and WHERE clauses intelligently

✅ **Professional Excel Export System**
- **Comprehensive Reports**: All lead fields, confidence assessments, explanations, corrections, and inferences
- **Visual Formatting**: Color-coded confidence scores, bordered tables, proper column sizing
- **Summary Statistics**: Analysis overview including total leads, issue percentages, average confidence
- **Timestamped Files**: Automatic naming with date/time for easy organization
- **Sample Export**: See [`docs/sample_excel.xlsx`](docs/sample_excel.xlsx) for example output format

✅ **AI-Powered ZoomInfo Enrichment Assessment**
- **Enhanced Validation**: 12+ data points for comprehensive enrichment quality assessment
- **Smart Explanations**: Clear bullet-point rationale with emoji indicators (✅ ⚠️ ❌)
- **Intelligent Corrections**: High-confidence fixes for conflicting ZoomInfo data (no URL formatting changes)
- **Contextual Inferences**: Lower-confidence guesses for missing enrichment data (prevents redundant URL variations)
- **Segment-Aware Analysis**: Use sales segment and channel context for better assessment

✅ **Performance & User Experience**
- **10x Faster Execution**: Optimized batch processing and query optimization
- **Two-Step Workflow**: Preview queries before running full analysis for better control
- **Smart UI Controls**: Export buttons only enabled after successful analysis completion
- **Web Interface**: Interactive testing and analysis with real-time feedback

✅ **Dependencies & Architecture**
- **Flask 3.1.1**: Latest stable with improved performance and security
- **simple-salesforce 1.12.6**: Enhanced JWT support, Bulk2.0 features, OAuth2 endpoints
- **OpenAI 1.90.0+**: Latest API features and improved response handling
- **openpyxl 3.1.5**: Professional Excel file generation and formatting
- **Modular Design**: Clean separation of concerns with service layer architecture

## Key Features

📊 **Comprehensive Data Collection**
- **10 Core Lead Fields**: Email, channel, segment, size ranges, dual website sources, ZoomInfo enrichment data
- **Cross-Validation Ready**: Compare ZoomInfo data against internal estimates and classifications
- **Business Context**: Sales segment and channel information for enhanced assessment
- **Dual Website Sources**: Compare lead-provided vs ZoomInfo-enriched website data

🧠 **AI-Powered ZoomInfo Assessment**
- **Enhanced Validation**: 10+ data points for comprehensive enrichment quality scoring (0-100)
- **Smart Explanations**: Clear bullet-point rationale with emoji indicators (✅ ⚠️ ❌)
- **Intelligent Corrections**: High-confidence fixes for conflicting ZoomInfo data (≥80% confidence)
- **Contextual Inferences**: Lower-confidence guesses for missing enrichment data (≥40% confidence)
- **Segment-Aware Analysis**: Use sales context for more accurate assessments
- **URL Intelligence**: Prevents redundant corrections like "example.com" → "https://example.com"

🔍 **Advanced Quality Detection**
- **Automated Quality Flags**: `not_in_TAM` and `suspicious_enrichment` detection
- **Website Consistency Checks**: Validate alignment between multiple website sources
- **Company Size Agreement**: Cross-validate employee counts with internal size estimates
- **Email Domain Analysis**: Corporate vs. free email validation with business logic
- **Cross-Field Validation**: Advanced consistency checks across all enrichment fields

📈 **Flexible SOQL Query System**
- **Enterprise-Grade Queries**: JOINs, UNIONs, subqueries allowed if they return Lead IDs
- **Result-Focused Security**: Smart validation ensures only Lead IDs are returned
- **Complex Business Logic**: Support for sophisticated lead filtering and segmentation
- **Query Intelligence**: Handles empty queries, LIMIT conflicts, and WHERE clauses automatically

📊 **Professional Excel Export**
- **Comprehensive Reports**: All 10 core fields plus 7 assessment outputs (confidence scores, explanations, corrections, inferences)
- **Visual Excellence**: Color-coded confidence scores, bordered tables, professional formatting
- **Summary Analytics**: Total leads, issue percentages, average confidence, trend analysis
- **Organized Output**: Timestamped files with clear structure for business reporting
- **Sample Available**: View [`docs/sample_excel.xlsx`](docs/sample_excel.xlsx) for example export format

⚡ **Performance & Experience**
- **10x Faster Execution**: Optimized batch processing and intelligent query optimization
- **Two-Step Workflow**: Preview queries before analysis for better control and validation
- **Smart UI Controls**: Context-aware interface with proper state management
- **Interactive Web Interface**: Real-time feedback and comprehensive testing capabilities

🚀 **Enterprise Architecture**
- **Flask 3.1.1**: Latest stable framework with enhanced security and performance
- **Modular Design**: Clean service layer separation with extensible architecture
- **OpenAI Integration**: Latest API features (v1.90.0+) for advanced AI-powered analysis
- **Professional Reporting**: openpyxl 3.1.5 integration for business-grade Excel output
- **Salesforce Optimized**: Enhanced simple-salesforce 1.12.6 with improved query capabilities

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

## Sample Excel Export

The API generates professional Excel reports with comprehensive ZoomInfo enrichment analysis. **View the sample export format at [`docs/sample_excel.xlsx`](docs/sample_excel.xlsx)** which includes:

- **17 Total Columns**: 10 core lead fields + 7 AI assessment outputs
- **Color-Coded Confidence**: Traffic light system (Red: 0-59, Yellow: 60-79, Green: 80-100)
- **Professional Formatting**: Bordered tables, proper column sizing, business-ready appearance
- **Summary Statistics**: Total leads analyzed, issue percentages, average confidence scores
- **Comprehensive Data**: All lead data, AI explanations, corrections, and inferences in one report

## Documentation

📚 **Full documentation is available in the [`docs/`](docs/) folder:**

- **[API Documentation](docs/README.md)** - Complete setup guide, API reference, and examples
- **[Project Requirements](docs/project_breakdown.md)** - Detailed project overview and specifications
- **[Lead Data Interpretation](docs/lead_data_interpretation.md)** - AI scoring methodology and field definitions
- **[Sample Excel Export](docs/sample_excel.xlsx)** - Example of professional Excel report output

## Project Structure

```
ZI_Enrichment_Assessment/
├── app.py                           # 🚀 Main Flask application with UI
├── docs/                           # 📚 Comprehensive Documentation
│   ├── README.md                   # Complete API guide & examples
│   ├── project_breakdown.md        # Project requirements & specifications
│   └── lead_data_interpretation.md # AI scoring methodology & field definitions
├── config/                         # ⚙️  Configuration Management
│   ├── config.py                   # Environment-based configuration
│   ├── requirements.txt            # Python dependencies (Flask 3.1.1, OpenAI 1.90.0+)
│   └── env.example                 # Environment template with all required vars
├── services/                       # 🔧 Core Business Logic Services
│   ├── salesforce_service.py       # 📊 Enhanced Salesforce integration (12+ fields)
│   ├── openai_service.py           # 🧠 AI-powered confidence assessment
│   └── excel_service.py            # 📈 Professional Excel export & formatting
└── routes/                         # 🛣️  API Route Definitions
    └── api_routes.py               # All endpoints with comprehensive validation
```

### **Key Components:**

**🚀 Flask Application (`app.py`)**
- Application factory pattern with blueprints
- Interactive web UI for testing and analysis
- Environment-based configuration management
- Unicode-safe JSON responses

**📊 Salesforce Service (`services/salesforce_service.py`)**
- **Enhanced Data Collection**: 10 core fields including segment, size ranges, dual websites
- **Flexible SOQL Support**: JOINs, UNIONs, complex queries with security validation
- **Optimized Performance**: Batch processing and intelligent query building
- **Quality Flag Analysis**: Automated `not_in_TAM` and `suspicious_enrichment` detection

**🧠 OpenAI Service (`services/openai_service.py`)**
- **Advanced Prompt Engineering**: Comprehensive field validation and cross-checking
- **Intelligent Assessment**: Confidence scoring with corrections and inferences
- **Context-Aware Analysis**: Sales segment and channel information integration
- **Structured Output**: Consistent JSON responses with emoji-coded explanations

**📈 Excel Service (`services/excel_service.py`)**
- **Professional Formatting**: Color-coded confidence scores and bordered tables
- **Comprehensive Reports**: All 10 core fields plus 7 assessment outputs
- **Summary Analytics**: Lead counts, issue percentages, confidence averages
- **Business-Ready Output**: Timestamped files with organized structure

**🛣️ API Routes (`routes/api_routes.py`)**
- **Complete Endpoint Suite**: Health checks, testing, analysis, and export
- **Security-First Validation**: SOQL query validation with result-focused approach
- **Performance Optimized**: Two-step workflow with preview capabilities
- **Export Integration**: Seamless Excel generation for all analysis types

---

**For complete setup instructions and API documentation, see [docs/README.md](docs/README.md)** 