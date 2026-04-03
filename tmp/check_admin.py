from app import app
from models import User

with app.app_context():
    admin = User.query.filter_by(is_admin=True).first()
    if admin:
        print(f"Admin email: {admin.email}")
    else:
        print("No admin found")
