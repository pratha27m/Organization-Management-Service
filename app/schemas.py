from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from bson import ObjectId

# Custom ObjectId field for MongoDB documents
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

# ============================================
#  Schema used for DB output (organization)
# ============================================
class OrganizationSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    organization_name: str
    collection_name: str
    admin_email: EmailStr
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            ObjectId: str
        }
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

# ============================================
#  Schema for Admin (DB representation)
# ============================================
class AdminSchema(BaseModel):
    email: EmailStr
    password: str  # hashed password stored in DB

# ============================================
#  JWT Token Response
# ============================================
class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    org_name: str
    admin_email: EmailStr
    collection_name: str
