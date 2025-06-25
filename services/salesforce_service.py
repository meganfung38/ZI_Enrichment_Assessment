from simple_salesforce import Salesforce
from config.config import Config


class SalesforceService:
    """Service class for handling Salesforce operations"""
    
    # Free email domains to check for suspicious enrichment
    FREE_EMAIL_DOMAINS = {
        'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'icloud.com',
        'protonmail.com', 'zoho.com', 'aol.com', 'live.com', 'msn.com',
        'ymail.com', 'rocketmail.com', 'me.com', 'mac.com'
    }
    
    def __init__(self):
        self.sf = None
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
    
    def _analyze_lead_flags(self, lead_record):
        """Analyze lead data and return business logic flags"""
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
            'suspicious_enrichment': suspicious_enrichment
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