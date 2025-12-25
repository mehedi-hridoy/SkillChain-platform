from fastapi import APIRouter
from app.services.qr import generate_qr
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/qr", tags=["QR"])

@router.get("/batch/{batch_id}")
def get_batch_qr(batch_id: int):
    dpp_url = f"https://api.yourdomain.com/public/dpp/batch/{batch_id}"
    img = generate_qr(dpp_url)
    return StreamingResponse(img, media_type="image/png")
