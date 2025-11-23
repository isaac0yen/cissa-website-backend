"""CLI command to create an admin user"""

import sys
import getpass
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.api.repositories.user import UserRepository
from app.api.models import User
from app.utils.password_utils import hash_password


def create_admin_command():
    """
    Create an admin user via command line.
    Usage: uv run python -m app.cli.create_admin
    """
    print("=== Create Admin User ===\n")

    # Get user input
    try:
        username = input("Enter username: ").strip()
        if not username:
            print("Error: Username cannot be empty")
            sys.exit(1)

        email = input("Enter email: ").strip()
        if not email:
            print("Error: Email cannot be empty")
            sys.exit(1)

        # Use getpass for secure password input (doesn't echo to terminal)
        password = getpass.getpass("Enter password: ")
        if not password:
            print("Error: Password cannot be empty")
            sys.exit(1)

        password_confirm = getpass.getpass("Confirm password: ")
        if password != password_confirm:
            print("Error: Passwords do not match")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(0)

    # Create database session
    db: Session = SessionLocal()

    try:
        # Initialize repository
        user_repo = UserRepository(db)

        # Check if username already exists
        existing_user = user_repo.get_by_username(username)
        if existing_user:
            print(f"Error: Username '{username}' already exists")
            sys.exit(1)

        # Check if email already exists
        existing_email = user_repo.get_by_email(email)
        if existing_email:
            print(f"Error: Email '{email}' already exists")
            sys.exit(1)

        # Hash the password
        hashed_password = hash_password(password)

        # Create admin user (NO StudentProfile)
        admin_user = User(
            username=username,
            email=email,
            password=hashed_password,
            role="admin",  # Set role to admin
        )

        # Use repository to create user
        created_user = user_repo.create(admin_user)

        print("\n✅ Admin user created successfully!")
        print(f"   ID: {created_user.id}")
        print(f"   Username: {created_user.username}")
        print(f"   Email: {created_user.email}")
        print(f"   Role: {created_user.role}")
        print(f"   Created: {created_user.created_at}")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error creating admin user: {str(e)}")
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    create_admin_command()
