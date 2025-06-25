# Salesforce Flask API

A clean, scalable Python Flask API for connecting to Salesforce using simple-salesforce. This API provides endpoints to test connections and query Salesforce data.

## Project Structure

```
ZI_Enrichment_Assessment/
├── app.py                      # Main Flask application
├── salesforce_client.py        # Salesforce connection utility
├── requirements.txt            # Python dependencies
├── env.example                 # Environment variables example
└── README.md                   # This file
```

## Setup Instructions

### 1. Clone and Navigate to Project
```bash
cd ZI_Enrichment_Assessment
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the example environment file and fill in your Salesforce credentials:

```bash
cp env.example .env
```

Edit `.env` with your Salesforce credentials:
```env
SF_USERNAME=your-salesforce-username@example.com
SF_PASSWORD=your-salesforce-password
SF_SECURITY_TOKEN=your-security-token
SF_DOMAIN=login  # Use 'login' for production, 'test' for sandbox
SECRET_KEY=your-secret-key-here
```

### 5. Get Salesforce Security Token
If you don't have your security token:
1. Log into Salesforce
2. Go to Settings → My Personal Information → Reset My Security Token
3. Check your email for the new security token

## Running the Application

### Development Mode
```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Production Mode
```bash
gunicorn -w 4 app:app
```

## API Endpoints

### Health Check
```
GET /
```
Returns the API status.

### Test Salesforce Connection and Query
```
GET /api/test
```
Tests the Salesforce connection and executes "SELECT Id FROM Lead LIMIT 5" to verify both connection and querying capability.

**Response (Success):**
```json
{
  "success": true,
  "connected": true,
  "message": "Connection successful and query executed",
  "query": "SELECT Id FROM Lead LIMIT 5",
  "total_size": 5,
  "records": [
    {"Id": "00Q1234567890ABC"},
    {"Id": "00Q1234567890DEF"}
  ]
}
```

**Response (Error):**
```json
{
  "success": false,
  "connected": false,
  "message": "Connection or query failed: [error details]",
  "query": "SELECT Id FROM Lead LIMIT 5",
  "total_size": 0,
  "records": []
}
```

## Testing the API

### Using curl

**Test connection and query:**
```bash
curl http://localhost:5000/api/test
```

### Using Python requests
```python
import requests

# Test connection and query
response = requests.get('http://localhost:5000/api/test')
print(response.json())
```

## Security Features

- Environment-based configuration management
- Input validation for SOQL queries
- Only SELECT queries allowed for security
- Query result limits to prevent performance issues
- Comprehensive error handling and logging

## Error Handling

The API provides detailed error messages for common issues:
- Missing environment variables
- Invalid Salesforce credentials
- Malformed SOQL queries
- Connection timeouts
- Invalid request formats

## Logging

The application uses Python's built-in logging module with INFO level by default. Logs include:
- Connection status
- Query execution details
- Error messages with context
- Request/response information

## Troubleshooting

### Common Issues

1. **"Import could not be resolved" errors:** Install dependencies with `pip install -r requirements.txt`

2. **Connection failures:** Verify your Salesforce credentials and security token

3. **"INVALID_LOGIN" error:** Check username, password, and security token combination

4. **Sandbox connection issues:** Set `SF_DOMAIN=test` for sandbox environments

### Salesforce Connection Requirements

- Valid Salesforce username and password
- Current security token (reset if needed)
- API access enabled for your user
- Correct domain setting (login/test)

## Future Enhancements

This project structure supports easy expansion:
- Add more Salesforce objects (Contacts, Opportunities, etc.)
- Implement authentication/authorization
- Add data manipulation endpoints (INSERT, UPDATE, DELETE)
- Add request caching
- Implement batch processing
- Add API rate limiting
- Add comprehensive test suite
