import os
import sys
import pandas as pd
import logging

# Add Joseph's system to Python path
joseph_system_path = os.path.join(os.path.dirname(__file__), 'joseph_system')
dependencies_path = os.path.join(os.path.dirname(__file__), 'joseph_system', 'dependencies')

if joseph_system_path not in sys.path:
    sys.path.insert(0, joseph_system_path)

class JosephScoringWrapper:
    """
    Simple wrapper for Joseph's scoring system that handles imports and data transformation.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._acquisition_scorer = None
        self._enrichment_scorer = None
        self._initialize_scorers()
    
    def _initialize_scorers(self):
        """Initialize Joseph's scorers with proper dependency path."""
        try:
            # Import here to avoid import issues at module level
            from completeness_dependency_loader import CompletenessDependencyLoader
            from acquisition_completeness_score import AcquisitionCompletenessScorer
            from enrichment_completeness_score import EnrichmentCompletenessScorer
            
            # Initialize with correct dependencies path
            self._acquisition_scorer = AcquisitionCompletenessScorer(config_path=dependencies_path)
            self._enrichment_scorer = EnrichmentCompletenessScorer(config_path=dependencies_path)
            
            self.logger.info("Joseph's scoring system initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Joseph's scoring system: {e}")
            raise
    
    def transform_salesforce_to_dataframe(self, salesforce_lead):
        """
        Transform a single Salesforce lead record into a DataFrame for Joseph's system.
        
        Args:
            salesforce_lead: Dict containing Salesforce lead data
            
        Returns:
            pandas.DataFrame: Single-row DataFrame formatted for Joseph's system
        """
        # Extract email domain from email
        email = salesforce_lead.get('Email', '')
        email_domain = ''
        if email and '@' in email:
            email_domain = email.split('@')[1].lower()
        
        # Extract website domain from website
        website = salesforce_lead.get('Website', '')
        website_domain = ''
        if website:
            website = str(website).lower()
            if website.startswith('http://'):
                website = website[7:]
            elif website.startswith('https://'):
                website = website[8:]
            if website.startswith('www.'):
                website = website[4:]
            if '/' in website:
                website = website.split('/')[0]
            website_domain = website
        
        # Create DataFrame with Joseph's expected columns
        data = {
            'Id': [salesforce_lead.get('Id', '')],
            # For acquisition completeness
            'first_name': [salesforce_lead.get('FirstName', '')],
            'last_name': [salesforce_lead.get('LastName', '')],
            'email_domain': [email_domain],
            'phone': [salesforce_lead.get('Phone', '')],
            'state_province': [salesforce_lead.get('State', '')],
            'country': [salesforce_lead.get('Country', '')],
            'sector': [salesforce_lead.get('Industry', '')],  # Map Industry to sector
            'company': [salesforce_lead.get('Company', '')],
            'website_domain': [website_domain],
            
            # For enrichment completeness 
            'account_name_zi_cdp': [salesforce_lead.get('ZI_Company__c', '')],
            'zi_company_name': [salesforce_lead.get('ZI_Company__c', '')],
            'zi_website_domain': [self._extract_zi_website_domain(salesforce_lead.get('ZI_Website__c', ''))],
            'zi_company_state': [salesforce_lead.get('ZI_State__c', '')],
            'zi_company_country': [salesforce_lead.get('ZI_Country__c', '')],
            'zi_employees': [self._convert_to_int(salesforce_lead.get('ZI_Employees__c', ''))],
            'segment_name': [salesforce_lead.get('SegmentName', '')],  # Need to get this from SF
        }
        
        return pd.DataFrame(data)
    
    def _extract_zi_email_domain(self, zi_email):
        """Extract domain from ZI email field."""
        if zi_email and '@' in str(zi_email):
            return str(zi_email).split('@')[1].lower()
        return ''
    
    def _extract_zi_website_domain(self, zi_website):
        """Extract domain from ZI website field."""
        if not zi_website:
            return ''
        
        website = str(zi_website).lower()
        if website.startswith('http://'):
            website = website[7:]
        elif website.startswith('https://'):
            website = website[8:]
        if website.startswith('www.'):
            website = website[4:]
        if '/' in website:
            website = website.split('/')[0]
        return website
    
    def _convert_to_int(self, value):
        """Convert a value to integer, return 0 if conversion fails."""
        if value is None or value == '':
            return 0
        try:
            return int(float(str(value)))
        except (ValueError, TypeError):
            return 0
    
    def calculate_acquisition_completeness(self, salesforce_lead):
        """
        Calculate acquisition completeness score for a single Salesforce lead.
        
        Args:
            salesforce_lead: Dict containing Salesforce lead data
            
        Returns:
            Dict containing score and details
        """
        try:
            # Transform to DataFrame
            df = self.transform_salesforce_to_dataframe(salesforce_lead)
            
            # Calculate score using Joseph's system
            scored_df = self._acquisition_scorer.score(df)
            
            # Extract results from the scored DataFrame
            result_row = scored_df.iloc[0]
            
            # Extract individual field scores
            field_scores = {}
            score_columns = [col for col in scored_df.columns if col.endswith('_score')]
            for col in score_columns:
                if col != 'acquisition_completeness_score':
                    field_scores[col] = float(result_row.get(col, 0))
            
            return {
                'score': float(result_row.get('acquisition_completeness_score', 0)),
                'percentage': float(result_row.get('acquisition_completeness_score', 0)),
                'component': 'acquisition_completeness',
                'details': {
                    'scored_fields': scored_df.columns.tolist(),
                    'field_scores': field_scores,
                    'lead_id': salesforce_lead.get('Id')
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating acquisition completeness for lead {salesforce_lead.get('Id')}: {e}")
            return {
                'score': 0,
                'percentage': 0,
                'component': 'acquisition_completeness',
                'details': {'error': str(e)}
            }
    
    def calculate_enrichment_completeness(self, salesforce_lead):
        """
        Calculate enrichment completeness score for a single Salesforce lead.
        
        Args:
            salesforce_lead: Dict containing Salesforce lead data
            
        Returns:
            Dict containing score and details
        """
        try:
            # Transform to DataFrame
            df = self.transform_salesforce_to_dataframe(salesforce_lead)
            
            # Calculate score using Joseph's system
            scored_df = self._enrichment_scorer.score(df)
            
            # Extract results from the scored DataFrame
            result_row = scored_df.iloc[0]
            
            # Extract individual field scores
            field_scores = {}
            score_columns = [col for col in scored_df.columns if col.endswith('_score')]
            for col in score_columns:
                if col != 'enrichment_completeness_score':
                    field_scores[col] = float(result_row.get(col, 0))
            
            return {
                'score': float(result_row.get('enrichment_completeness_score', 0)),
                'percentage': float(result_row.get('enrichment_completeness_score', 0)),
                'component': 'enrichment_completeness',
                'details': {
                    'scored_fields': scored_df.columns.tolist(),
                    'field_scores': field_scores,
                    'lead_id': salesforce_lead.get('Id')
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating enrichment completeness for lead {salesforce_lead.get('Id')}: {e}")
            return {
                'score': 0,
                'percentage': 0,
                'component': 'enrichment_completeness',
                'details': {'error': str(e)}
            }
    
    def calculate_both_scores(self, salesforce_lead):
        """
        Calculate both acquisition and enrichment completeness scores.
        
        Args:
            salesforce_lead: Dict containing Salesforce lead data
            
        Returns:
            Dict containing both scores
        """
        acquisition_result = self.calculate_acquisition_completeness(salesforce_lead)
        enrichment_result = self.calculate_enrichment_completeness(salesforce_lead)
        
        return {
            'acquisition_completeness': acquisition_result,
            'enrichment_completeness': enrichment_result,
            'lead_id': salesforce_lead.get('Id')
        } 