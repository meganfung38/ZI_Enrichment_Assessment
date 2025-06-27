from flask import Blueprint, jsonify, request
from services.salesforce_service import SalesforceService
from services.openai_service import test_openai_connection, test_openai_completion, get_openai_config, generate_lead_confidence_assessment
from config.config import Config

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
            "debug_config": "/debug-config",
            "salesforce_test": "/test-salesforce-connection",
            "openai_test": "/test-openai-connection",
            "openai_completion": "/test-openai-completion",
            "get_lead": "/lead/<lead_id>",
            "query_leads": "/leads",
            "lead_confidence": "/lead/<lead_id>/confidence"
        }
    })

@api_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "ZoomInfo Quality Assessment API"
    })

@api_bp.route('/debug-config')
def debug_config():
    """Debug endpoint to check configuration (for development only)"""
    try:
        return jsonify({
            "salesforce": {
                "username_present": bool(Config.SF_USERNAME),
                "password_present": bool(Config.SF_PASSWORD),
                "token_present": bool(Config.SF_SECURITY_TOKEN),
                "domain": Config.SF_DOMAIN
            },
            "openai": {
                "api_key_present": bool(Config.OPENAI_API_KEY),
                "api_key_length": len(Config.OPENAI_API_KEY) if Config.OPENAI_API_KEY else 0,
                "api_key_starts_with_sk": Config.OPENAI_API_KEY.startswith('sk-') if Config.OPENAI_API_KEY else False,
                "model": Config.OPENAI_MODEL,
                "max_tokens": Config.OPENAI_MAX_TOKENS
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Configuration error: {str(e)}"
        }), 500

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

@api_bp.route('/test-openai-connection')
def test_openai_connection_endpoint():
    """Test endpoint to verify OpenAI API connection"""
    try:
        is_connected, message = test_openai_connection()
        
        if is_connected:
            config_info = get_openai_config()
            return jsonify({
                "status": "success",
                "message": message,
                "configuration": config_info
            })
        else:
            return jsonify({
                "status": "error",
                "message": message,
                "debug_info": {
                    "api_key_present": bool(Config.OPENAI_API_KEY),
                    "api_key_length": len(Config.OPENAI_API_KEY) if Config.OPENAI_API_KEY else 0,
                    "api_key_starts_with_sk": Config.OPENAI_API_KEY.strip().startswith('sk-') if Config.OPENAI_API_KEY else False
                }
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }), 500

@api_bp.route('/test-openai-completion')
def test_openai_completion_endpoint():
    """Test endpoint to verify OpenAI completion generation"""
    try:
        # Get optional prompt from query parameters
        prompt = request.args.get('prompt', 'Hello! Please respond with "OpenAI connection test successful."')
        
        completion, message = test_openai_completion(prompt)
        
        if completion:
            return jsonify({
                "status": "success",
                "message": message,
                "prompt": prompt,
                "completion": completion,
                "configuration": get_openai_config()
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

@api_bp.route('/lead/<lead_id>/confidence')
def get_lead_confidence_assessment(lead_id):
    """Get lead data with AI-powered confidence assessment and explanation"""
    try:
        # First, get the lead data with flags and email domain
        lead_data, sf_message = sf_service.get_lead_by_id(lead_id)
        
        if not lead_data:
            return jsonify({
                "status": "error",
                "message": sf_message
            }), 404
        
        # Generate confidence assessment using OpenAI
        assessment, ai_message = generate_lead_confidence_assessment(lead_data)
        
        if not assessment:
            return jsonify({
                "status": "error",
                "message": f"Failed to generate confidence assessment: {ai_message}",
                "lead_data": lead_data  # Still return the lead data even if AI fails
            }), 500
        
        # Return successful response with both lead data and assessment
        return jsonify({
            "status": "success",
            "message": "Lead confidence assessment completed successfully",
            "lead_data": lead_data,
            "confidence_assessment": assessment,
            "processing_info": {
                "salesforce_message": sf_message,
                "ai_message": ai_message
            }
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }), 500