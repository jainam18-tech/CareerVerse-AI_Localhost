from app import app, db
from models import User, LoginHistory, ChatHistory, UserPerformance

with app.app_context():
    try:
        # Delete children first (foreign key constraints)
        print("Cleaning up LoginHistory...")
        db.session.query(LoginHistory).delete()
        
        print("Cleaning up ChatHistory...")
        db.session.query(ChatHistory).delete()
        
        print("Cleaning up UserPerformance...")
        db.session.query(UserPerformance).delete()
        
        # Delete parents last
        print("Cleaning up Users...")
        db.session.query(User).delete()
        
        db.session.commit()
        print("Successfully deleted all user information from the database.")
    except Exception as e:
        db.session.rollback()
        print(f"Error clearing database: {e}")
