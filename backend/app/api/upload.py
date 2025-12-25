from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.file_upload import FileUploadService
from typing import List

router = APIRouter(prefix="/upload", tags=["File Upload"])

@router.post("/compliance")
async def upload_compliance_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload compliance documents (certificates, test reports, photos, audits)
    Allowed: PDF, images, Office documents
    Requires: Authentication
    """
    try:
        file_info = await FileUploadService.save_file(file, category="compliance")
        return {
            "success": True,
            "message": "File uploaded successfully",
            "file": file_info
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="File upload failed")

@router.post("/learning")
async def upload_learning_content(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload learning content (images for articles, course materials, resources)
    Requires: Authentication (platform_admin or factory_admin)
    """
    if current_user.role not in ["platform_admin", "factory_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    try:
        file_info = await FileUploadService.save_file(file, category="learning")
        return {
            "success": True,
            "message": "File uploaded successfully",
            "file": file_info
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="File upload failed")

@router.post("/certificate")
async def upload_certificate(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload factory/product certificates (ISO, WRAP, GOTS, etc.)
    Requires: factory_admin or platform_admin
    """
    if current_user.role not in ["platform_admin", "factory_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    
    try:
        file_info = await FileUploadService.save_file(file, category="certificates")
        return {
            "success": True,
            "message": "Certificate uploaded successfully",
            "file": file_info
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="File upload failed")
