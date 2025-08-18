// Global variables to store analysis results for export
let previewData = null;
let analysisResults = null;
let singleLeadResults = null;

// Global variables for Excel upload functionality
let excelFileData = null;
let excelPreviewData = null;
let excelAnalysisResults = null;

// Function to generate HTML for single lead with collapsible toggles
function generateSingleLeadHTML(lead, assessment, isEven = true) {
    const finalScore = (lead.acquisition_completeness_score && lead.enrichment_completeness_score && assessment && assessment.confidence_score) ?
        Math.round((lead.acquisition_completeness_score * 0.15) + (lead.enrichment_completeness_score * 0.15) + (assessment.confidence_score * 0.70)) : null;

    const backgroundClass = isEven ? 'lead-container-even' : 'lead-container-odd';
    
    return `<div class="lead-container ${backgroundClass}"><h3 class="lead-header">Lead Analysis: ${lead.Id || 'N/A'}</h3>
<div class="toggle-section"><button class="toggle-header" onclick="toggleSection(this)">Lead Data<span class="toggle-icon">▶</span></button><div class="toggle-content"><div class="data-row">First Name: ${lead.FirstName || 'N/A'}</div><div class="data-row">Last Name: ${lead.LastName || 'N/A'}</div><div class="data-row">Phone: ${lead.Phone || 'N/A'}</div><div class="data-row">Country: ${lead.Country || 'N/A'}</div><div class="data-row">Title: ${lead.Title || 'N/A'}</div><div class="data-row">Industry: ${lead.Industry || 'N/A'}</div><div class="data-row">Email: ${lead.Email || 'N/A'}</div><div class="data-row">First Channel: ${lead.First_Channel__c || 'N/A'}</div><div class="data-row">Segment: ${lead.SegmentName || 'N/A'}</div><div class="data-row">Company Size Range: ${lead.LS_Company_Size_Range__c || 'N/A'}</div><div class="data-row">Website: ${lead.Website || 'N/A'}</div><div class="data-row">Company: ${lead.Company || 'N/A'}</div><div class="data-row">ZI Company: ${lead.ZI_Company_Name__c || 'N/A'}</div><div class="data-row">ZI Employees: ${lead.ZI_Employees__c || 'N/A'}</div><div class="data-row">ZI Website: ${lead.ZI_Website__c || 'N/A'}</div><div class="data-row">Email Domain: ${lead.email_domain || 'N/A'}</div></div></div>
<div class="toggle-section"><button class="toggle-header" onclick="toggleSection(this)">Quality Flags<span class="toggle-icon">▶</span></button><div class="toggle-content"><div class="flag-item">Not in TAM: ${lead.not_in_TAM ? 'Yes' : 'No'}</div><div class="flag-item">Suspicious Enrichment: ${lead.suspicious_enrichment ? 'Yes' : 'No'}</div></div></div>
<div class="toggle-section"><button class="toggle-header active" onclick="toggleSection(this)">Assessment Scores<span class="toggle-icon">▼</span></button><div class="toggle-content active"><div class="score-section"><div class="score-title">🎯 Acquisition Completeness: ${lead.acquisition_completeness_score || 'N/A'}%</div><div class="score-explanation">${generateAcquisitionExplanation(lead)}</div></div>

<div class="score-section"><div class="score-title">🔍 Enrichment Completeness: ${lead.enrichment_completeness_score || 'N/A'}%</div><div class="score-explanation">${generateEnrichmentExplanation(lead)}</div></div>

<div class="score-section"><div class="score-title">🤖 AI Coherence Score: ${assessment ? (assessment.confidence_score || 'N/A') : 'N/A'}</div>${assessment && assessment.explanation_bullets && assessment.explanation_bullets.length > 0 ? `<div class="ai-bullets">AI Explanation:${assessment.explanation_bullets.map(bullet => `<div class="ai-bullet">• ${bullet}</div>`).join('')}</div>` : ''}${assessment && assessment.corrections && Object.keys(assessment.corrections).length > 0 ? `<div class="corrections">Corrections:${Object.entries(assessment.corrections).map(([field, value]) => `<div class="correction-item">${field}: ${value}</div>`).join('')}</div>` : ''}${assessment && assessment.inferences && Object.keys(assessment.inferences).length > 0 ? `<div class="inferences">Inferences:${Object.entries(assessment.inferences).map(([field, value]) => `<div class="inference-item">${field}: ${value}</div>`).join('')}</div>` : ''}</div>

<div class="final-score final-score-bold">🏆 Final Confidence Score: ${finalScore || 'N/A'}% (Weighted: 15% + 15% + 70%)</div></div></div></div>`;
}

// Function to toggle collapsible sections
function toggleSection(button) {
    const content = button.nextElementSibling;
    const icon = button.querySelector('.toggle-icon');
    
    if (content.classList.contains('active')) {
        content.classList.remove('active');
        icon.textContent = '▶';
    } else {
        content.classList.add('active');
        icon.textContent = '▼';
    }
}

// Function to generate detailed acquisition score explanation
function generateAcquisitionExplanation(lead) {
    if (!lead.joseph_scoring_details || !lead.joseph_scoring_details.acquisition_completeness || 
        !lead.joseph_scoring_details.acquisition_completeness.details || 
        !lead.joseph_scoring_details.acquisition_completeness.details.field_scores) {
        return "Individual field scores not available";
    }
    
    const fieldScores = lead.joseph_scoring_details.acquisition_completeness.details.field_scores;
    const scoreEntries = [];
    
    // Map field score keys to readable names
    const fieldMapping = {
        'first_name_score': 'First Name',
        'last_name_score': 'Last Name', 
        'email_domain_score': 'Email Domain',
        'phone_score': 'Phone',
        'state_province_score': 'State',
        'country_score': 'Country',
        'sector_score': 'Industry',
        'company_score': 'Company',
        'website_domain_score': 'Website'
    };
    
    Object.entries(fieldScores).forEach(([key, score]) => {
        if (fieldMapping[key]) {
            scoreEntries.push(`${fieldMapping[key]}: ${score}%`);
        }
    });
    
    return scoreEntries.length > 0 ? scoreEntries.join(', ') : "No field scores available";
}

// Function to generate detailed enrichment score explanation  
function generateEnrichmentExplanation(lead) {
    if (!lead.joseph_scoring_details || !lead.joseph_scoring_details.enrichment_completeness || 
        !lead.joseph_scoring_details.enrichment_completeness.details || 
        !lead.joseph_scoring_details.enrichment_completeness.details.field_scores) {
        return "Individual field scores not available";
    }
    
    const fieldScores = lead.joseph_scoring_details.enrichment_completeness.details.field_scores;
    const scoreEntries = [];
    
    // Map field score keys to readable names
    const fieldMapping = {
        'account_name_zi_cdp_score': 'ZI Account Name',
        'zi_company_name_score': 'ZI Company Name',
        'zi_website_domain_score': 'ZI Website',
        'zi_company_state_score': 'ZI State',
        'zi_company_country_score': 'ZI Country',
        'zi_employees_score': 'ZI Employees'
    };
    
    Object.entries(fieldScores).forEach(([key, score]) => {
        if (fieldMapping[key]) {
            scoreEntries.push(`${fieldMapping[key]}: ${score}%`);
        }
    });
    
    return scoreEntries.length > 0 ? scoreEntries.join(', ') : "No field scores available";
}

// Function to generate HTML for batch results (SOQL Query and Excel)
function generateBatchResultsHTML(leads, summary) {
    let batchHTML = `<div style="margin-bottom: 10px; padding: 10px; background-color: #e8f5e8;"><h3 style="margin: 0;">✅ Batch Analysis Complete!</h3><p style="margin: 0;"><strong>Processed ${leads.length} leads successfully</strong></p></div>

<div class="lead-container summary-container"><h3 class="lead-header">📊 Summary Statistics</h3><div class="toggle-section"><button class="toggle-header active" onclick="toggleSection(this)">Overall Scores<span class="toggle-icon">▼</span></button><div class="toggle-content active"><div class="score-section"><div class="score-title">Average Acquisition Score: ${summary.avgAcquisition || 'N/A'}</div></div><div class="score-section"><div class="score-title">Average Enrichment Score: ${summary.avgEnrichment || 'N/A'}</div></div><div class="score-section"><div class="score-title">Average AI Coherence Score: ${summary.avgConfidence || 'N/A'}</div></div><div class="final-score final-score-bold">🏆 Average Final Confidence Score: ${summary.avgFinal || 'N/A'} (Weighted: 15% + 15% + 70%)</div></div></div></div>`;

    // Add individual lead results with alternating backgrounds
    leads.forEach((lead, index) => {
        const isEven = index % 2 === 0;
        batchHTML += generateSingleLeadHTML(lead, lead.confidence_assessment, isEven);
    });

    return batchHTML;
}

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
    
    // Excel upload event handlers
    document.getElementById('excelFile').addEventListener('change', handleExcelFileChange);
    document.getElementById('parseExcelBtn').addEventListener('click', handleParseExcel);
    document.getElementById('validateLeadIdsBtn').addEventListener('click', handleValidateLeadIds);
    document.getElementById('analyzeExcelBtn').addEventListener('click', handleAnalyzeExcel);
    document.getElementById('exportExcelBtn').addEventListener('click', handleExportExcel);
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
            const summary = data.data.summary;
            const leads = data.data.leads;
            const queryInfo = data.data.query_info;
            
            // Calculate hybrid scoring averages
            let acquisitionScores = [];
            let enrichmentScores = [];
            let overallScores = [];
            
            leads.forEach(lead => {
                if (lead.acquisition_completeness_score) acquisitionScores.push(lead.acquisition_completeness_score);
                if (lead.enrichment_completeness_score) enrichmentScores.push(lead.enrichment_completeness_score);
                if (lead.acquisition_completeness_score && lead.enrichment_completeness_score && lead.confidence_assessment && lead.confidence_assessment.confidence_score) {
                    const finalScore = Math.round((lead.acquisition_completeness_score * 0.15) + (lead.enrichment_completeness_score * 0.15) + (lead.confidence_assessment.confidence_score * 0.70));
                    overallScores.push(finalScore);
                }
            });
            
            const avgAcquisition = acquisitionScores.length > 0 ? Math.round(acquisitionScores.reduce((a, b) => a + b, 0) / acquisitionScores.length) : 'N/A';
            const avgEnrichment = enrichmentScores.length > 0 ? Math.round(enrichmentScores.reduce((a, b) => a + b, 0) / enrichmentScores.length) : 'N/A';
            const avgFinal = overallScores.length > 0 ? Math.round(overallScores.reduce((a, b) => a + b, 0) / overallScores.length) : 'N/A';
            
            // Generate collapsible HTML structure for batch results
            const summaryData = {
                avgAcquisition: avgAcquisition,
                avgEnrichment: avgEnrichment,
                avgConfidence: summary.avg_confidence_score,
                avgFinal: avgFinal
            };
            
            responseDiv.innerHTML = generateBatchResultsHTML(leads, summaryData);
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
            const lead = data.lead_data;  // Fixed: use lead_data instead of data
            const assessment = data.confidence_assessment;  // Get assessment from top level
            
            // Generate collapsible HTML structure
            responseDiv.innerHTML = generateSingleLeadHTML(lead, assessment);
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

// Excel Upload Handlers

function handleExcelFileChange(e) {
    const file = e.target.files[0];
    const parseBtn = document.getElementById('parseExcelBtn');
    const configDiv = document.getElementById('excelConfig');
    const responseDiv = document.getElementById('excelResponse');
    
    if (file) {
        excelFileData = file;
        parseBtn.disabled = false;
        configDiv.style.display = 'none';
        responseDiv.style.display = 'none';
        
        // Reset all subsequent buttons
        document.getElementById('validateLeadIdsBtn').disabled = true;
        document.getElementById('analyzeExcelBtn').disabled = true;
        document.getElementById('exportExcelBtn').disabled = true;
        
        // Clear previous data
        excelPreviewData = null;
        excelAnalysisResults = null;
    } else {
        excelFileData = null;
        parseBtn.disabled = true;
        configDiv.style.display = 'none';
    }
}

async function handleParseExcel(e) {
    e.preventDefault();
    
    if (!excelFileData) {
        alert('Please select an Excel file first.');
        return;
    }
    
    const button = e.target;
    const responseDiv = document.getElementById('excelResponse');
    
    // Show loading state
    button.disabled = true;
    button.textContent = 'Parsing...';
    responseDiv.innerHTML = 'Parsing Excel file...';
    responseDiv.className = 'response loading';
    responseDiv.style.display = 'block';
    
    try {
        const formData = new FormData();
        formData.append('file', excelFileData);
        
        const response = await fetch('/excel/parse', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            excelPreviewData = data.data;
            populateExcelSelectors(data.data);
            responseDiv.innerHTML = `✅ File parsed successfully! Found ${data.data.total_rows} rows in ${data.data.sheet_names.length} sheet(s).\n\nSelect the sheet and Lead ID column, then validate the Lead IDs.`;
            responseDiv.className = 'response success';
            document.getElementById('excelConfig').style.display = 'block';
            document.getElementById('validateLeadIdsBtn').disabled = false;
        } else {
            responseDiv.innerHTML = JSON.stringify(data, null, 2);
            responseDiv.className = 'response error';
            document.getElementById('excelConfig').style.display = 'none';
        }
    } catch (error) {
        responseDiv.innerHTML = `Error: ${error.message}`;
        responseDiv.className = 'response error';
        document.getElementById('excelConfig').style.display = 'none';
    } finally {
        button.disabled = false;
        button.textContent = '1. Parse File';
    }
}

function populateExcelSelectors(data) {
    const sheetSelect = document.getElementById('sheetSelect');
    const columnSelect = document.getElementById('leadIdColumn');
    
    // Populate sheet selector
    sheetSelect.innerHTML = '';
    data.sheet_names.forEach(sheetName => {
        const option = document.createElement('option');
        option.value = sheetName;
        option.textContent = sheetName;
        sheetSelect.appendChild(option);
    });
    
    // Populate column selector
    columnSelect.innerHTML = '<option value="">-- Select Lead ID Column --</option>';
    data.headers.forEach(header => {
        const option = document.createElement('option');
        option.value = header;
        option.textContent = header;
        columnSelect.appendChild(option);
    });
}

async function handleValidateLeadIds(e) {
    e.preventDefault();
    
    if (!excelFileData || !excelPreviewData) {
        alert('Please parse the Excel file first.');
        return;
    }
    
    const button = e.target;
    const responseDiv = document.getElementById('excelResponse');
    const sheetName = document.getElementById('sheetSelect').value;
    const leadIdColumn = document.getElementById('leadIdColumn').value;
    
    if (!sheetName || !leadIdColumn) {
        alert('Please select both sheet and Lead ID column.');
        return;
    }
    
    // Show loading state
    button.disabled = true;
    button.textContent = 'Validating...';
    responseDiv.innerHTML = 'Validating Lead IDs with Salesforce...';
    responseDiv.className = 'response loading';
    responseDiv.style.display = 'block';
    
    try {
        const formData = new FormData();
        formData.append('file', excelFileData);
        formData.append('sheet_name', sheetName);
        formData.append('lead_id_column', leadIdColumn);
        
        const response = await fetch('/excel/validate-lead-ids', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const validationData = data.data;
            
            // Debug logging
            console.log('🔍 DEBUG: Validation response:', data);
            console.log('🔍 DEBUG: Validation data:', validationData);
            console.log('🔍 DEBUG: Invalid Lead IDs list:', validationData.invalid_lead_ids_list);
            
            let output = `✅ Validation Complete!\n\n`;
            output += `📋 Validation Summary:\n`;
            output += `- Total Lead IDs found: ${validationData.total_lead_ids}\n`;
            output += `- Valid Lead IDs: ${validationData.valid_lead_ids}\n`;
            output += `- Invalid Lead IDs: ${validationData.invalid_lead_ids}\n`;
            
            if (validationData.invalid_lead_ids_list && validationData.invalid_lead_ids_list.length > 0) {
                output += `\n❌ Invalid Lead IDs found:\n`;
                validationData.invalid_lead_ids_list.forEach(id => {
                    output += `  • ${id}\n`;
                });
                
                if (validationData.validation_summary && validationData.validation_summary.partial_validation) {
                    output += `\n⚠️ Partial validation detected. Analysis will proceed with ${validationData.valid_lead_ids} valid Lead IDs only.`;
                    output += `\n📋 Invalid Lead IDs (${validationData.invalid_lead_ids}) will be marked in red in the export.`;
                    responseDiv.className = 'response warning';
                    document.getElementById('analyzeExcelBtn').disabled = false; // Allow analysis to proceed
                } else {
                    output += `\n❌ No valid Lead IDs found. Please check your data and try again.`;
                    responseDiv.className = 'response error';
                    document.getElementById('analyzeExcelBtn').disabled = true;
                }
            } else {
                output += `\n✅ All Lead IDs are valid! You can now proceed to analyze.`;
                responseDiv.className = 'response success';
                document.getElementById('analyzeExcelBtn').disabled = false;
            }
            
            responseDiv.innerHTML = output;
        } else {
            responseDiv.innerHTML = `❌ Validation failed!\n\n${JSON.stringify(data, null, 2)}`;
            responseDiv.className = 'response error';
            document.getElementById('analyzeExcelBtn').disabled = true;
        }
    } catch (error) {
        responseDiv.innerHTML = `Error: ${error.message}`;
        responseDiv.className = 'response error';
        document.getElementById('analyzeExcelBtn').disabled = true;
    } finally {
        button.disabled = false;
        button.textContent = '2. Validate Lead IDs';
    }
}

async function handleAnalyzeExcel(e) {
    e.preventDefault();
    
    if (!excelFileData || !excelPreviewData) {
        alert('Please parse and validate the Excel file first.');
        return;
    }
    
    const button = e.target;
    const responseDiv = document.getElementById('excelResponse');
    const sheetName = document.getElementById('sheetSelect').value;
    const leadIdColumn = document.getElementById('leadIdColumn').value;
    
    // Validate inputs
    if (!sheetName || !leadIdColumn) {
        alert('Please select both sheet and Lead ID column.');
        return;
    }
    
    // Show loading state
    button.disabled = true;
    button.textContent = 'Analyzing...';
    document.getElementById('exportExcelBtn').disabled = true;
    responseDiv.innerHTML = `Analyzing all leads from Excel file with AI confidence scoring...`;
    responseDiv.className = 'response loading';
    responseDiv.style.display = 'block';
    
    try {
        const formData = new FormData();
        formData.append('file', excelFileData);
        formData.append('sheet_name', sheetName);
        formData.append('lead_id_column', leadIdColumn);
        formData.append('max_analyze', '10000'); // Set high limit to analyze all
        formData.append('include_ai_assessment', 'true'); // Always include AI assessment
        
        const response = await fetch('/excel/analyze', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            excelAnalysisResults = data;
            const summary = data.data.summary;
            const leads = data.data.leads;
            
            // Store validation summary for export
            if (data.validation_summary) {
                excelAnalysisResults.validation_summary = data.validation_summary;
            }
            
            // Display summary and individual lead results
            // Use the exact same logic as the Excel service for consistency
            const validationSummary = data.validation_summary;
            
            // Calculate metrics exactly like the Excel service
            const totalLeadIds = validationSummary ? validationSummary.total_lead_ids : summary.leads_analyzed;
            const invalidLeadIds = validationSummary ? validationSummary.invalid_lead_ids : 0;
            const validLeadIds = totalLeadIds - invalidLeadIds;
            
            // AI assessments successful = valid Lead IDs that were successfully analyzed
            const aiAssessmentsSuccessful = validLeadIds;
            
            // AI assessments failed = invalid Lead IDs (leads that couldn't be analyzed)
            const aiAssessmentsFailed = invalidLeadIds;
            
            // Calculate hybrid scoring averages for Excel results
            let acquisitionScores = [];
            let enrichmentScores = [];
            let overallScores = [];
            
            leads.forEach(lead => {
                if (lead.acquisition_completeness_score) acquisitionScores.push(lead.acquisition_completeness_score);
                if (lead.enrichment_completeness_score) enrichmentScores.push(lead.enrichment_completeness_score);
                if (lead.acquisition_completeness_score && lead.enrichment_completeness_score && lead.confidence_assessment && lead.confidence_assessment.confidence_score) {
                    const finalScore = Math.round((lead.acquisition_completeness_score * 0.15) + (lead.enrichment_completeness_score * 0.15) + (lead.confidence_assessment.confidence_score * 0.70));
                    overallScores.push(finalScore);
                }
            });
            
            const avgAcquisition = acquisitionScores.length > 0 ? Math.round(acquisitionScores.reduce((a, b) => a + b, 0) / acquisitionScores.length) : 'N/A';
            const avgEnrichment = enrichmentScores.length > 0 ? Math.round(enrichmentScores.reduce((a, b) => a + b, 0) / enrichmentScores.length) : 'N/A';
            const avgFinal = overallScores.length > 0 ? Math.round(overallScores.reduce((a, b) => a + b, 0) / overallScores.length) : 'N/A';
            
            // Generate collapsible HTML structure for Excel batch results
            const summaryData = {
                avgAcquisition: avgAcquisition,
                avgEnrichment: avgEnrichment,
                avgConfidence: summary.avg_confidence_score,
                avgFinal: avgFinal
            };
            
            responseDiv.innerHTML = generateBatchResultsHTML(leads, summaryData);
            responseDiv.className = 'response success';
            document.getElementById('exportExcelBtn').disabled = false;
        } else {
            excelAnalysisResults = null;
            responseDiv.innerHTML = JSON.stringify(data, null, 2);
            responseDiv.className = 'response error';
            document.getElementById('exportExcelBtn').disabled = true;
        }
    } catch (error) {
        responseDiv.innerHTML = `Error: ${error.message}`;
        responseDiv.className = 'response error';
        document.getElementById('exportExcelBtn').disabled = true;
    } finally {
        button.disabled = false;
        button.textContent = '3. Analyze All Leads';
    }
}

async function handleExportExcel(e) {
    e.preventDefault();
    
    if (!excelAnalysisResults) {
        alert('Please run the Excel analysis first before exporting.');
        return;
    }
    
    const button = e.target;
    const leadIdColumn = document.getElementById('leadIdColumn').value;
    const sheetName = document.getElementById('sheetSelect').value;
    
    // Show loading state
    button.disabled = true;
    button.textContent = 'Exporting...';
    
    try {
        // Create FormData to re-send the file for export
        const formData = new FormData();
        formData.append('file', excelFileData);
        formData.append('sheet_name', sheetName);
        formData.append('lead_id_column', leadIdColumn);
        formData.append('analysis_results', JSON.stringify(excelAnalysisResults.data));
        
        // Add invalid Lead IDs if available from validation results
        if (excelAnalysisResults.validation_summary && excelAnalysisResults.validation_summary.invalid_lead_ids_list) {
            formData.append('invalid_lead_ids', JSON.stringify(excelAnalysisResults.validation_summary.invalid_lead_ids_list));
            console.log('🔍 DEBUG: Passing invalid Lead IDs to export:', excelAnalysisResults.validation_summary.invalid_lead_ids_list);
        } else {
            console.log('🔍 DEBUG: No invalid Lead IDs found in validation summary');
        }
        
        const response = await fetch('/excel/export-analysis-with-file', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            await downloadFile(response, 'excel_analysis.xlsx');
            alert('Excel file with analysis results downloaded successfully!');
        } else {
            const errorData = await response.json();
            alert(`Export failed: ${errorData.message}`);
        }
    } catch (error) {
        alert(`Export error: ${error.message}`);
    } finally {
        button.disabled = false;
        button.textContent = '📊 Export Results';
    }
} 