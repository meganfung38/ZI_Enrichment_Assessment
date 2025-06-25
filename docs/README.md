# ZoomInfo Quality Assessment API

A Flask API for assessing the quality and reliability of ZoomInfo-enriched lead data.

## Project Structure

```
ZI_Enrichment_Assessment/
├── app.py                    # Main Flask application
├── docs/                     # Documentation
│   ├── README.md            # This file
│   └── project_breakdown.md # Project requirements & overview
├── config/                   # Configuration files
│   ├── config.py            # Application configuration
│   ├── requirements.txt     # Python dependencies
│   └── env.example         # Example environment file
├── .env                     # Environment variables (not in git)
├── services/                # Business logic services
│   ├── __init__.py
│   └── salesforce_service.py  # Salesforce API integration
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

### 2. Install Dependencies
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

### Salesforce Connection
- **GET** `/test-salesforce-connection` - Test Salesforce connectivity

### Lead Data
- **GET** `/lead/<lead_id>` - Get specific lead by ID
- **GET** `/leads?limit=100&where=<conditions>` - Query leads with filters

### Example Usage

```bash
# Test connection
curl http://localhost:5000/test-salesforce-connection

# Get a specific lead
curl http://localhost:5000/lead/00Q5e00000ABC123

# Query leads with filters
curl "http://localhost:5000/leads?limit=50&where=Email!=null"
```

## Lead Fields Returned

The API returns the following ZoomInfo-related fields:
- `Id` - Salesforce Lead ID
- `First_Channel__c` - First channel information
- `ZI_Company_Name__c` - ZoomInfo company name
- `Email` - Lead email address
- `Website` - Company website
- `ZI_Employees__c` - ZoomInfo employee count
- `LS_Enrichment_Status__c` - Lead enrichment status

## Development

### Project Architecture
- **Flask Application Factory Pattern**: Clean app initialization
- **Blueprints**: Organized route management
- **Service Layer**: Separation of business logic
- **Configuration Management**: Environment-based config

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