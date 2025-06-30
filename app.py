from flask import Flask
from config.config import config
from routes.api_routes import api_bp
import os


def create_app(config_name=None):
    """Application factory pattern for creating Flask app"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Configure JSON to not escape Unicode characters (for proper emoji display)
    # Handle Flask 3.x compatibility
    try:
        app.json.ensure_ascii = False
    except AttributeError:
        # For older Flask versions or if attribute doesn't exist
        pass
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    # Add UI route
    @app.route('/ui')
    def ui():
        """Serve the web UI"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZoomInfo Quality Assessment API - UI</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .endpoint {
            margin-bottom: 40px;
            padding: 25px;
            border: 1px solid #ddd;
            border-radius: 6px;
            background-color: #fafafa;
        }
        .endpoint h2 {
            color: #2c5aa0;
            margin-top: 0;
            margin-bottom: 10px;
        }
        .endpoint-description {
            color: #666;
            margin-bottom: 20px;
            font-style: italic;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        input[type="text"], textarea {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            box-sizing: border-box;
        }
        textarea {
            height: 120px;
            resize: vertical;
        }
        .form-row {
            display: flex;
            gap: 20px;
            margin-bottom: 15px;
        }
        .form-row > div {
            flex: 1;
        }
        button {
            background-color: #2c5aa0;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 10px;
        }
        button:hover {
            background-color: #1e3d6f;
        }
        button:disabled {
            background-color: #ccc !important;
            color: #666 !important;
            cursor: not-allowed;
            opacity: 0.6;
        }
        .response {
            margin-top: 20px;
            padding: 15px;
            border-radius: 4px;
            white-space: pre-wrap;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 12px;
            max-height: 400px;
            overflow-y: auto;
        }
        .response.success {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        .response.error {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        .loading {
            color: #666;
            font-style: italic;
        }
        .method-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
            margin-right: 10px;
        }
        .post {
            background-color: #28a745;
            color: white;
        }
        .get {
            background-color: #007bff;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 ZoomInfo Quality Assessment API</h1>
        <div style="text-align: center; margin-bottom: 40px; padding: 20px; background-color: #f8f9fa; border-radius: 6px; border-left: 4px solid #2c5aa0;">
            <p style="font-size: 18px; color: #333; margin: 0;">
                <strong>Assess the quality and reliability of ZoomInfo-enriched lead data using AI-powered confidence scoring.</strong>
            </p>
            <p style="color: #666; margin: 10px 0 0 0;">
                Identify enrichment gaps, suspicious data patterns, and get actionable insights to improve your lead quality.
            </p>
        </div>
        
        <!-- SOQL Query Analysis Endpoint -->
        <div class="endpoint">
            <h2><span class="method-badge post">POST</span>/leads/analyze-query</h2>
            <div class="endpoint-description">
                Analyze ZoomInfo enrichment quality across multiple leads from a custom SOQL query. Get AI confidence scores and explanations for data reliability issues.
            </div>
            
            <form id="queryForm">
                <label for="soqlQuery">SOQL Query (optional - leave blank for random leads):</label>
<textarea id="soqlQuery" placeholder="Valid examples:&#10;• Leave blank for random leads&#10;• WHERE Email LIKE '%@gmail.com'&#10;• LIMIT 50&#10;• SELECT Id FROM Lead WHERE Company = 'Acme'&#10;• SELECT Lead.Id FROM Lead JOIN Account ON...&#10;• SELECT Id FROM Lead WHERE... UNION SELECT Id FROM Lead WHERE...&#10;&#10;✅ JOINs & UNIONs allowed if they return Lead IDs only"></textarea>
                
                <div class="form-row">
                    <div>
                        <label for="previewLimit">Preview Limit (1-1000):</label>
                        <input type="text" id="previewLimit" value="100">
                    </div>
                    <div>
                        <label for="maxAnalyze">Max Leads to Analyze (1-500):</label>
                        <input type="text" id="maxAnalyze" value="10">
                    </div>
                </div>
                
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <button type="button" id="previewBtn">1. Preview Query</button>
                    <button type="submit" id="analyzeBtn" disabled>Get Confidence Assessment</button>
                    <button type="button" id="exportBtn" disabled style="background-color: #28a745;">📊 Export to Excel</button>
                </div>
            </form>
            
            <div id="queryResponse" class="response" style="display: none;"></div>
        </div>
        
        <!-- Lead Confidence Assessment Endpoint -->
        <div class="endpoint">
            <h2><span class="method-badge get">GET</span>/lead/{lead_id}/confidence</h2>
            <div class="endpoint-description">
                Get AI-powered confidence assessment for a single lead's ZoomInfo enrichment data. Provides detailed scoring and natural language explanations of enrichment reliability.
            </div>
            
            <form id="confidenceForm">
                <label for="leadId">Salesforce Lead ID:</label>
                <input type="text" id="leadId" placeholder="00Q5e00000ABC123" pattern="[0-9a-zA-Z]{15,18}">
                
                <div style="display: flex; gap: 10px;">
                    <button type="submit">Get Confidence Assessment</button>
                    <button type="button" id="exportConfidenceBtn" disabled style="background-color: #28a745;">📊 Export to Excel</button>
                </div>
            </form>
            
            <div id="confidenceResponse" class="response" style="display: none;"></div>
        </div>
    </div>

    <script>
        let previewData = null;
        
        // Preview Button Handler
        document.getElementById('previewBtn').addEventListener('click', async function(e) {
            e.preventDefault();
            
            const responseDiv = document.getElementById('queryResponse');
            const button = e.target;
            const analyzeBtn = document.getElementById('analyzeBtn');
            
            // Get form values
            const whereClause = document.getElementById('soqlQuery').value.trim();
            const previewLimit = parseInt(document.getElementById('previewLimit').value);
            
            // No validation needed - empty query is allowed for random leads
            
            if (isNaN(previewLimit) || previewLimit < 1 || previewLimit > 1000) {
                responseDiv.innerHTML = 'Preview limit must be a number between 1 and 1000.';
                responseDiv.className = 'response error';
                responseDiv.style.display = 'block';
                return;
            }
            
            // Build SOQL query - let backend handle empty queries
            const fullQuery = whereClause;
            
            // Show loading state
            button.disabled = true;
            button.textContent = 'Previewing...';
            responseDiv.innerHTML = 'Executing SOQL query preview...';
            responseDiv.className = 'response loading';
            responseDiv.style.display = 'block';
            
            try {
                const response = await fetch('/leads/preview-query', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        soql_query: fullQuery,
                        preview_limit: previewLimit
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    previewData = data.data;
                    responseDiv.innerHTML = `Preview Results:\\n\\n${JSON.stringify(data, null, 2)}\\n\\n✅ Query successful! You can now proceed to analyze the leads.`;
                    responseDiv.className = 'response success';
                    analyzeBtn.disabled = false;
                    analyzeBtn.textContent = `Get Confidence Assessment (${Math.min(previewData.total_found, parseInt(document.getElementById('maxAnalyze').value))} leads)`;
                    // Export button stays disabled until analysis is complete
                } else {
                    responseDiv.innerHTML = JSON.stringify(data, null, 2);
                    responseDiv.className = 'response error';
                    analyzeBtn.disabled = true;
                    document.getElementById('exportBtn').disabled = true;
                }
            } catch (error) {
                responseDiv.innerHTML = `Error: ${error.message}`;
                responseDiv.className = 'response error';
                analyzeBtn.disabled = true;
            } finally {
                button.disabled = false;
                button.textContent = '1. Preview Query';
            }
        });
        
        // SOQL Query Form Handler (Full Analysis)
        document.getElementById('queryForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            if (!previewData) {
                const responseDiv = document.getElementById('queryResponse');
                responseDiv.innerHTML = 'Please run the preview first to see which leads will be analyzed.';
                responseDiv.className = 'response error';
                responseDiv.style.display = 'block';
                return;
            }
            
            const responseDiv = document.getElementById('queryResponse');
            const button = document.getElementById('analyzeBtn');
            
            // Get form values
            const whereClause = document.getElementById('soqlQuery').value.trim();
            const maxAnalyze = parseInt(document.getElementById('maxAnalyze').value);
            
            // Validate inputs
            if (isNaN(maxAnalyze) || maxAnalyze < 1 || maxAnalyze > 500) {
                responseDiv.innerHTML = 'Max leads to analyze must be a number between 1 and 500.';
                responseDiv.className = 'response error';
                responseDiv.style.display = 'block';
                return;
            }
            
            // Build SOQL query - let backend handle empty queries
            const fullQuery = whereClause;
            
            // Show loading state
            button.disabled = true;
            button.textContent = 'Analyzing...';
            document.getElementById('exportBtn').disabled = true; // Disable export during analysis
            responseDiv.innerHTML = `Analyzing first ${maxAnalyze} leads from ${previewData.total_found} total leads found (with AI confidence scoring)...`;
            responseDiv.className = 'response loading';
            responseDiv.style.display = 'block';
            
            try {
                const response = await fetch('/leads/analyze-query', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        soql_query: fullQuery,
                        max_analyze: maxAnalyze,
                        include_ai_assessment: true
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    responseDiv.innerHTML = JSON.stringify(data, null, 2);
                    responseDiv.className = 'response success';
                    document.getElementById('exportBtn').disabled = false; // Enable the correct export button
                } else {
                    responseDiv.innerHTML = JSON.stringify(data, null, 2);
                    responseDiv.className = 'response error';
                    document.getElementById('exportBtn').disabled = true;
                }
            } catch (error) {
                responseDiv.innerHTML = `Error: ${error.message}`;
                responseDiv.className = 'response error';
                document.getElementById('exportBtn').disabled = true; // Keep export disabled on error
            } finally {
                button.disabled = false;
                button.textContent = `Get Confidence Assessment (${Math.min(previewData.total_found, maxAnalyze)} leads)`;
            }
        });
        
        // Export Button Handler for Analyze Query
        document.getElementById('exportBtn').addEventListener('click', async function(e) {
            e.preventDefault();
            
            if (!previewData) {
                alert('Please run the preview first before exporting.');
                return;
            }
            
            const button = e.target;
            const whereClause = document.getElementById('soqlQuery').value.trim();
            const maxAnalyze = parseInt(document.getElementById('maxAnalyze').value);
            
            // Build SOQL query - let backend handle empty queries
            const fullQuery = whereClause;
            
            // Show loading state
            button.disabled = true;
            button.textContent = 'Exporting...';
            
            try {
                const response = await fetch('/leads/analyze-query/export', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        soql_query: fullQuery,
                        max_analyze: maxAnalyze,
                        include_ai_assessment: true
                    })
                });
                
                if (response.ok) {
                    // Handle file download
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    
                    // Extract filename from response headers or use default
                    const contentDisposition = response.headers.get('Content-Disposition');
                    let filename = 'lead_query_analysis.xlsx';
                    if (contentDisposition) {
                        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
                        if (filenameMatch) {
                            filename = filenameMatch[1];
                        }
                    }
                    
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                    
                    alert('Excel file downloaded successfully!');
                } else {
                    const errorData = await response.json();
                    alert(`Export failed: ${errorData.message}`);
                }
            } catch (error) {
                alert(`Export error: ${error.message}`);
            } finally {
                button.disabled = false;
                button.textContent = '📊 Export to Excel';
            }
        });
        
        // Lead Confidence Form Handler
        document.getElementById('confidenceForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const responseDiv = document.getElementById('confidenceResponse');
            const button = e.target.querySelector('button');
            const leadId = document.getElementById('leadId').value.trim();
            
            // Validate Lead ID
            if (!leadId) {
                responseDiv.innerHTML = 'Please enter a Salesforce Lead ID.';
                responseDiv.className = 'response error';
                responseDiv.style.display = 'block';
                return;
            }
            
            if (leadId.length < 15 || leadId.length > 18) {
                responseDiv.innerHTML = 'Lead ID must be 15-18 characters long.';
                responseDiv.className = 'response error';
                responseDiv.style.display = 'block';
                return;
            }
            
            // Show loading state
            button.disabled = true;
            button.textContent = 'Analyzing...';
            responseDiv.innerHTML = 'Getting lead data and generating confidence assessment...';
            responseDiv.className = 'response loading';
            responseDiv.style.display = 'block';
            
            try {
                const response = await fetch(`/lead/${leadId}/confidence`);
                const data = await response.json();
                
                if (response.ok) {
                    responseDiv.innerHTML = JSON.stringify(data, null, 2);
                    responseDiv.className = 'response success';
                    // Enable export button after successful analysis
                    document.getElementById('exportConfidenceBtn').disabled = false;
                } else {
                    responseDiv.innerHTML = JSON.stringify(data, null, 2);
                    responseDiv.className = 'response error';
                    // Keep export button disabled on error
                    document.getElementById('exportConfidenceBtn').disabled = true;
                }
            } catch (error) {
                responseDiv.innerHTML = `Error: ${error.message}`;
                responseDiv.className = 'response error';
            } finally {
                button.disabled = false;
                button.textContent = 'Get Confidence Assessment';
            }
        });
        
        // Export Button Handler for Lead Confidence
        document.getElementById('exportConfidenceBtn').addEventListener('click', async function(e) {
            e.preventDefault();
            
            const leadId = document.getElementById('leadId').value.trim();
            
            if (!leadId) {
                alert('Please enter a Lead ID first.');
                return;
            }
            
            const button = e.target;
            
            // Show loading state
            button.disabled = true;
            button.textContent = 'Exporting...';
            
            try {
                const response = await fetch(`/lead/${leadId}/confidence/export`);
                
                if (response.ok) {
                    // Handle file download
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    
                    // Extract filename from response headers or use default
                    const contentDisposition = response.headers.get('Content-Disposition');
                    let filename = `lead_confidence_${leadId}.xlsx`;
                    if (contentDisposition) {
                        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
                        if (filenameMatch) {
                            filename = filenameMatch[1];
                        }
                    }
                    
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                    
                    alert('Excel file downloaded successfully!');
                } else {
                    const errorData = await response.json();
                    alert(`Export failed: ${errorData.message}`);
                }
            } catch (error) {
                alert(`Export error: ${error.message}`);
            } finally {
                button.disabled = false;
                button.textContent = '📊 Export to Excel';
            }
        });
    </script>
</body>
</html>
        '''
    
    return app


if __name__ == '__main__':
    # Create and run the app
    app = create_app()
    app.run(debug=app.config['DEBUG']) 