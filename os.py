

import os

class Config:
    AZURE_DB_HOST = os.getenv('AZURE_DB_HOST', 'your-azure-mysql-server.mysql.database.azure.com')
    AZURE_DB_USER = os.getenv('AZURE_DB_USER', 'your-admin-username@your-azure-mysql-server')
    AZURE_DB_PASSWORD = os.getenv('AZURE_DB_PASSWORD', 'your-admin-password')
    AZURE_DB_SUPER = os.getenv('AZURE_DB_SUPER', 'aiwiz_super_database')
