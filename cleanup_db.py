import os
from app import app
from models import db
import shutil

def reset_database():
    with app.app_context():
        print("DEBUG: Connecting to database...")
        try:
            # Drop all tables in reverse order of dependencies
            print("DEBUG: Dropping all existing tables...")
            db.drop_all()
            
            # Recreate all tables
            print("DEBUG: Recreating database schema...")
            db.create_all()
            
            print("DEBUG: Database tables reset successfully.")
            
            # Optional: Clear reports and uploads if they exist
            data_dir = os.path.join(os.path.dirname(__file__), "data")
            if os.path.exists(data_dir):
                print(f"DEBUG: Cleaning filesystem data in {data_dir}...")
                for item in os.listdir(data_dir):
                    item_path = os.path.join(data_dir, item)
                    if os.path.isdir(item_path):
                        # Keep the directory structure but delete contents
                        for subitem in os.listdir(item_path):
                            subitem_path = os.path.join(item_path, subitem)
                            if os.path.isfile(subitem_path):
                                os.remove(subitem_path)
                            elif os.path.isdir(subitem_path):
                                shutil.rmtree(subitem_path)
                print("DEBUG: Filesystem data cleared.")
            
            print("\n" + "="*40)
            print("SUCCESS: Your local CareerVerse environment has been reset!")
            print("You can now start fresh by registering a new account.")
            print("="*40)
            
        except Exception as e:
            print(f"ERROR during reset: {e}")

if __name__ == "__main__":
    confirm = input("Are you sure you want to delete ALL data? (y/n): ")
    if confirm.lower() == 'y':
        reset_database()
    else:
        print("Reset cancelled.")
