from simple_salesforce import Salesforce
from config.config import Config


class SalesforceService:
    """Service class for handling Salesforce operations"""
    
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
    
    def get_lead_by_id(self, lead_id):
        """Get specific Lead fields by Lead ID"""
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
            
            # Return the first (and should be only) record
            lead_record = result['records'][0]
            
            # Remove Salesforce metadata from the response
            if 'attributes' in lead_record:
                del lead_record['attributes']
                
            return lead_record, "Lead retrieved successfully"
            
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
            
            # Clean up records by removing Salesforce metadata
            clean_records = []
            for record in result['records']:
                if 'attributes' in record:
                    del record['attributes']
                clean_records.append(record)
            
            return {
                'records': clean_records,
                'totalSize': result['totalSize'],
                'done': result['done']
            }, "Query executed successfully"
            
        except Exception as e:
            return None, f"Error executing query: {str(e)}" 