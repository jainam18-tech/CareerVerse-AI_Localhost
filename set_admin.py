from app import app, db
from models import User
import sys

def promote_to_admin(email):
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"Error: User with email {email} not found.")
            return False
        
        user.is_admin = True
        db.session.commit()
        print(f"Success: {email} has been promoted to Admin.")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python set_admin.py <email>")
    else:
        promote_to_admin(sys.argv[1])
