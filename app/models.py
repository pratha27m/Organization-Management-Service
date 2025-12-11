from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class OrgCreate(BaseModel):
    organization_name: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=6)

class OrgUpdate(BaseModel):
    existing_name: str = Field(..., min_length=3)
    new_name: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=6)

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class OrgOut(BaseModel):
    organization_name: str
    collection_name: str
    admin_email: EmailStr
    created_at: datetime
