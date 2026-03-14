"""Test file to isolate circular import issues."""
import sys
sys.path.append('backend')

try:
    from app.database import engine
    print('Database engine imported successfully')
    from app.models.hospital import Hospital
    print('Hospital model imported successfully')
    from sqlalchemy.orm import Session
    print('Session imported successfully')
    print('All imports successful!')
except Exception as e:
    print(f'Import error: {e}')