from flask import Flask, jsonify
from simple_salesforce import Salesforce
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

class SalesforceService:
    def __init__(self):
        self.sf = None
    
    def connect(self):
        """Establish connection to Salesforce"""
        try:
            # Get credentials from environment variables
            username = os.getenv('SF_USERNAME')
            password = os.getenv('SF_PASSWORD')
            security_token = os.getenv('SF_SECURITY_TOKEN')
            domain = os.getenv('SF_DOMAIN', 'login')  # 'login' for production, 'test' for sandbox
            
            if not all([username, password, security_token]):
                raise ValueError("Missing required Salesforce credentials in environment variables")
            
            # Create Salesforce connection
            self.sf = Salesforce(
                username=username,
                password=password,
                security_token=security_token,
                domain=domain
            )
            
            return True
        except Exception as e:
            print(f"Failed to connect to Salesforce: {str(e)}")
            return False
    
    def test_connection(self):
        """Test if connection is working by running a simple query"""
        try:
            if not self.sf:
                if not self.connect():
                    return False, "Failed to establish connection"
            
            # Simple test - query 5 Lead IDs
            query_result = self.sf.query("SELECT Id FROM Lead LIMIT 5")
            
            # If we get here, connection is working and we can query data
            record_count = len(query_result['records'])
            return True, f"Connection successful - Retrieved {record_count} Lead records"
            
        except Exception as e:
            return False, f"Connection failed: {str(e)}"

# Initialize Salesforce service
sf_service = SalesforceService()

@app.route('/')
def index():
    return jsonify({
        "message": "ZoomInfo Quality Assessment API",
        "status": "running"
    })

@app.route('/test-salesforce-connection')
def test_salesforce_connection():
    """Test endpoint to verify Salesforce connection"""
    try:
        is_connected, message = sf_service.test_connection()
        
        if is_connected:
            # Get some basic info if connection is successful
            org_info = {
                "instance_url": sf_service.sf.sf_instance,
                "session_id": "Connected" if sf_service.sf.session_id else "Not Connected",
                "api_version": sf_service.sf.sf_version
            }
            
            return jsonify({
                "status": "success",
                "message": message,
                "connection_details": org_info
            })
        else:
            return jsonify({
                "status": "error",
                "message": message
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 