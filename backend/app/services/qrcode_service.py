import qrcode
from io import BytesIO
import os
from PIL import Image

class QRCodeService:
    
    @staticmethod
    def generate_qr_code(data: str, logo_path: str = None) -> BytesIO:
        """
        Generate QR code image
        data: URL or text to encode
        logo_path: Optional logo to embed in center
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction for logo
            box_size=10,
            border=4,
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Add logo if provided
        if logo_path and os.path.exists(logo_path):
            logo = Image.open(logo_path)
            
            # Calculate logo size (should be ~1/5 of QR code)
            qr_width, qr_height = img.size
            logo_size = qr_width // 5
            
            # Resize logo
            logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
            
            # Calculate position (center)
            logo_pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
            
            # Paste logo
            img.paste(logo, logo_pos)
        
        # Save to BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return buffer
    
    @staticmethod
    def save_qr_code(data: str, filename: str, directory: str = "uploads/qrcodes") -> str:
        """
        Generate and save QR code to file
        Returns: relative path to saved file
        """
        os.makedirs(directory, exist_ok=True)
        
        qr_image = QRCodeService.generate_qr_code(data)
        
        file_path = os.path.join(directory, filename)
        with open(file_path, 'wb') as f:
            f.write(qr_image.getvalue())
        
        return file_path
