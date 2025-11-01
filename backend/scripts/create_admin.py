"""
Script to create superuser admin account.
Run: python -m scripts.create_admin
"""

import asyncio
import uuid
from datetime import datetime
from app.core.database import async_session, engine, Base
from app.models.users import User
from app.core.security import hash_password
from sqlalchemy import select

async def create_admin():
    """Create superuser admin if it doesn't exist"""
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session() as session:
        # Check if admin already exists
        result = await session.execute(
            select(User).where(User.email == 'admin@hireassist.com')
        )
        existing_admin = result.scalars().first()
        
        if existing_admin:
            print("✅ Admin already exists!")
            print(f"   Email: {existing_admin.email}")
            print(f"   Role: {existing_admin.role}")
            return
        
        # Create admin user
        admin_user = User(
            id=uuid.uuid4(),
            email='admin@hireassist.com',
            password_hash=hash_password('AdminPassword123!'),
            first_name='Admin',
            last_name='User',
            role='admin',
            is_approved=True,  # Admin is auto-approved
            created_at=datetime.utcnow()
        )
        
        session.add(admin_user)
        await session.commit()
        
        print("✅ Superuser admin created successfully!")
        print("\n📋 Admin Credentials:")
        print("   Email: admin@hireassist.com")
        print("   Password: AdminPassword123!")
        print("\n⚠️  IMPORTANT: Change this password after first login!")

async def main():
    try:
        await create_admin()
    except Exception as e:
        print(f"❌ Error creating admin: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
