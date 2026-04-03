import os
from dotenv import load_dotenv
import pymysql
try:
    from sqlalchemy import create_engine
    from sqlalchemy.engine.url import make_url
except ImportError:
    print("ERROR: SQLAlchemy not found. Please run 'pip install flask-sqlalchemy'")
    exit(1)

load_dotenv()
db_url = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost/careerverse")

print("="*50)
print("CAREERVERSE DATABASE DIAGNOSTIC")
print("="*50)
print(f"Testing connection to: {db_url}")

try:
    url = make_url(db_url)
    
    # 1. Test raw pymysql connection to MySQL server
    print("\n[1/3] Testing raw pymysql connection to MySQL server...")
    try:
        conn = pymysql.connect(
            host=url.host or 'localhost',
            user=url.username or 'root',
            password=url.password or '',
            connect_timeout=5
        )
        print("✅ SUCCESS: Connected to MySQL server.")
        
        # 2. Check if DB exists
        print(f"\n[2/3] Checking if database '{url.database}' exists...")
        cursor = conn.cursor()
        cursor.execute(f"SHOW DATABASES LIKE '{url.database}'")
        result = cursor.fetchone()
        if result:
            print(f"✅ SUCCESS: Database '{url.database}' exists.")
        else:
            print(f"❌ WARNING: Database '{url.database}' does NOT exist.")
            print(f"   (The app will try to create it automatically if you have privileges)")
        conn.close()
    except Exception as e:
        print(f"❌ FAILURE: Could not connect to MySQL server: {e}")
        print("   Is MySQL running? Are your credentials correct in .env?")

    # 3. Test SQLAlchemy engine
    print("\n[3/3] Testing SQLAlchemy connection to the database...")
    try:
        engine = create_engine(db_url)
        with engine.connect() as connection:
            print("✅ SUCCESS: SQLAlchemy connected successfully.")
    except Exception as e:
        print(f"❌ FAILURE: SQLAlchemy connection failed: {e}")

except Exception as e:
    print(f"\n❌ CRITICAL ERROR: {e}")

print("\n" + "="*50)
print("DIAGNOSTIC COMPLETE")
print("="*50)
