
from backend.database.connection import SessionLocal
from backend.database.repositories import UserRepository

email = input("Enter your registered email: ").strip().lower()

db = SessionLocal()

try:
    user = UserRepository(db).get_by_email(email)

    if user is None:
        print("User not found.")
    else:
        user.role = "reviewer"
        db.commit()
        db.refresh(user)

        print("Reviewer role updated successfully.")
        print("Email:", user.email)
        print("Role:", user.role)

except Exception as exc:
    db.rollback()
    print("Update failed:", str(exc))

finally:
    db.close()
