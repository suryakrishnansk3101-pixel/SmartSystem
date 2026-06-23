from app.database import SessionLocal
from app.models import User
from app.auth import hash_password
db = SessionLocal()

admin = User(
    name="Super Admin",
    email="admin@smartdesk.com",
    password=hash_password("admin123"),
    role="admin"

)

db.add(admin)
db.commit()

print("Super Admin Created Successfully!")