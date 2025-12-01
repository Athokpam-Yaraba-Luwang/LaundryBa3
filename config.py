import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # General
    ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'
    SECRET_KEY_BUSINESS = os.getenv('SECRET_KEY_BUSINESS', 'dev_key_business')
    SECRET_KEY_CUSTOMER = os.getenv('SECRET_KEY_CUSTOMER', 'dev_key_customer')

    # Ports (Cloud Run sets PORT, but we need defaults for local)
    PORT_BUSINESS = int(os.getenv('PORT_BUSINESS', 5000))
    PORT_CUSTOMER = int(os.getenv('PORT_CUSTOMER', 5001))

    # URLs
    BUSINESS_APP_URL = os.getenv('BUSINESS_APP_URL', f'http://localhost:{PORT_BUSINESS}')
    
    # Database
    # On Cloud Run, use /tmp for SQLite if not using Cloud SQL
    IS_CLOUD_RUN = os.getenv('K_SERVICE') is not None
    DB_FILE = "/tmp/agents_memory.db" if IS_CLOUD_RUN else "agents_memory.db"
    USE_CLOUD_SQL = os.getenv("USE_CLOUD_SQL", "False") == "True"

    # AI / Google
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') # Fallback
