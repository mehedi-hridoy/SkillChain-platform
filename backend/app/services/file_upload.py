import os
import shutil
from datetime import datetime
from fastapi import UploadFile
from typing import Optional
import uuid

UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {
    'image': {'.jpg', '.jpeg', '.png', '.gif', '.webp'},
    'document': {'.pdf', '.doc', '.docx', '.xls', '.xlsx'},
    'all': {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.pdf', '.doc', '.docx', '.xls', '.xlsx'}
}

class FileUploadService:
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        return os.path.splitext(filename)[1].lower()
    
    @staticmethod
    def validate_file(filename: str, allowed_types: str = 'all') -> bool:
        ext = FileUploadService.get_file_extension(filename)
        return ext in ALLOWED_EXTENSIONS.get(allowed_types, ALLOWED_EXTENSIONS['all'])
    
    @staticmethod
    async def save_file(file: UploadFile, category: str = 'compliance') -> dict:
        """
        Save uploaded file and return file info
        category: compliance, learning, certificates
        """
        if not FileUploadService.validate_file(file.filename):
            raise ValueError(f"File type not allowed: {file.filename}")
        
        # Create category directory if not exists
        category_dir = os.path.join(UPLOAD_DIR, category)
        os.makedirs(category_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        ext = FileUploadService.get_file_extension(file.filename)
        new_filename = f"{timestamp}_{unique_id}{ext}"
        
        file_path = os.path.join(category_dir, new_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Return file info
        return {
            "filename": new_filename,
            "original_filename": file.filename,
            "file_path": file_path,
            "url": f"/files/{category}/{new_filename}",
            "size": os.path.getsize(file_path),
            "content_type": file.content_type,
            "uploaded_at": datetime.now().isoformat()
        }
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """Delete file from storage"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
