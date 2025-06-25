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

### Example Response

```json
{
  "status": "success",
  "message": "Lead retrieved successfully with analysis",
  "lead": {
    "Id": "00Q5e00000ABC123",
    "First_Channel__c": "Website",
    "ZI_Company_Name__c": "Example Corp",
    "Email": "john.doe@gmail.com",
    "Website": null,
    "ZI_Employees__c": 250,
    "LS_Enrichment_Status__c": "SUCCESS",
    "not_in_TAM": false,
    "suspicious_enrichment": true
  }
}
```

In this example:
- `not_in_TAM: false` - Company name is populated, so it's in TAM base
- `suspicious_enrichment: true` - Gmail email + no website + company name + >100 employees suggests potential enrichment issue

## Lead Fields Returned

The API returns the following ZoomInfo-related fields:

### **Core Lead Data**
- `Id` - Salesforce Lead ID
- `First_Channel__c` - First channel information
- `ZI_Company_Name__c` - ZoomInfo company name
- `Email` - Lead email address
- `Website` - Company website
- `ZI_Employees__c` - ZoomInfo employee count
- `LS_Enrichment_Status__c` - Lead enrichment status

### **Quality Assessment Flags**
- `not_in_TAM` - Boolean indicating if lead should be in RC TAM base
  - `true` when `ZI_Employees__c > 100` but `ZI_Company_Name__c` is null
  - Suggests incomplete enrichment for companies that should be in Total Addressable Market
- `suspicious_enrichment` - Boolean indicating potentially incorrect enrichment
  - `true` when email has free domain (gmail, yahoo, etc.) + no website + company name populated + >100 employees
  - Suggests enrichment may have incorrectly associated personal email with large company

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