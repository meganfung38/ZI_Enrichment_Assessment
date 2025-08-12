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
            "lead_confidence": "/lead/<lead_id>/confidence",
            "excel_analyze": "/excel/analyze",
            "excel_analyze_batch": "/excel/analyze-batch-optimized"
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
    """Analyze leads from a custom SOQL query that returns Lead IDs only"""
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

@api_bp.route('/leads/export-analysis-data', methods=['POST'])
def export_analysis_data():
    """Export pre-analyzed lead data to Excel file without re-running analysis"""
    try:
        # Get JSON data from request
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Request must be JSON'
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        if 'analysis_data' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: analysis_data'
            }), 400
        
        analysis_data = data['analysis_data']
        
        # Validate that analysis_data has the expected structure
        if not isinstance(analysis_data, dict):
            return jsonify({
                'status': 'error',
                'message': 'analysis_data must be an object'
            }), 400
        
        if 'leads' not in analysis_data or 'summary' not in analysis_data:
            return jsonify({
                'status': 'error',
                'message': 'analysis_data must contain leads and summary fields'
            }), 400
        
        # Generate Excel file using the provided analysis data
        try:
            file_buffer, filename = excel_service.create_lead_analysis_excel(
                analysis_data=analysis_data['leads'],
                summary_data=analysis_data['summary'],
                query_info=analysis_data.get('query_info'),
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
            'message': f'Error exporting analysis data: {str(e)}'
        }), 500

@api_bp.route('/leads/export-single-lead-data', methods=['POST'])
def export_single_lead_data():
    """Export pre-analyzed single lead data to Excel file without re-running analysis"""
    try:
        # Get JSON data from request
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Request must be JSON'
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        if 'lead_data' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: lead_data'
            }), 400
        
        lead_response = data['lead_data']
        
        # Validate that lead_data has the expected structure (from /lead/{id}/confidence response)
        if not isinstance(lead_response, dict):
            return jsonify({
                'status': 'error',
                'message': 'lead_data must be an object'
            }), 400
        
        if 'lead_data' not in lead_response or 'confidence_assessment' not in lead_response:
            return jsonify({
                'status': 'error',
                'message': 'lead_data must contain lead_data and confidence_assessment fields'
            }), 400
        
        # Extract the lead data and merge with confidence assessment
        lead_info = lead_response['lead_data']
        confidence_assessment = lead_response['confidence_assessment']
        
        # Merge the data (same format as bulk analysis)
        merged_lead_data = {
            **lead_info,
            'confidence_assessment': confidence_assessment,
            'ai_assessment_status': 'success'
        }
        
        # Generate Excel file using the provided single lead data
        try:
            lead_id = lead_info.get('Id', 'unknown')
            file_buffer, filename = excel_service.create_single_lead_excel(
                lead_data=merged_lead_data,
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
            'message': f'Error exporting single lead data: {str(e)}'
        }), 500

@api_bp.route('/leads/analyze-query/export', methods=['POST'])
def export_analyze_query_excel():
    """Export analyze-query results to Excel file (SOQL query must return Lead IDs only) - DEPRECATED: Use /leads/export-analysis-data instead"""
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
    """Export single lead confidence assessment to Excel file - DEPRECATED: Use /leads/export-single-lead-data instead"""
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

@api_bp.route('/excel/parse', methods=['POST'])
def parse_excel_file():
    """Parse uploaded Excel file and return sheet names and preview data"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No file selected'
            }), 400
        
        # Validate file extension
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            return jsonify({
                'status': 'error',
                'message': 'File must be an Excel file (.xlsx or .xls)'
            }), 400
        
        # Read file content
        file_content = file.read()
        
        # Parse the Excel file
        result = excel_service.parse_excel_file(file_content)
        
        if result['success']:
            return jsonify({
                'status': 'success',
                'message': 'Excel file parsed successfully',
                'data': {
                    'sheet_names': result['sheet_names'],
                    'headers': result['headers'],
                    'preview_data': result['preview_data'],
                    'total_rows': result['total_rows']
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'message': result['error']
            }), 400
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error parsing Excel file: {str(e)}'
        }), 500

@api_bp.route('/excel/validate-lead-ids', methods=['POST'])
def validate_excel_lead_ids():
    """Validate Lead IDs from Excel file upload"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No file selected'
            }), 400
        
        # Get form data
        sheet_name = request.form.get('sheet_name')
        lead_id_column = request.form.get('lead_id_column')
        
        # Validate parameters
        if not sheet_name:
            return jsonify({
                'status': 'error',
                'message': 'Sheet name is required'
            }), 400
        
        if not lead_id_column:
            return jsonify({
                'status': 'error',
                'message': 'Lead ID column is required'
            }), 400
        
        # Read file content
        file_content = file.read()
        
        # Extract Lead IDs from Excel
        extraction_result = excel_service.extract_lead_ids_from_excel(
            file_content, sheet_name, lead_id_column
        )
        
        if not extraction_result['success']:
            return jsonify({
                'status': 'error',
                'message': extraction_result['error']
            }), 400
        
        lead_ids = extraction_result['lead_ids']
        
        # 🔍 DEBUG: Log the extracted Lead IDs for debugging
        print(f"🔍 DEBUG: Extracted {len(lead_ids)} Lead IDs from Excel:")
        for i, lid in enumerate(lead_ids[:5]):  # Show first 5 for debugging
            print(f"   {i+1}. '{lid}' (length: {len(lid)}, type: {type(lid)})")
        if len(lead_ids) > 5:
            print(f"   ... and {len(lead_ids) - 5} more")
        
        if not lead_ids:
            return jsonify({
                'status': 'error',
                'message': f'No valid Lead IDs found in column "{lead_id_column}"'
            }), 400
        
        # Validate Lead IDs with Salesforce (strict validation - any invalid ID blocks analysis)
        validation_result, validation_message = sf_service.validate_lead_ids(lead_ids)
        
        if validation_result is None:
            return jsonify({
                'status': 'error',
                'message': validation_message
            }), 500
        
        # Get valid and invalid Lead IDs
        valid_lead_ids = validation_result.get('valid_lead_ids', [])
        invalid_lead_ids = validation_result.get('invalid_lead_ids', [])
        
        # Check if we have any valid Lead IDs
        if not valid_lead_ids:
            return jsonify({
                'status': 'error',
                'message': f'No valid Lead IDs found. All {len(invalid_lead_ids)} Lead IDs are invalid.',
                'invalid_lead_ids': invalid_lead_ids,
                'valid_lead_ids': [],
                'debug_info': {
                    'total_extracted': len(lead_ids),
                    'format_invalid_count': validation_result.get('format_invalid_count', 0),
                    'sf_invalid_count': validation_result.get('sf_invalid_count', 0)
                }
            }), 400
        
        # Return validation results (allowing partial validation)
        return jsonify({
            'status': 'success',
            'message': f'Validation complete: {len(valid_lead_ids)} valid, {len(invalid_lead_ids)} invalid Lead IDs',
            'data': {
                'total_lead_ids': len(lead_ids),
                'valid_lead_ids': len(valid_lead_ids),
                'invalid_lead_ids': len(invalid_lead_ids),
                'invalid_lead_ids_list': invalid_lead_ids,
                'original_data_rows': extraction_result['total_rows'],
                'validation_summary': {
                    'can_proceed': len(valid_lead_ids) > 0,
                    'all_valid': len(invalid_lead_ids) == 0,
                    'partial_validation': len(valid_lead_ids) > 0 and len(invalid_lead_ids) > 0
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error validating Lead IDs: {str(e)}'
        }), 500

@api_bp.route('/excel/analyze', methods=['POST'])
def analyze_excel_leads():
    """Analyze leads from Excel file upload"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No file selected'
            }), 400
        
        # Get form data
        sheet_name = request.form.get('sheet_name')
        lead_id_column = request.form.get('lead_id_column')
        max_analyze = int(request.form.get('max_analyze', 10000))  # High default to analyze all
        include_ai_assessment = True  # Always include AI assessment
        
        # Validate parameters
        if not sheet_name:
            return jsonify({
                'status': 'error',
                'message': 'Sheet name is required'
            }), 400
        
        if not lead_id_column:
            return jsonify({
                'status': 'error',
                'message': 'Lead ID column is required'
            }), 400
        
        # Read file content
        file_content = file.read()
        
        # Extract Lead IDs from Excel
        extraction_result = excel_service.extract_lead_ids_from_excel(
            file_content, sheet_name, lead_id_column
        )
        
        if not extraction_result['success']:
            return jsonify({
                'status': 'error',
                'message': extraction_result['error']
            }), 400
        
        # Use all Lead IDs (remove artificial limit since we want to analyze everything)
        lead_ids = extraction_result['lead_ids']
        
        if not lead_ids:
            return jsonify({
                'status': 'error',
                'message': f'No valid Lead IDs found in column "{lead_id_column}"'
            }), 400
        
        # Validate Lead IDs with Salesforce (allow partial validation)
        validation_result, validation_message = sf_service.validate_lead_ids(lead_ids)
        
        if validation_result is None:
            return jsonify({
                'status': 'error',
                'message': validation_message
            }), 500
        
        # Get valid and invalid Lead IDs
        valid_lead_ids = validation_result.get('valid_lead_ids', [])
        invalid_lead_ids = validation_result.get('invalid_lead_ids', [])
        
        # Check if we have any valid Lead IDs to analyze
        if not valid_lead_ids:
            return jsonify({
                'status': 'error',
                'message': f'No valid Lead IDs found. All {len(invalid_lead_ids)} Lead IDs are invalid.',
                'invalid_lead_ids': invalid_lead_ids
            }), 400
        
        # Proceed with analysis on valid Lead IDs only
        
        # Choose analysis method based on dataset size
        # Use batch-optimized processing for large datasets (>1000 leads)
        if len(valid_lead_ids) > 1000:
            result, message = sf_service.analyze_leads_from_ids_batch_optimized(
                valid_lead_ids, 
                include_ai_assessment=include_ai_assessment,
                batch_size=150,  # Conservative batch size for large datasets
                ai_batch_size=50  # Smaller AI batches for rate limiting
            )
        else:
            result, message = sf_service.analyze_leads_from_ids(
                valid_lead_ids, include_ai_assessment
            )
        
        if result is None:
            return jsonify({
                'status': 'error',
                'message': message
            }), 500
        
        # Store original Excel data and validation info for export
        result['excel_metadata'] = {
            'lead_id_column': lead_id_column,
            'sheet_name': sheet_name,
            'filename': file.filename,
            'has_original_data': True,  # Flag that original data is available for export
            'validation_summary': {
                'total_lead_ids': len(lead_ids),
                'valid_lead_ids': len(valid_lead_ids),
                'invalid_lead_ids': len(invalid_lead_ids),
                'invalid_lead_ids_list': invalid_lead_ids
            }
        }
        
        return jsonify({
            'status': 'success',
            'message': f"{message} (Skipped {len(invalid_lead_ids)} invalid Lead IDs)",
            'data': result,
            'validation_summary': {
                'total_lead_ids': len(lead_ids),
                'valid_lead_ids': len(valid_lead_ids),
                'invalid_lead_ids': len(invalid_lead_ids),
                'invalid_lead_ids_list': invalid_lead_ids
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error analyzing Excel leads: {str(e)}'
        }), 500

@api_bp.route('/excel/export-analysis', methods=['POST'])
def export_excel_analysis():
    """Export Excel analysis results combining original data with AI analysis"""
    try:
        # Get JSON data from request
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Request must be JSON'
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['analysis_results', 'original_data', 'lead_id_column']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        analysis_results = data['analysis_results']
        original_data = data['original_data']
        lead_id_column = data['lead_id_column']
        filename_prefix = data.get('filename_prefix', 'excel_analysis')
        
        # Validate data types
        if not isinstance(analysis_results, list):
            return jsonify({
                'status': 'error',
                'message': 'analysis_results must be a list'
            }), 400
        
        if not isinstance(original_data, list):
            return jsonify({
                'status': 'error',
                'message': 'original_data must be a list'
            }), 400
        
        # Get invalid Lead IDs from the request if available
        invalid_lead_ids = data.get('invalid_lead_ids', [])
        
        # Generate Excel file with combined data
        result = excel_service.create_excel_with_analysis(
            original_data, analysis_results, lead_id_column, filename_prefix, invalid_lead_ids
        )
        
        if not result['success']:
            return jsonify({
                'status': 'error',
                'message': result['error']
            }), 500
        
        return send_file(
            result['file_buffer'],
            as_attachment=True,
            download_name=result['filename'],
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error exporting Excel analysis: {str(e)}'
        }), 500

@api_bp.route('/excel/export-analysis-with-file', methods=['POST'])
def export_excel_analysis_with_file():
    """Export Excel analysis results by re-extracting original data from file"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No file selected'
            }), 400
        
        # Get form data
        sheet_name = request.form.get('sheet_name')
        lead_id_column = request.form.get('lead_id_column')
        analysis_results_json = request.form.get('analysis_results')
        
        if not sheet_name or not lead_id_column or not analysis_results_json:
            return jsonify({
                'status': 'error',
                'message': 'Missing required parameters'
            }), 400
        
        # Parse analysis results
        import json
        analysis_results = json.loads(analysis_results_json)
        
        # Read file content and extract original data fresh
        file_content = file.read()
        extraction_result = excel_service.extract_lead_ids_from_excel(
            file_content, sheet_name, lead_id_column
        )
        
        if not extraction_result['success']:
            return jsonify({
                'status': 'error',
                'message': extraction_result['error']
            }), 400
        
        # Get invalid Lead IDs from the request if available
        invalid_lead_ids_json = request.form.get('invalid_lead_ids', '[]')
        invalid_lead_ids = json.loads(invalid_lead_ids_json)
        
        # Generate Excel file with combined data
        result = excel_service.create_excel_with_analysis(
            extraction_result['original_data'], 
            analysis_results, 
            lead_id_column, 
            'excel_analysis',
            invalid_lead_ids
        )
        
        if not result['success']:
            return jsonify({
                'status': 'error',
                'message': result['error']
            }), 500
        
        return send_file(
            result['file_buffer'],
            as_attachment=True,
            download_name=result['filename'],
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error exporting Excel analysis with file: {str(e)}'
        }), 500

@api_bp.route('/test-lead-validation', methods=['POST'])
def test_lead_validation():
    """Test Lead ID validation with a list of Lead IDs"""
    try:
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Request must be JSON'
            }), 400
        
        data = request.get_json()
        lead_ids = data.get('lead_ids', [])
        
        if not lead_ids:
            return jsonify({
                'status': 'error',
                'message': 'No Lead IDs provided'
            }), 400
        
        # 🔍 DEBUG: Log the provided Lead IDs
        print(f"🔍 DEBUG: Testing validation for {len(lead_ids)} Lead IDs:")
        for i, lid in enumerate(lead_ids[:5]):  # Show first 5 for debugging
            print(f"   {i+1}. '{lid}' (length: {len(lid)}, type: {type(lid)})")
        if len(lead_ids) > 5:
            print(f"   ... and {len(lead_ids) - 5} more")
        
        # Validate Lead IDs with Salesforce
        validation_result, validation_message = sf_service.validate_lead_ids(lead_ids)
        
        if validation_result is None:
            return jsonify({
                'status': 'error',
                'message': validation_message
            }), 500
        
        return jsonify({
            'status': 'success',
            'message': validation_message,
            'data': {
                'total_provided': len(lead_ids),
                'valid_lead_ids': validation_result.get('valid_lead_ids', []),
                'invalid_lead_ids': validation_result.get('invalid_lead_ids', []),
                'format_invalid_count': validation_result.get('format_invalid_count', 0),
                'sf_invalid_count': validation_result.get('sf_invalid_count', 0),
                'validation_details': {
                    'total_valid': len(validation_result.get('valid_lead_ids', [])),
                    'total_invalid': len(validation_result.get('invalid_lead_ids', []))
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error testing Lead ID validation: {str(e)}'
        }), 500

@api_bp.route('/excel/analyze-batch-optimized', methods=['POST'])
def analyze_excel_leads_batch_optimized():
    """Analyze leads from Excel file upload using optimized batch processing for large datasets (50k+ leads)"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No file selected'
            }), 400
        
        # Get form data
        sheet_name = request.form.get('sheet_name')
        lead_id_column = request.form.get('lead_id_column')
        batch_size = int(request.form.get('batch_size', 200))  # Salesforce batch size
        ai_batch_size = int(request.form.get('ai_batch_size', 50))  # AI processing batch size
        include_ai_assessment = True  # Always include AI assessment
        
        # Validate parameters
        if not sheet_name:
            return jsonify({
                'status': 'error',
                'message': 'Sheet name is required'
            }), 400
        
        if not lead_id_column:
            return jsonify({
                'status': 'error',
                'message': 'Lead ID column is required'
            }), 400
        
        # Validate batch sizes
        if batch_size < 50 or batch_size > 200:
            return jsonify({
                'status': 'error',
                'message': 'batch_size must be between 50 and 200'
            }), 400
            
        if ai_batch_size < 10 or ai_batch_size > 100:
            return jsonify({
                'status': 'error',
                'message': 'ai_batch_size must be between 10 and 100'
            }), 400
        
        # Read file content
        file_content = file.read()
        
        # Extract Lead IDs from Excel
        extraction_result = excel_service.extract_lead_ids_from_excel(
            file_content, sheet_name, lead_id_column
        )
        
        if not extraction_result['success']:
            return jsonify({
                'status': 'error',
                'message': extraction_result['error']
            }), 400
        
        lead_ids = extraction_result['lead_ids']
        
        if not lead_ids:
            return jsonify({
                'status': 'error',
                'message': f'No valid Lead IDs found in column "{lead_id_column}"'
            }), 400
        

        
        # Validate Lead IDs with Salesforce (using optimized validation)
        validation_result, validation_message = sf_service.validate_lead_ids(lead_ids)
        
        if validation_result is None:
            return jsonify({
                'status': 'error',
                'message': validation_message
            }), 500
        
        # Get valid and invalid Lead IDs
        valid_lead_ids = validation_result.get('valid_lead_ids', [])
        invalid_lead_ids = validation_result.get('invalid_lead_ids', [])
        
        # Check if we have any valid Lead IDs to analyze
        if not valid_lead_ids:
            return jsonify({
                'status': 'error',
                'message': f'No valid Lead IDs found. All {len(invalid_lead_ids)} Lead IDs are invalid.',
                'invalid_lead_ids': invalid_lead_ids
            }), 400
        

        
        # Progress tracking variables (in a real implementation, this would be stored in Redis/database)
        progress_data = {
            'phase': 'starting',
            'total_leads': len(valid_lead_ids),
            'leads_processed': 0,
            'batches_completed': 0,
            'progress_percentage': 0
        }
        
        def progress_callback(update):
            """Callback function to track progress (could be enhanced with WebSocket/SSE)"""
            progress_data.update(update)
        
        # Analyze the leads using optimized batch processing
        result, message = sf_service.analyze_leads_from_ids_batch_optimized(
            valid_lead_ids, 
            include_ai_assessment=include_ai_assessment,
            batch_size=batch_size,
            ai_batch_size=ai_batch_size,
            progress_callback=progress_callback
        )
        
        if result is None:
            return jsonify({
                'status': 'error',
                'message': message
            }), 500
        
        # Store original Excel data and validation info for export
        result['excel_metadata'] = {
            'lead_id_column': lead_id_column,
            'sheet_name': sheet_name,
            'filename': file.filename,
            'has_original_data': True,
            'batch_processing_config': {
                'salesforce_batch_size': batch_size,
                'ai_batch_size': ai_batch_size,
                'total_batches': result['summary']['processing_stats']['total_batches'],
                'successful_batches': result['summary']['processing_stats']['successful_batches'],
                'failed_batches': result['summary']['processing_stats']['failed_batches']
            },
            'validation_summary': {
                'total_lead_ids': len(lead_ids),
                'valid_lead_ids': len(valid_lead_ids),
                'invalid_lead_ids': len(invalid_lead_ids),
                'invalid_lead_ids_list': invalid_lead_ids
            }
        }
        
        return jsonify({
            'status': 'success',
            'message': f"{message} (Skipped {len(invalid_lead_ids)} invalid Lead IDs)",
            'data': result,
            'validation_summary': {
                'total_lead_ids': len(lead_ids),
                'valid_lead_ids': len(valid_lead_ids),
                'invalid_lead_ids': len(invalid_lead_ids),
                'invalid_lead_ids_list': invalid_lead_ids
            },
            'performance_metrics': {
                'total_processing_time': result['summary']['processing_stats']['total_processing_time'],
                'leads_per_second': result['summary']['processing_stats']['leads_per_second'],
                'avg_batch_time': result['summary']['processing_stats']['avg_batch_time'],
                'batch_success_rate': round(
                    (result['summary']['processing_stats']['successful_batches'] / 
                     result['summary']['processing_stats']['total_batches']) * 100, 2
                ) if result['summary']['processing_stats']['total_batches'] > 0 else 0
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error in batch-optimized Excel analysis: {str(e)}'
        }), 500