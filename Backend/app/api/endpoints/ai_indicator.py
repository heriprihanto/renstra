from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import get_session
from app.schemas.ai import (
    DokumenAuditResponse,
    SmartRecommendationRequest,
    SmartRecommendationResponse,
)
from app.services.dokumen_ai_audit import execute_dokumen_audit, get_saved_audit_from_db
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


@router.get("/audit-dokumen-perencanaan/{id_skpd}", response_model=Optional[DokumenAuditResponse])
async def get_saved_audit_dokumen(
    id_skpd: int,
    id_dokumen: Optional[int] = Query(default=None, description="Opsional: ID dokumen spesifik (65/66)"),
    session: AsyncSession = Depends(get_session),
):
    """
    Mengambil hasil audit kesesuaian dokumen yang tersimpan di database jika ada.
    """
    return await get_saved_audit_from_db(session, id_skpd=id_skpd, id_dokumen=id_dokumen)


@router.post("/audit-dokumen-perencanaan/{id_skpd}", response_model=DokumenAuditResponse)
async def audit_dokumen_perencanaan_opd(
    id_skpd: int,
    id_dokumen: Optional[int] = Query(default=None, description="Opsional: ID dokumen spesifik (65/66)"),
    force_reanalyze: bool = Query(default=False, description="Paksa analisa ulang dengan AI"),
    session: AsyncSession = Depends(get_session),
):
    """
    Menganalisa kesesuaian dokumen perencanaan (Penetapan jika ada, atau Rancangan Akhir)
    terhadap data database resmi aplikasi dengan bantuan AI.
    Hasil audit disimpan otomatis ke database dan pengguna dapat menjalankan analisa ulang kapan saja.
    """
    try:
        # Jika tidak dipaksa analisa ulang, periksa apakah sudah ada hasil audit tersimpan di database
        if not force_reanalyze:
            saved = await get_saved_audit_from_db(session, id_skpd=id_skpd, id_dokumen=id_dokumen)
            if saved:
                return saved

        # Jalankan analisa audit AI baru dan otomatis simpan ke database
        response = await execute_dokumen_audit(session, id_skpd=id_skpd, id_dokumen=id_dokumen)
        return response
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail=f"Terjadi kesalahan saat memproses audit dokumen AI: {str(err)}"
        )

