from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Check if is_verified column exists
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT FALSE"))
            conn.commit()
            print("Successfully added is_verified column to users table.")
    except Exception as e:
        if "Duplicate column name" in str(e):
            print("Column is_verified already exists.")
        else:
            print(f"Error updating database: {e}")
