import os
from app import app
from models import db
import shutil

def reset_database():
    with app.app_context():
        print("DEBUG: Connecting to database for force reset...")
        try:
            # Drop all tables
            print("DEBUG: Dropping all existing tables...")
            db.drop_all()
            
            # Recreate all tables
            print("DEBUG: Recreating database schema...")
            db.create_all()
            
            print("DEBUG: Database tables reset successfully.")
            
            # Clear reports and uploads
            data_dir = os.path.join(os.path.dirname(__file__), "data")
            if os.path.exists(data_dir):
                print(f"DEBUG: Cleaning filesystem data in {data_dir}...")
                for item in os.listdir(data_dir):
                    item_path = os.path.join(data_dir, item)
                    if os.path.isdir(item_path):
                        for subitem in os.listdir(item_path):
                            subitem_path = os.path.join(item_path, subitem)
                            if os.path.isfile(subitem_path):
                                os.remove(subitem_path)
                            elif os.path.isdir(subitem_path):
                                shutil.rmtree(subitem_path)
                print("DEBUG: Filesystem data cleared.")
            
            print("SUCCESS: Database and filesystem reset.")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    reset_database()
