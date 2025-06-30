from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime
import json
import io

class ExcelService:
    """Service for exporting lead analysis data to Excel format"""
    
    def __init__(self):
        self.header_font = Font(bold=True, color="FFFFFF")
        self.header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        self.summary_font = Font(bold=True, color="000000")
        self.summary_fill = PatternFill(start_color="E7F3FF", end_color="E7F3FF", fill_type="solid")
        self.border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        self.center_alignment = Alignment(horizontal='center', vertical='center')
        self.wrap_alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
    
    def create_lead_analysis_excel(self, analysis_data, summary_data, query_info=None, filename_prefix="lead_analysis"):
        """Create Excel file from lead analysis data"""
        wb = Workbook()
        ws = wb.active
        ws.title = "Lead Analysis"
        
        # Add title and metadata
        current_row = 1
        ws.merge_cells(f'A{current_row}:L{current_row}')
        ws[f'A{current_row}'] = "ZoomInfo Lead Quality Analysis Report"
        ws[f'A{current_row}'].font = Font(bold=True, size=16)
        ws[f'A{current_row}'].alignment = self.center_alignment
        current_row += 1
        
        # Add generation timestamp
        ws.merge_cells(f'A{current_row}:L{current_row}')
        ws[f'A{current_row}'] = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ws[f'A{current_row}'].alignment = self.center_alignment
        current_row += 2
        
        # Add summary section if provided
        if summary_data:
            current_row = self._add_summary_section(ws, summary_data, query_info, current_row)
            current_row += 1
        
        # Add headers
        headers = [
            "Lead ID", "Email", "Company Name", "Employee Count", "Website", 
            "Enrichment Status", "First Channel", "Email Domain",
            "Not in TAM", "Suspicious Enrichment", "Confidence Score", 
            "Explanation", "Corrections", "Inferences", "AI Status"
        ]
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=current_row, column=col, value=header)
            cell.font = self.header_font
            cell.fill = self.header_fill
            cell.alignment = self.center_alignment
            cell.border = self.border
        
        current_row += 1
        
        # Add data rows
        for lead in analysis_data:
            self._add_lead_row(ws, lead, current_row)
            current_row += 1
        
        # Auto-adjust column widths
        self._auto_adjust_columns(ws)
        
        # Create file buffer
        file_buffer = io.BytesIO()
        wb.save(file_buffer)
        file_buffer.seek(0)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{filename_prefix}_{timestamp}.xlsx"
        
        return file_buffer, filename
    
    def _add_summary_section(self, ws, summary_data, query_info, start_row):
        """Add summary statistics section to the worksheet"""
        ws.merge_cells(f'A{start_row}:D{start_row}')
        ws[f'A{start_row}'] = "Analysis Summary"
        ws[f'A{start_row}'].font = self.summary_font
        ws[f'A{start_row}'].fill = self.summary_fill
        start_row += 1
        
        # Summary statistics
        summary_items = [
            ("Total Leads Analyzed", summary_data.get('leads_analyzed', 0)),
            ("Leads with Issues", summary_data.get('leads_with_issues', 0)),
            ("Issue Percentage", f"{summary_data.get('issue_percentage', 0)}%"),
            ("Average Confidence Score", summary_data.get('avg_confidence_score', 0)),
            ("Not in TAM Count", summary_data.get('not_in_tam_count', 0)),
            ("Suspicious Enrichment Count", summary_data.get('suspicious_enrichment_count', 0)),
        ]
        
        if summary_data.get('total_query_results'):
            summary_items.insert(0, ("Total Query Results", summary_data.get('total_query_results', 0)))
        
        if summary_data.get('ai_assessments_successful') is not None:
            summary_items.extend([
                ("AI Assessments Successful", summary_data.get('ai_assessments_successful', 0)),
                ("AI Assessments Failed", summary_data.get('ai_assessments_failed', 0))
            ])
        
        for label, value in summary_items:
            ws[f'A{start_row}'] = label
            ws[f'B{start_row}'] = value
            ws[f'A{start_row}'].font = Font(bold=True)
            start_row += 1
        
        # Query info if available
        if query_info:
            start_row += 1
            ws.merge_cells(f'A{start_row}:D{start_row}')
            ws[f'A{start_row}'] = "Query Information"
            ws[f'A{start_row}'].font = self.summary_font
            ws[f'A{start_row}'].fill = self.summary_fill
            start_row += 1
            
            if query_info.get('original_query'):
                ws[f'A{start_row}'] = "Original Query"
                ws[f'B{start_row}'] = query_info['original_query']
                ws[f'B{start_row}'].alignment = self.wrap_alignment
                start_row += 1
            
            if query_info.get('execution_time'):
                ws[f'A{start_row}'] = "Execution Time"
                ws[f'B{start_row}'] = query_info['execution_time']
                start_row += 1
        
        return start_row + 1
    
    def _add_lead_row(self, ws, lead, row):
        """Add a single lead's data to the worksheet"""
        # Extract confidence assessment data
        confidence_assessment = lead.get('confidence_assessment', {})
        confidence_score = confidence_assessment.get('confidence_score', '') if confidence_assessment else ''
        
        # Format explanation bullets
        explanation_bullets = confidence_assessment.get('explanation_bullets', []) if confidence_assessment else []
        explanation_text = '\n'.join(explanation_bullets) if explanation_bullets else ''
        
        # Format corrections and inferences
        corrections = confidence_assessment.get('corrections', {}) if confidence_assessment else {}
        corrections_text = json.dumps(corrections, indent=2) if corrections else ''
        
        inferences = confidence_assessment.get('inferences', {}) if confidence_assessment else {}
        inferences_text = json.dumps(inferences, indent=2) if inferences else ''
        
        # Data for each column
        row_data = [
            lead.get('Id', ''),
            lead.get('Email', ''),
            lead.get('ZI_Company_Name__c', ''),
            lead.get('ZI_Employees__c', ''),
            lead.get('Website', ''),
            lead.get('LS_Enrichment_Status__c', ''),
            lead.get('First_Channel__c', ''),
            lead.get('email_domain', ''),
            'Yes' if lead.get('not_in_TAM') else 'No',
            'Yes' if lead.get('suspicious_enrichment') else 'No',
            confidence_score,
            explanation_text,
            corrections_text,
            inferences_text,
            lead.get('ai_assessment_status', '')
        ]
        
        for col, value in enumerate(row_data, 1):
            cell = ws.cell(row=row, column=col, value=value)
            cell.border = self.border
            
            # Special formatting for certain columns
            if col in [9, 10]:  # Boolean flags
                cell.alignment = self.center_alignment
                if value == 'Yes':
                    cell.fill = PatternFill(start_color="FFE6E6", end_color="FFE6E6", fill_type="solid")
            elif col == 11:  # Confidence score
                cell.alignment = self.center_alignment
                if isinstance(value, (int, float)) and value > 0:
                    if value >= 80:
                        cell.fill = PatternFill(start_color="E6FFE6", end_color="E6FFE6", fill_type="solid")
                    elif value >= 60:
                        cell.fill = PatternFill(start_color="FFFACD", end_color="FFFACD", fill_type="solid")
                    else:
                        cell.fill = PatternFill(start_color="FFE6E6", end_color="FFE6E6", fill_type="solid")
            elif col in [12, 13, 14]:  # Text fields that might be long
                cell.alignment = self.wrap_alignment
    
    def _auto_adjust_columns(self, ws):
        """Auto-adjust column widths based on content"""
        column_widths = {
            1: 20,   # Lead ID
            2: 25,   # Email
            3: 20,   # Company Name
            4: 12,   # Employee Count
            5: 20,   # Website
            6: 15,   # Enrichment Status
            7: 15,   # First Channel
            8: 15,   # Email Domain
            9: 12,   # Not in TAM
            10: 15,  # Suspicious Enrichment
            11: 12,  # Confidence Score
            12: 40,  # Explanation
            13: 25,  # Corrections
            14: 25,  # Inferences
            15: 12   # AI Status
        }
        
        for col, width in column_widths.items():
            ws.column_dimensions[get_column_letter(col)].width = width
        
        # Set row heights for better readability
        for row in ws.iter_rows():
            ws.row_dimensions[row[0].row].height = 25
    
    def create_single_lead_excel(self, lead_data, filename_prefix="lead_confidence"):
        """Create Excel file for a single lead confidence assessment"""
        return self.create_lead_analysis_excel(
            analysis_data=[lead_data],
            summary_data=None,
            query_info=None,
            filename_prefix=filename_prefix
        ) 