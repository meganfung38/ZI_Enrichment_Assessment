from simple_salesforce import Salesforce
from config.config import Config
from typing import Optional


class SalesforceService:
    """Service class for handling Salesforce operations"""
    
    # Free email domains to check for suspicious enrichment
    FREE_EMAIL_DOMAINS = {
        'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'icloud.com',
        'protonmail.com', 'zoho.com', 'aol.com', 'live.com', 'msn.com',
        'ymail.com', 'rocketmail.com', 'me.com', 'mac.com'
    }
    
    def __init__(self):
        self.sf: Optional[Salesforce] = None
        self._is_connected = False
    
    def connect(self):
        """Establish connection to Salesforce"""
        try:
            # Validate configuration first
            Config.validate_salesforce_config()
            
            # Create Salesforce connection
            self.sf = Salesforce(
                username=Config.SF_USERNAME,
                password=Config.SF_PASSWORD,
                security_token=Config.SF_SECURITY_TOKEN,
                domain=Config.SF_DOMAIN
            )
            
            self._is_connected = True
            return True
        except Exception as e:
            print(f"Failed to connect to Salesforce: {str(e)}")
            self._is_connected = False
            return False
    
    def ensure_connection(self):
        """Ensure we have an active Salesforce connection"""
        if not self._is_connected or not self.sf:
            return self.connect()
        return True
    
    def test_connection(self):
        """Test if connection is working by running a simple query"""
        try:
            if not self.ensure_connection():
                return False, "Failed to establish connection"
            
            # Simple test - query 5 Lead IDs
            assert self.sf is not None  # Type hint for linter
            query_result = self.sf.query("SELECT Id FROM Lead LIMIT 5")
            
            # If we get here, connection is working and we can query data
            record_count = len(query_result['records'])
            return True, f"Connection successful - Retrieved {record_count} Lead records"
            
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    
    def get_connection_info(self):
        """Get basic connection information"""
        if not self._is_connected or not self.sf:
            return None
        
        return {
            "instance_url": self.sf.sf_instance,
            "session_id": "Connected" if self.sf.session_id else "Not Connected",
            "api_version": self.sf.sf_version
        }
    
    def _is_free_email_domain(self, email):
        """Check if email uses a free email domain"""
        if not email:
            return False
        try:
            domain = email.split('@')[1].lower()
            return bool(domain in self.FREE_EMAIL_DOMAINS)
        except (IndexError, AttributeError):
            return False
    
    def _extract_email_domain(self, email):
        """Extract domain from email address"""
        if not email:
            return None
        try:
            domain = email.split('@')[1].lower().strip()
            return domain if domain else None
        except (IndexError, AttributeError):
            return None
    
    def _analyze_lead_flags(self, lead_record):
        """Analyze lead data and return business logic flags and email domain"""
        # Extract values with explicit None handling
        zi_employees = lead_record.get('ZI_Employees__c')
        zi_company_name = lead_record.get('ZI_Company_Name__c')
        email = lead_record.get('Email')
        website = lead_record.get('Website')
        
        # Convert employee count to int if it exists, default to 0
        try:
            employee_count = int(zi_employees) if zi_employees is not None else 0
        except (ValueError, TypeError):
            employee_count = 0
        
        # Normalize string values - treat empty strings as None
        zi_company_name = zi_company_name.strip() if zi_company_name else None
        email = email.strip() if email else None
        website = website.strip() if website else None
        
        # Extract email domain
        email_domain = self._extract_email_domain(email)
        
        # Flag 1: not_in_TAM
        # True when ZI_Employees__c > 100 AND ZI_Company_Name__c is null/empty
        not_in_tam = bool(employee_count > 100 and not zi_company_name)
        
        # Flag 2: suspicious_enrichment  
        # True when: free email domain AND no website AND has company name AND > 100 employees
        has_free_email = self._is_free_email_domain(email)
        has_no_website = not website  # website is null/empty
        has_company_name = bool(zi_company_name)  # company name is populated
        has_many_employees = employee_count > 100
        
        suspicious_enrichment = bool(
            has_free_email and 
            has_no_website and 
            has_company_name and 
            has_many_employees
        )
        
        return {
            'not_in_TAM': not_in_tam,
            'suspicious_enrichment': suspicious_enrichment,
            'email_domain': email_domain
        }
    
    def get_lead_by_id(self, lead_id):
        """Get specific Lead fields by Lead ID with business logic flags"""
        try:
            if not self.ensure_connection():
                return None, "Failed to establish Salesforce connection"
            
            # Query for specific ZoomInfo fields
            query = """
            SELECT Id, First_Channel__c, ZI_Company_Name__c, Email, Website, 
                   ZI_Employees__c, LS_Enrichment_Status__c
            FROM Lead 
            WHERE Id = '{}'
            """.format(lead_id)
            
            assert self.sf is not None  # Type hint for linter
            result = self.sf.query(query)
            
            if result['totalSize'] == 0:
                return None, f"No Lead found with ID: {lead_id}"
            
            # Get the lead record
            lead_record = result['records'][0]
            
            # Remove Salesforce metadata from the response
            if 'attributes' in lead_record:
                del lead_record['attributes']
            
            # Add business logic flags
            flags = self._analyze_lead_flags(lead_record)
            lead_record.update(flags)
                
            return lead_record, "Lead retrieved successfully with analysis"
            
        except Exception as e:
            return None, f"Error retrieving Lead: {str(e)}"
    
    def query_leads(self, query_conditions=None, limit=100):
        """Query leads with optional conditions"""
        try:
            if not self.ensure_connection():
                return None, "Failed to establish Salesforce connection"
            
            # Base query with ZoomInfo fields
            base_query = """
            SELECT Id, First_Channel__c, ZI_Company_Name__c, Email, Website, 
                   ZI_Employees__c, LS_Enrichment_Status__c
            FROM Lead
            """
            
            # Add conditions if provided
            if query_conditions:
                base_query += f" WHERE {query_conditions}"
            
            # Add limit
            base_query += f" LIMIT {limit}"
            
            assert self.sf is not None  # Type hint for linter
            result = self.sf.query(base_query)
            
            # Clean up records by removing Salesforce metadata and add flags
            clean_records = []
            for record in result['records']:
                if 'attributes' in record:
                    del record['attributes']
                
                # Add business logic flags
                flags = self._analyze_lead_flags(record)
                record.update(flags)
                clean_records.append(record)
            
            return {
                'records': clean_records,
                'totalSize': result['totalSize'],
                'done': result['done']
            }, "Query executed successfully"
            
        except Exception as e:
            return None, f"Error executing query: {str(e)}"

    def preview_soql_query(self, soql_query, limit=100):
        """Preview SOQL query results - just return Lead IDs and count"""
        import time
        start_time = time.time()
        
        try:
            if not self.ensure_connection():
                return None, "Failed to establish Salesforce connection"
            
            # Validate SOQL query contains Id field
            if not self._validate_soql_query(soql_query):
                return None, "SOQL query must include 'Id' in SELECT clause and cannot contain dangerous operations"
            
            # Add LIMIT to the query for preview if not already present
            query_upper = soql_query.upper()
            if 'LIMIT' not in query_upper:
                preview_query = f"{soql_query} LIMIT {limit}"
            else:
                preview_query = soql_query
            
            # Execute the SOQL query to get lead IDs only
            assert self.sf is not None  # Type hint for linter
            query_result = self.sf.query(preview_query)
            
            execution_time = time.time() - start_time
            
            # Extract just the Lead IDs
            lead_ids = [record['Id'] for record in query_result['records']]
            
            result = {
                'total_found': query_result['totalSize'],
                'preview_count': len(lead_ids),
                'lead_ids': lead_ids,
                'query_info': {
                    'original_query': soql_query,
                    'preview_query': preview_query,
                    'execution_time': f"{execution_time:.2f}s",
                    'has_more': not query_result['done']
                }
            }
            
            return result, f"Found {query_result['totalSize']} total leads, showing first {len(lead_ids)}"
            
        except Exception as e:
            return None, f"Error previewing SOQL query: {str(e)}"

    def analyze_leads_from_query(self, soql_query, max_analyze=100, include_ai_assessment=True):
        """Analyze leads from a custom SOQL query with quality assessment and AI confidence scoring"""
        import time
        start_time = time.time()
        
        try:
            if not self.ensure_connection():
                return None, "Failed to establish Salesforce connection"
            
            # Validate SOQL query contains Id field
            if not self._validate_soql_query(soql_query):
                return None, "SOQL query must include 'Id' in SELECT clause and cannot contain dangerous operations"
            
            # Execute the SOQL query to get lead IDs only (much faster than query_all)
            assert self.sf is not None  # Type hint for linter
            
            # Get only the IDs we need to analyze (limit the query from the start)
            limited_query = f"{soql_query} LIMIT {max_analyze}"
            id_result = self.sf.query(limited_query)
            lead_ids_to_analyze = [record['Id'] for record in id_result['records']]
            actual_analyze_count = len(lead_ids_to_analyze)
            
            # If no leads found, return early
            if actual_analyze_count == 0:
                return {
                    'summary': {
                        'total_query_results': 0,
                        'leads_analyzed': 0,
                        'leads_with_issues': 0,
                        'not_in_tam_count': 0,
                        'suspicious_enrichment_count': 0,
                        'avg_confidence_score': 0
                    },
                    'leads': [],
                    'query_info': {
                        'original_query': soql_query,
                        'execution_time': f"{time.time() - start_time:.2f}s",
                        'total_found': 0,
                        'analyzed_count': 0
                    }
                }, "No leads found matching the query"
            
            # For total count, we can estimate or get it if needed
            # For now, we'll use the actual count we got (could be less than total if limited)
            total_found = id_result['totalSize'] if not id_result.get('done', True) else actual_analyze_count
            
            # Process leads with AI confidence assessment
            analyzed_leads = []
            leads_with_issues = 0
            not_in_tam_count = 0
            suspicious_enrichment_count = 0
            total_confidence_score = 0
            successful_ai_assessments = 0
            
            # Import here to avoid circular imports
            from services.openai_service import generate_lead_confidence_assessment
            
            # Get all lead data in one batch query (much faster!)
            batch_leads = self._analyze_lead_batch(lead_ids_to_analyze, include_details=True)
            
            # Process each lead for AI assessment
            for lead_data in batch_leads:
                try:
                    # Count basic quality issues
                    if lead_data.get('not_in_TAM') or lead_data.get('suspicious_enrichment'):
                        leads_with_issues += 1
                    if lead_data.get('not_in_TAM'):
                        not_in_tam_count += 1
                    if lead_data.get('suspicious_enrichment'):
                        suspicious_enrichment_count += 1
                    
                    # Generate AI confidence assessment if requested
                    if include_ai_assessment:
                        assessment, ai_message = generate_lead_confidence_assessment(lead_data)
                        if assessment and assessment.get('confidence_score') is not None:
                            lead_data['confidence_assessment'] = assessment
                            lead_data['ai_assessment_status'] = 'success'
                            total_confidence_score += assessment.get('confidence_score', 0)
                            successful_ai_assessments += 1
                        else:
                            lead_data['confidence_assessment'] = None
                            lead_data['ai_assessment_status'] = f'failed: {ai_message}'
                    
                    # Always include full lead data
                    analyzed_leads.append(lead_data)
                        
                except Exception as e:
                    print(f"Error processing lead {lead_data.get('Id', 'unknown')}: {str(e)}")
                    continue
            
            execution_time = time.time() - start_time
            avg_confidence_score = (total_confidence_score / successful_ai_assessments) if successful_ai_assessments > 0 else 0
            
            result = {
                'summary': {
                    'total_query_results': total_found,
                    'leads_analyzed': actual_analyze_count,
                    'leads_with_issues': leads_with_issues,
                    'not_in_tam_count': not_in_tam_count,
                    'suspicious_enrichment_count': suspicious_enrichment_count,
                    'issue_percentage': round((leads_with_issues / actual_analyze_count) * 100, 2) if actual_analyze_count > 0 else 0,
                    'avg_confidence_score': round(avg_confidence_score, 1),
                    'ai_assessments_successful': successful_ai_assessments,
                    'ai_assessments_failed': actual_analyze_count - successful_ai_assessments
                },
                'leads': analyzed_leads,
                'query_info': {
                    'original_query': soql_query,
                    'execution_time': f"{execution_time:.2f}s",
                    'total_found': total_found,
                    'analyzed_count': actual_analyze_count,
                    'skipped_count': total_found - actual_analyze_count,
                    'include_ai_assessment': include_ai_assessment
                }
            }
            
            return result, f"Successfully analyzed {actual_analyze_count} of {total_found} leads from query with AI confidence scoring"
            
        except Exception as e:
            return None, f"Error analyzing leads from query: {str(e)}"
    
    def _validate_soql_query(self, soql_query):
        """Validate SOQL query for safety and required fields"""
        if not soql_query:
            return False
        
        # Convert to uppercase for checking
        query_upper = soql_query.upper().strip()
        
        # Must be a SELECT query
        if not query_upper.startswith('SELECT'):
            return False
        
        # Must include Id field
        if 'ID' not in query_upper or 'SELECT ID' not in query_upper.replace(',', ' ').replace('\n', ' '):
            return False
        
        # Check for dangerous operations
        dangerous_keywords = ['DELETE', 'UPDATE', 'INSERT', 'UPSERT', 'MERGE']
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return False
        
        return True
    
    def _analyze_lead_batch(self, lead_ids, include_details=True):
        """Analyze a batch of leads by their IDs"""
        try:
            # Build batch query for all lead IDs
            ids_string = "', '".join(lead_ids)
            batch_query = f"""
            SELECT Id, First_Channel__c, ZI_Company_Name__c, Email, Website, 
                   ZI_Employees__c, LS_Enrichment_Status__c
            FROM Lead 
            WHERE Id IN ('{ids_string}')
            """
            
            assert self.sf is not None  # Type hint for linter
            result = self.sf.query(batch_query)
            
            analyzed_leads = []
            for record in result['records']:
                # Remove Salesforce metadata
                if 'attributes' in record:
                    del record['attributes']
                
                # Add business logic flags
                flags = self._analyze_lead_flags(record)
                
                if include_details:
                    # Include all lead data
                    record.update(flags)
                    analyzed_leads.append(record)
                else:
                    # Include only ID and flags
                    analyzed_leads.append({
                        'Id': record['Id'],
                        'not_in_TAM': flags['not_in_TAM'],
                        'suspicious_enrichment': flags['suspicious_enrichment']
                    })
            
            return analyzed_leads
            
        except Exception as e:
            # Return empty results for this batch on error
            print(f"Error analyzing batch: {str(e)}")
            return [] 