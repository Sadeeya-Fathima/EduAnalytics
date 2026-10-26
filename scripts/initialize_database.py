from getpass import getpass
# from uuid import uuid4

from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import Institution, User

def main():
    app = create_app()

    with app.app_context():
        print("EduAnalytics - Initial Database Setup")
        print("-------------------------------------")

        if User.query.filter_by(role="admin").first():
            print(
                "Initial setup is already complete: "
                "an Admin account exists."
            )
            print("No changes were made to the database.")
            return

        if User.query.first():
            print(
                "Initial setup cannot continue: "
                "existing user accounts were found."
            )
            print("No changes were made to the database.")
            return

        institution_name = input("Institution name: ").strip()
        if not institution_name:
            print("Error: Institution name cannot be empty.")
            return

        userid = input("Admin user ID: ").strip()

        if not userid:
            print("Error: User ID cannot be empty.")
            return

        if User.query.filter_by(userid=userid).first():
            print("This user ID already exists.")
            return

        admin_email = input("Admin email: ").strip().lower()
        if not admin_email:
            print("Error: Admin email cannot be empty.")
            return

        existing_user = User.query.filter_by(email=admin_email).first()
        if existing_user:
            print("An account with this email already exists.")
            return

        first_name = input("Admin first name: ").strip()
        last_name = input("Admin last name: ").strip()

        if not first_name or not last_name:
            print("Error: First name and last name are required.")
            return

        password = getpass("Admin password (hidden): ")
        confirm_password = getpass("Confirm admin password: ")

        if len(password) < 8:
            print("Error: Use a password with at least 8 characters.")
            return

        if password != confirm_password:
            print("Error: Passwords do not match.")
            return

        institution = Institution.query.filter_by(
            name=institution_name
        ).first()

        if institution is None:
            institution = Institution(name=institution_name)
            db.session.add(institution)
            db.session.flush()

        admin = User(
            userid=userid,
            email=admin_email,
            institution_id=institution.id,
            first_name=first_name,
            last_name=last_name,
            title="Administrator",
            role="admin",
            status="active",
            password=generate_password_hash(password),
        )

        try:
            db.session.add(admin)
            db.session.commit()
            print("\nSetup completed successfully.")
            print(f"Institution: {institution.name}")
            print(f"Admin email: {admin.email}")
            print(f"Admin user ID: {admin.userid}")
            print("Password stored as a hash.")
        except Exception:
            db.session.rollback()
            print("Setup failed. No changes from this transaction were saved.")
            raise

if __name__ == "__main__":
    main()
