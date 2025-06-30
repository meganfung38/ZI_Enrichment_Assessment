from flask import Blueprint, jsonify, request, send_file
from services.salesforce_service import SalesforceService
from services.openai_service import test_openai_connection, test_openai_completion, get_openai_config, generate_lead_confidence_assessment
from services.excel_service import ExcelService
from config.config import Config

# Create blueprint for API routes
api_bp = Blueprint('api', __name__)

# Initialize services
sf_service = SalesforceService()
excel_service = ExcelService()

@api_bp.route('/')
def index():
    """API root endpoint"""
    return jsonify({
        "message": "ZoomInfo Quality Assessment API",
        "version": "1.0.0",
        "status": "running",
        "web_ui": "/ui",
        "endpoints": {
            "health": "/health",
            "debug_config": "/debug-config",
            "salesforce_test": "/test-salesforce-connection",
            "openai_test": "/test-openai-connection",
            "openai_completion": "/test-openai-completion",
            "get_lead": "/lead/<lead_id>",
            "query_leads": "/leads",
            "analyze_query": "/leads/analyze-query",
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

@api_bp.route('/leads', methods=['GET'])
def query_leads():
    """Query leads with optional filters"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 100, type=int)
        where_clause = request.args.get('where')
        
        # Query leads using the service
        result, message = sf_service.query_leads(where_clause, limit)
        
        if result is None:
            return jsonify({
                'status': 'error',
                'message': message
            }), 500
        
        return jsonify({
            'status': 'success',
            'message': message,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error querying leads: {str(e)}'
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

@api_bp.route('/leads/analyze-query', methods=['POST'])
def analyze_leads_query():
    """Analyze leads from a custom SOQL query"""
    try:
        # Get JSON data from request
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Request must be JSON'
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        if 'soql_query' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: soql_query'
            }), 400
        
        soql_query = data['soql_query']
        max_analyze = data.get('max_analyze', 100)
        include_ai_assessment = data.get('include_ai_assessment', True)
        
        # Validate max_analyze
        if not isinstance(max_analyze, int) or max_analyze < 1 or max_analyze > 500:
            return jsonify({
                'status': 'error',
                'message': 'max_analyze must be an integer between 1 and 500'
            }), 400
        
        # Validate include_ai_assessment
        if not isinstance(include_ai_assessment, bool):
            return jsonify({
                'status': 'error',
                'message': 'include_ai_assessment must be a boolean'
            }), 400
        
        # Execute the analysis (always include full details)
        result, message = sf_service.analyze_leads_from_query(
            soql_query, max_analyze, include_ai_assessment
        )
        
        if result is None:
            return jsonify({
                'status': 'error',
                'message': message
            }), 400
        
        return jsonify({
            'status': 'success',
            'message': message,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error analyzing leads from query: {str(e)}'
        }), 500

@api_bp.route('/leads/preview-query', methods=['POST'])
def preview_leads_query():
    """Preview SOQL query results - show Lead IDs before full analysis"""
    try:
        # Get JSON data from request
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Request must be JSON'
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        if 'soql_query' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: soql_query'
            }), 400
        
        soql_query = data['soql_query']
        preview_limit = data.get('preview_limit', 100)
        
        # Validate preview_limit
        if not isinstance(preview_limit, int) or preview_limit < 1 or preview_limit > 1000:
            return jsonify({
                'status': 'error',
                'message': 'preview_limit must be an integer between 1 and 1000'
            }), 400
        
        # Execute the preview
        result, message = sf_service.preview_soql_query(soql_query, preview_limit)
        
        if result is None:
            return jsonify({
                'status': 'error',
                'message': message
            }), 400
        
        return jsonify({
            'status': 'success',
            'message': message,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error previewing SOQL query: {str(e)}'
        }), 500

@api_bp.route('/leads/analyze-query/export', methods=['POST'])
def export_analyze_query_excel():
    """Export analyze-query results to Excel file"""
    try:
        # Get JSON data from request
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Request must be JSON'
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        if 'soql_query' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: soql_query'
            }), 400
        
        soql_query = data['soql_query']
        max_analyze = data.get('max_analyze', 100)
        include_ai_assessment = data.get('include_ai_assessment', True)
        
        # Validate parameters (same as regular analyze-query endpoint)
        if not isinstance(max_analyze, int) or max_analyze < 1 or max_analyze > 500:
            return jsonify({
                'status': 'error',
                'message': 'max_analyze must be an integer between 1 and 500'
            }), 400
        
        if not isinstance(include_ai_assessment, bool):
            return jsonify({
                'status': 'error',
                'message': 'include_ai_assessment must be a boolean'
            }), 400
        
        # Execute the analysis (same as regular endpoint)
        result, message = sf_service.analyze_leads_from_query(
            soql_query, max_analyze, include_ai_assessment
        )
        
        if result is None:
            return jsonify({
                'status': 'error',
                'message': message
            }), 400
        
        # Generate Excel file
        try:
            file_buffer, filename = excel_service.create_lead_analysis_excel(
                analysis_data=result['leads'],
                summary_data=result['summary'],
                query_info=result['query_info'],
                filename_prefix="lead_query_analysis"
            )
            
            return send_file(
                file_buffer,
                as_attachment=True,
                download_name=filename,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
        except Exception as excel_error:
            return jsonify({
                'status': 'error',
                'message': f'Error generating Excel file: {str(excel_error)}'
            }), 500
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error exporting analyze-query results: {str(e)}'
        }), 500

@api_bp.route('/lead/<lead_id>/confidence/export')
def export_lead_confidence_excel(lead_id):
    """Export single lead confidence assessment to Excel file"""
    try:
        # First, get the lead data with confidence assessment (same as regular endpoint)
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
                "message": f"Failed to generate confidence assessment: {ai_message}"
            }), 500
        
        # Add assessment to lead data
        lead_data['confidence_assessment'] = assessment
        lead_data['ai_assessment_status'] = 'success'
        
        # Generate Excel file
        try:
            file_buffer, filename = excel_service.create_single_lead_excel(
                lead_data=lead_data,
                filename_prefix=f"lead_confidence_{lead_id}"
            )
            
            return send_file(
                file_buffer,
                as_attachment=True,
                download_name=filename,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
        except Exception as excel_error:
            return jsonify({
                'status': 'error',
                'message': f'Error generating Excel file: {str(excel_error)}'
            }), 500
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error exporting lead confidence assessment: {str(e)}'
        }), 500