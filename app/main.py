from fastapi import FastAPI, HTTPException, Depends, Header
from .models import OrgCreate, OrgUpdate, AdminLogin
from .crud import create_organization, get_org, update_org, delete_org, admin_login
from .auth import decode_token
from fastapi.responses import JSONResponse

app = FastAPI(title="Organization Management Service")

@app.post("/org/create")
async def api_create_org(payload: OrgCreate):
    try:
        org = await create_organization(payload.organization_name, payload.email, payload.password)
        return {
            "message": "Organization created",
            "organization_name": org["organization_name"],
            "collection_name": org["collection_name"],
            "admin_email": org["admin"]["email"],
            "created_at": org["created_at"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/org/get")
async def api_get_org(organization_name: str):
    doc = await get_org(organization_name)
    if not doc:
        raise HTTPException(status_code=404, detail="Organization not found")
    return {
        "organization_name": doc["organization_name"],
        "collection_name": doc["collection_name"],
        "admin_email": doc["admin"]["email"],
        "created_at": doc.get("created_at")
    }

@app.put("/org/update")
async def api_update_org(payload: OrgUpdate):
    try:
        updated = await update_org(
            payload.existing_name,
            payload.new_name,
            payload.email,
            payload.password
        )
        return {
            "message": "Organization updated",
            "organization": {
                "organization_name": updated["organization_name"],
                "collection_name": updated["collection_name"]
            }
        }
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def get_current_admin(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth scheme")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload

@app.delete("/org/delete")
async def api_delete_org(organization_name: str, admin=Depends(get_current_admin)):
    try:
        # ensure admin belongs to the org
        if admin.get("org_name") != organization_name:
            raise HTTPException(status_code=403, detail="Not authorized for this org")
        await delete_org(organization_name, admin.get("admin_email"))
        return JSONResponse({"message": "Organization deleted"})
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.post("/admin/login")
async def api_admin_login(payload: AdminLogin):
    res = await admin_login(payload.email, payload.password)
    if not res:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return res
