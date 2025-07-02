// Global variables to store analysis results for export
let previewData = null;
let analysisResults = null;
let singleLeadResults = null;

// Initialize event handlers when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeEventHandlers();
});

function initializeEventHandlers() {
    // Preview Query Button Handler
    document.getElementById('previewBtn').addEventListener('click', handlePreviewQuery);
    
    // SOQL Query Form Handler (Full Analysis)
    document.getElementById('queryForm').addEventListener('submit', handleQueryFormSubmit);
    
    // Export Button Handler for Analyze Query
    document.getElementById('exportBtn').addEventListener('click', handleExportAnalysis);
    
    // Lead Confidence Form Handler
    document.getElementById('confidenceForm').addEventListener('submit', handleConfidenceFormSubmit);
    
    // Export Button Handler for Lead Confidence
    document.getElementById('exportConfidenceBtn').addEventListener('click', handleExportConfidence);
    
    // Clear stored results when inputs change
    document.getElementById('leadId').addEventListener('input', function() {
        singleLeadResults = null;
        document.getElementById('exportConfidenceBtn').disabled = true;
    });
    
    document.getElementById('soqlQuery').addEventListener('input', function() {
        analysisResults = null;
        document.getElementById('exportBtn').disabled = true;
    });
    
    document.getElementById('maxAnalyze').addEventListener('input', function() {
        analysisResults = null;
        document.getElementById('exportBtn').disabled = true;
    });
}

async function handlePreviewQuery(e) {
    e.preventDefault();
    
    const responseDiv = document.getElementById('queryResponse');
    const button = e.target;
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    // Get form values
    const whereClause = document.getElementById('soqlQuery').value.trim();
    const previewLimit = parseInt(document.getElementById('previewLimit').value);
    
    // Validate inputs
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
    analyzeBtn.disabled = true;
    document.getElementById('exportBtn').disabled = true;
    responseDiv.innerHTML = 'Previewing query results...';
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
            responseDiv.innerHTML = `✅ Preview Results:\n\n${JSON.stringify(data, null, 2)}\n\n✅ Query successful! You can now proceed to analyze the leads.`;
            responseDiv.className = 'response success';
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = `Get Confidence Assessment (${Math.min(previewData.total_found, parseInt(document.getElementById('maxAnalyze').value))} leads)`;
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
}

async function handleQueryFormSubmit(e) {
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
    document.getElementById('exportBtn').disabled = true;
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
            analysisResults = data;
            responseDiv.innerHTML = JSON.stringify(data, null, 2);
            responseDiv.className = 'response success';
            document.getElementById('exportBtn').disabled = false;
        } else {
            analysisResults = null;
            responseDiv.innerHTML = JSON.stringify(data, null, 2);
            responseDiv.className = 'response error';
            document.getElementById('exportBtn').disabled = true;
        }
    } catch (error) {
        responseDiv.innerHTML = `Error: ${error.message}`;
        responseDiv.className = 'response error';
        document.getElementById('exportBtn').disabled = true;
    } finally {
        button.disabled = false;
        button.textContent = `Get Confidence Assessment (${Math.min(previewData.total_found, maxAnalyze)} leads)`;
    }
}

async function handleExportAnalysis(e) {
    e.preventDefault();
    
    if (!analysisResults) {
        alert('Please run the analysis first before exporting.');
        return;
    }
    
    const button = e.target;
    
    // Show loading state
    button.disabled = true;
    button.textContent = 'Exporting...';
    
    try {
        const response = await fetch('/leads/export-analysis-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                analysis_data: analysisResults.data
            })
        });
        
        if (response.ok) {
            await downloadFile(response, 'lead_query_analysis.xlsx');
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
}

async function handleConfidenceFormSubmit(e) {
    e.preventDefault();
    
    const responseDiv = document.getElementById('confidenceResponse');
    const button = e.target.querySelector('button');
    const leadId = document.getElementById('leadId').value.trim();
    
    // Clear previous results when analyzing a new lead
    singleLeadResults = null;
    document.getElementById('exportConfidenceBtn').disabled = true;
    
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
            singleLeadResults = data;
            responseDiv.innerHTML = JSON.stringify(data, null, 2);
            responseDiv.className = 'response success';
            document.getElementById('exportConfidenceBtn').disabled = false;
        } else {
            singleLeadResults = null;
            responseDiv.innerHTML = JSON.stringify(data, null, 2);
            responseDiv.className = 'response error';
            document.getElementById('exportConfidenceBtn').disabled = true;
        }
    } catch (error) {
        responseDiv.innerHTML = `Error: ${error.message}`;
        responseDiv.className = 'response error';
    } finally {
        button.disabled = false;
        button.textContent = 'Get Confidence Assessment';
    }
}

async function handleExportConfidence(e) {
    e.preventDefault();
    
    if (!singleLeadResults) {
        alert('Please run the confidence analysis first before exporting.');
        return;
    }
    
    const button = e.target;
    
    // Show loading state
    button.disabled = true;
    button.textContent = 'Exporting...';
    
    try {
        const response = await fetch('/leads/export-single-lead-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                lead_data: singleLeadResults
            })
        });
        
        if (response.ok) {
            const leadId = singleLeadResults.lead_data?.Id || 'unknown';
            await downloadFile(response, `lead_confidence_${leadId}.xlsx`);
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
}

async function downloadFile(response, defaultFilename) {
    // Handle file download
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    
    // Extract filename from response headers or use default
    const contentDisposition = response.headers.get('Content-Disposition');
    let filename = defaultFilename;
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
} 