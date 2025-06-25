import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Salesforce Configuration
    SF_USERNAME = os.getenv('SF_USERNAME')
    SF_PASSWORD = os.getenv('SF_PASSWORD')
    SF_SECURITY_TOKEN = os.getenv('SF_SECURITY_TOKEN')
    SF_DOMAIN = os.getenv('SF_DOMAIN', 'login')
    
    @staticmethod
    def validate_salesforce_config():
        """Validate that all required Salesforce credentials are present"""
        required_vars = ['SF_USERNAME', 'SF_PASSWORD', 'SF_SECURITY_TOKEN']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 