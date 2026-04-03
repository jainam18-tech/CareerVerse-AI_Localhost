from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        with db.engine.connect() as conn:
            # Add is_hidden to chat_history
            try:
                conn.execute(text("ALTER TABLE chat_history ADD COLUMN is_hidden BOOLEAN DEFAULT FALSE"))
                print("Successfully added is_hidden to chat_history.")
            except Exception as e:
                print(f"Note: chat_history update: {e}")

            # Add is_hidden to user_performance
            try:
                conn.execute(text("ALTER TABLE user_performance ADD COLUMN is_hidden BOOLEAN DEFAULT FALSE"))
                print("Successfully added is_hidden to user_performance.")
            except Exception as e:
                print(f"Note: user_performance update: {e}")
            
            conn.commit()
            print("Database migration complete.")
    except Exception as e:
        print(f"Critical error updating database: {e}")
