from app import app
from models import db, User, LoginHistory, ChatHistory, UserPerformance

def cleanup_unverified():
    with app.app_context():
        print("DEBUG: Fetching unverified users...")
        try:
            # Drop all records belonging to unverified users first
            unverified_users = User.query.filter_by(is_verified=False).all()
            if not unverified_users:
                print("DEBUG: No unverified users found.")
                return

            print(f"DEBUG: Found {len(unverified_users)} unverified users.")
            unverified_user_ids = [user.id for user in unverified_users]
            
            # Use synchronize_session=False for performance and to avoid session issues
            # We must delete children first to satisfy foreign key constraints
            print("DEBUG: Deleting related data for unverified users...")
            LoginHistory.query.filter(LoginHistory.user_id.in_(unverified_user_ids)).delete(synchronize_session=False)
            ChatHistory.query.filter(ChatHistory.user_id.in_(unverified_user_ids)).delete(synchronize_session=False)
            UserPerformance.query.filter(UserPerformance.user_id.in_(unverified_user_ids)).delete(synchronize_session=False)
            
            # Delete the users
            print("DEBUG: Deleting unverified users from 'users' table...")
            User.query.filter_by(is_verified=False).delete(synchronize_session=False)
            
            db.session.commit()
            print(f"SUCCESS: {len(unverified_users)} unverified users and their associated data have been permanently removed.")
        except Exception as e:
            db.session.rollback()
            print(f"ERROR: An error occurred during database cleanup: {e}")

if __name__ == "__main__":
    cleanup_unverified()
