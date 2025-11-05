"""
Initialize database and create superuser admin.
Run: python -m scripts.init_db
"""

import asyncio
import uuid
from datetime import datetime
from app.core.database import async_session, engine, Base
from app.models.users import User
from app.core.security import get_password_hash
from sqlalchemy import select

async def init_database():
    """Initialize database and create superuser"""
    
    print("🔄 Initializing database...")
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables created")
    
    async with async_session() as session:
        # Check if admin already exists
        result = await session.execute(
            select(User).where(User.email == 'admin@hireassist.com')
        )
        existing_admin = result.scalars().first()
        
        if existing_admin:
            print("✅ Superuser admin already exists")
            print(f"   Email: {existing_admin.email}")
            print(f"   Role: {existing_admin.role}")
            print(f"   Approved: {existing_admin.is_approved}")
            return
        
        # Create superuser admin
        admin_user = User(
            id=uuid.uuid4(),
            email='admin@hireassist.com',
            password_hash=get_password_hash('AdminPassword123!'),
            first_name='Admin',
            last_name='User',
            role='admin',
            is_approved=True,
            created_at=datetime.utcnow()
        )
        
        session.add(admin_user)
        await session.commit()
        
        print("\n✅ Superuser admin created successfully!")
        print("\n📋 Admin Credentials:")
        print("   Email: admin@hireassist.com")
        print("   Password: AdminPassword123!")
        print("\n⚠️  IMPORTANT: Change password after first login!")
        print("\n🎯 Next steps:")
        print("   1. Login with admin credentials")
        print("   2. Review pending user approvals")
        print("   3. Approve or reject candidates")

async def main():
    try:
        await init_database()
        print("\n✅ Database initialization complete!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
