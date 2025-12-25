import qrcode
from io import BytesIO
from fastapi.responses import StreamingResponse

def generate_qr(url: str):
    img = qrcode.make(url)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer
