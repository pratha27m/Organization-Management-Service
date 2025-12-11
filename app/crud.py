from .db import master_db, tenant_db
from .auth import hash_password, verify_password, create_access_token
from datetime import datetime, timedelta
from .config import settings
from bson.objectid import ObjectId

ORGS = master_db["organizations"]  # master collection for org metadata

async def org_exists(org_name: str) -> bool:
    return await ORGS.count_documents({"organization_name": org_name}) > 0

async def create_organization(org_name: str, admin_email: str, admin_password: str):
    if await org_exists(org_name):
        raise ValueError("Organization already exists")
    collection_name = f"org_{org_name.lower().replace(' ', '_')}"
    # create dynamic collection (empty) in tenant_db
    await tenant_db.create_collection(collection_name) if collection_name not in await tenant_db.list_collection_names() else None

    # create admin user record inside master ORGS meta
    admin_hashed = hash_password(admin_password)
    org_doc = {
        "organization_name": org_name,
        "collection_name": collection_name,
        "connection": {"db": tenant_db.name},
        "admin": {
            "email": admin_email,
            "password": admin_hashed
        },
        "created_at": datetime.utcnow()
    }
    res = await ORGS.insert_one(org_doc)
    org_doc["_id"] = res.inserted_id
    return org_doc

async def get_org(org_name: str):
    doc = await ORGS.find_one({"organization_name": org_name})
    return doc


async def update_org(existing_name: str, new_name: str, admin_email: str, admin_password: str):
    doc = await get_org(existing_name)
    if not doc:
        raise LookupError("Organization not found")

    # If new name exists AND is different
    if new_name != existing_name and await org_exists(new_name):
        raise ValueError("New organization name already exists")

    old_collection = doc["collection_name"]
    new_collection = f"org_{new_name.lower().replace(' ', '_')}"

    # Rename logic only if name changed
    if old_collection != new_collection:
        old_col = tenant_db[old_collection]
        new_col = tenant_db[new_collection]

        # Copy all data
        async for doc_item in old_col.find({}):
            await new_col.insert_one(doc_item)

        # Drop old collection
        await old_col.drop()

    # Update admin + organization metadata
    admin_hashed = hash_password(admin_password)
    update_query = {
        "$set": {
            "organization_name": new_name,
            "collection_name": new_collection,
            "admin": {"email": admin_email, "password": admin_hashed},
            "updated_at": datetime.utcnow()
        }
    }

    await ORGS.update_one({"_id": doc["_id"]}, update_query)
    return await get_org(new_name)

async def delete_org(org_name: str, requesting_admin_email: str):
    doc = await get_org(org_name)
    if not doc:
        raise LookupError("Organization not found")
    # check admin
    if doc["admin"]["email"] != requesting_admin_email:
        raise PermissionError("Only the org admin can delete this organization")
    # drop collection
    col_name = doc["collection_name"]
    if col_name in await tenant_db.list_collection_names():
        await tenant_db[col_name].drop()
    # remove metadata
    await ORGS.delete_one({"_id": doc["_id"]})
    return True

async def admin_login(email: str, password: str):
    doc = await ORGS.find_one({"admin.email": email})
    if not doc:
        return None
    hashed = doc["admin"]["password"]
    if not verify_password(password, hashed):
        return None
    payload = {
        "admin_email": email,
        "org_name": doc["organization_name"],
        "collection_name": doc["collection_name"],
        "admin_id": str(doc["_id"])
    }
    token = create_access_token(payload)
    return {"access_token": token, "token_type": "bearer", "org": payload}
