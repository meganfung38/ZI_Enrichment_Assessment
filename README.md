# ZoomInfo Quality Assessment API

A Flask API for assessing the quality and reliability of ZoomInfo-enriched lead data.

## Quick Start

```bash
# Install dependencies
pip install -r config/requirements.txt

# Set up environment
cp config/env.example .env
# Edit .env with your Salesforce credentials

# Run the application
python app.py
```

## Documentation

📚 **Full documentation is available in the [`docs/`](docs/) folder:**

- **[API Documentation](docs/README.md)** - Complete setup guide, API reference, and examples
- **[Project Requirements](docs/project_breakdown.md)** - Detailed project overview and specifications

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