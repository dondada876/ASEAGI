"""
ASEAGI Workspace Configuration
Legal Intelligence workspace for PROJ344 document analysis
"""

# Workspace Identity
WORKSPACE_ID = 'legal'
WORKSPACE_NAME = 'Legal Intelligence (PROJ344)'
WORKSPACE_TYPE = 'legal'

# Repository Information
REPOSITORY_NAME = 'ASEAGI'
REPOSITORY_URL = 'https://github.com/dondada876/ASEAGI'

# Default Bug Tracker Settings
DEFAULT_COMPONENT = 'legal_document_scanner'
DEFAULT_ENVIRONMENT = 'production'

# File Export Paths
BUG_EXPORT_DIR = '/data/bugs/legal'
LOG_EXPORT_DIR = '/data/logs/legal'

# Feature Flags
ENABLE_AUTO_BUG_CREATION = True
ENABLE_FILE_EXPORTS = True
ENABLE_EXTERNAL_INTEGRATION = False

# PROJ344 Specific Settings
CASE_ID = 'ashe-bucknor-j24-00478'
CASE_NUMBER = 'J24-00478'
