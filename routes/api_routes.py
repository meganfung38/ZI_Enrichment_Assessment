from flask import Blueprint, jsonify, request
from services.salesforce_service import SalesforceService

# Create blueprint for API routes
api_bp = Blueprint('api', __name__)

# Initialize Salesforce service
sf_service = SalesforceService()

@api_bp.route('/')
def index():
    """API root endpoint"""
    return jsonify({
        "message": "ZoomInfo Quality Assessment API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "salesforce_test": "/test-salesforce-connection", 
            "get_lead": "/lead/<lead_id>",
            "query_leads": "/leads"
        }
    })

@api_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "ZoomInfo Quality Assessment API"
    })

@api_bp.route('/test-salesforce-connection')
def test_salesforce_connection():
    """Test endpoint to verify Salesforce connection"""
    try:
        is_connected, message = sf_service.test_connection()
        
        if is_connected:
            connection_info = sf_service.get_connection_info()
            return jsonify({
                "status": "success",
                "message": message,
                "connection_details": connection_info
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

@api_bp.route('/lead/<lead_id>')
def get_lead(lead_id):
    """Get specific Lead data by Lead ID"""
    try:
        lead_data, message = sf_service.get_lead_by_id(lead_id)
        
        if lead_data:
            return jsonify({
                "status": "success",
                "message": message,
                "lead": lead_data
            })
        else:
            return jsonify({
                "status": "error",
                "message": message
            }), 404
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }), 500

@api_bp.route('/leads')
def query_leads():
    """Query leads with optional filters"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 100, type=int)
        conditions = request.args.get('where')
        
        # Validate limit
        if limit > 1000:
            return jsonify({
                "status": "error",
                "message": "Limit cannot exceed 1000 records"
            }), 400
        
        result, message = sf_service.query_leads(conditions, limit)
        
        if result:
            return jsonify({
                "status": "success",
                "message": message,
                "data": result
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