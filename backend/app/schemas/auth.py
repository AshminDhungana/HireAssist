from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID


class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    role: str = Field(default="candidate", description="User role: admin, recruiter, or candidate")
    
    class Config:
        example = {
            "email": "john@example.com",
            "password": "SecurePass123!",
            "first_name": "John",
            "last_name": "Doe",
            "role": "candidate"
        }


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str
    
    class Config:
        example = {
            "email": "john@example.com",
            "password": "SecurePass123!"
        }


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str = "bearer"
    
    class Config:
        example = {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }


class UserResponse(UserBase):
    """Schema for user response (without password)"""
    id: UUID
    role: str
    is_active: bool
    is_verified: bool
    
    class Config:
        from_attributes = True
        example = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "role": "candidate",
            "is_active": True,
            "is_verified": False
        }


class LoginResponse(BaseModel):
    """Complete login response with user info and token"""
    user: UserResponse
    access_token: str
    token_type: str = "bearer"
    
    class Config:
        example = {
            "user": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "role": "candidate",
                "is_active": True,
                "is_verified": False
            },
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
