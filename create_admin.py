import sys
from app import app, db
from models import User

def promote_to_admin(email):
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if user:
            user.is_admin = True
            db.session.commit()
            print(f"User {email} promoted to admin successfully.")
        else:
            print(f"User with email {email} not found.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_admin.py <email>")
    else:
        promote_to_admin(sys.argv[1])
