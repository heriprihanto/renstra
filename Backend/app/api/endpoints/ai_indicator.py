from fastapi import APIRouter, HTTPException

from app.schemas.ai import (
    SmartRecommendationRequest,
    SmartRecommendationResponse,
)
from app.services.smart_indicator_ai import generate_smart_recommendations

router = APIRouter(prefix="/ai", tags=["AI Assistant Indikator SMART"])


@router.post("/smart-indicator-recommendation", response_model=SmartRecommendationResponse)
async def get_smart_indicator_recommendations(req: SmartRecommendationRequest):
    """
    Menghasilkan rekomendasi indikator kinerja SMART (Specific, Measurable,
    Achievable, Relevant, Time-Bound) berdasarkan inputan Tujuan, Sasaran, Program,
    Kegiatan (memperhatikan subkegiatan di bawahnya), atau Subkegiatan.
    Menggunakan OpenAI API dengan integrasi kunci API dari .env.
    """
    if not req.get_uraian():
        raise HTTPException(
            status_code=400,
            detail="Uraian entitas (Tujuan/Sasaran/Program/Kegiatan/Subkegiatan) tidak boleh kosong."
        )

    try:
        response = await generate_smart_recommendations(req)
        return response
    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail=f"Terjadi kesalahan saat memproses rekomendasi AI: {str(err)}"
        )
