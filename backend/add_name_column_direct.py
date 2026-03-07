"""
Direct SQL script to add name column to doctors table.
This bypasses the circular import issue in Alembic.
"""
import os
import psycopg2
from psycopg2 import sql
from urllib.parse import urlparse

def parse_database_url(url):
    """Parse PostgreSQL URL into components."""
    parsed = urlparse(url)
    return {
        'host': parsed.hostname or 'localhost',
        'port': parsed.port or 5432,
        'database': parsed.path.lstrip('/'),
        'user': parsed.username or 'postgres',
        'password': parsed.password or 'postgres',
    }

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/hospital_db"
)

db_config = parse_database_url(DATABASE_URL)

def add_name_column():
    """Add name column to doctors table if it doesn't exist."""
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password']
        )
        cursor = conn.cursor()
        
        print("✓ Connected to database")
        
        # Check if column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'doctors' AND column_name = 'name'
        """)
        
        if cursor.fetchone():
            print("✓ Column 'name' already exists in doctors table")
            cursor.close()
            conn.close()
            return True
        
        print("Adding 'name' column to doctors table...")
        
        # Add name column (nullable initially)
        cursor.execute("""
            ALTER TABLE doctors ADD COLUMN name VARCHAR(255)
        """)
        print("✓ Column added")
        
        # Populate from users table
        print("Populating doctor names from users table...")
        cursor.execute("""
            UPDATE doctors
            SET name = users.name
            FROM users
            WHERE doctors.user_id = users.id
        """)
        
        affected_rows = cursor.rowcount
        print(f"✓ Updated {affected_rows} doctor records with names")
        
        # Make column NOT NULL
        print("Setting name column to NOT NULL...")
        cursor.execute("""
            ALTER TABLE doctors ALTER COLUMN name SET NOT NULL
        """)
        print("✓ Column set to NOT NULL")
        
        # Create index
        print("Creating index on name column...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_doctors_name ON doctors(name)
        """)
        print("✓ Index created")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"✗ Database error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    success = add_name_column()
    exit(0 if success else 1)
