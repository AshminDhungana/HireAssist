from fastapi import APIRouter, HTTPException, status, Header, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.users import User
from app.core.security import decode_token
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


def extract_admin_user(authorization: str) -> uuid.UUID:
    """Extract and verify admin user from token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    try:
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise ValueError("Invalid format")
        token = parts[1]
    except (ValueError, IndexError):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    try:
        return uuid.UUID(user_id) if isinstance(user_id, str) else user_id
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid user ID format")


async def verify_admin_access(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Verify that user is admin. Returns admin user object."""
    admin_id = extract_admin_user(authorization)
    
    result = await db.execute(select(User).where(User.id == admin_id))
    admin_user = result.scalars().first()
    
    if not admin_user:
        raise HTTPException(status_code=404, detail="Admin user not found")
    
    if not admin_user.is_admin():  # ← Use the helper method
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return admin_user


@router.get("/pending-users")
async def get_pending_users(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """Get list of pending user approvals (Admin only)"""
    admin_user = await verify_admin_access(authorization, db)
    
    # Get all non-approved users (excluding admins)
    result = await db.execute(
        select(User)
        .where(User.is_approved == False)
        .where(User.role != 'admin')
        .order_by(User.created_at.desc())
    )
    pending_users = result.scalars().all()
    
    logger.info(f"Admin {admin_user.email} retrieved pending users list")
    
    return {
        "success": True,
        "pending_users": [
            {
                "id": str(u.id),
                "email": u.email,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "role": u.role,
                "created_at": u.created_at.isoformat() if u.created_at else None
            }
            for u in pending_users
        ],
        "total": len(pending_users)
    }


@router.post("/approve-user/{user_id}")
async def approve_user(
    user_id: str,
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """Approve a pending user (Admin only)"""
    admin_user = await verify_admin_access(authorization, db)
    
    # Validate UUID format
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    # Get user to approve
    result = await db.execute(select(User).where(User.id == uid))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already approved
    if user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already approved"
        )
    
    # Approve user
    user.is_approved = True
    user.approved_at = datetime.utcnow()  # ← Set approval timestamp
    db.add(user)
    await db.commit()
    
    logger.info(f"User {user.email} approved by admin {admin_user.email}")
    
    return {
        "success": True,
        "message": "User approved successfully",
        "user_id": str(user.id),
        "email": user.email,
        "approved_at": user.approved_at.isoformat() if user.approved_at else None
    }


@router.post("/reject-user/{user_id}")
async def reject_user(
    user_id: str,
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """Reject and delete a pending user (Admin only)"""
    admin_user = await verify_admin_access(authorization, db)
    
    # Validate UUID format
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    # Get user to reject
    result = await db.execute(select(User).where(User.id == uid))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Don't allow rejecting admins
    if user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot reject admin users"
        )
    
    # Store email before deletion for logging
    email = user.email
    
    # Delete user
    await db.delete(user)
    await db.commit()
    
    logger.info(f"User {email} rejected by admin {admin_user.email}")
    
    return {
        "success": True,
        "message": "User rejected and deleted successfully",
        "email": email
    }


@router.get("/stats")
async def get_admin_stats(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """Get admin dashboard statistics"""
    admin_user = await verify_admin_access(authorization, db)
    
    # Total users
    result_total = await db.execute(select(User))
    total_users = len(result_total.scalars().all())
    
    # Pending approvals
    result_pending = await db.execute(
        select(User).where(User.is_approved == False).where(User.role != 'admin')
    )
    pending_count = len(result_pending.scalars().all())
    
    # Approved users
    result_approved = await db.execute(
        select(User).where(User.is_approved == True).where(User.role == 'candidate')
    )
    approved_count = len(result_approved.scalars().all())
    
    # Users by role
    result_candidates = await db.execute(
        select(User).where(User.role == 'candidate')
    )
    candidates_count = len(result_candidates.scalars().all())
    
    result_recruiters = await db.execute(
        select(User).where(User.role == 'recruiter')
    )
    recruiters_count = len(result_recruiters.scalars().all())
    
    logger.info(f"Admin {admin_user.email} accessed dashboard stats")
    
    return {
        "success": True,
        "stats": {
            "total_users": total_users,
            "pending_approvals": pending_count,
            "approved_candidates": approved_count,
            "candidates": candidates_count,
            "recruiters": recruiters_count,
            "admins": total_users - candidates_count - recruiters_count
        }
    }
