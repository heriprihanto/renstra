import re
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import get_session
from app.models.opd import TaOpd
from app.services.laporan_service import (
    generate_evaluasi_renstra_excel,
    generate_iku_excel,
    generate_program_kegiatan_excel,
    generate_tujuan_sasaran_excel,
    get_evaluasi_renstra_report_data,
    get_iku_report_data,
    get_program_kegiatan_report_data,
    get_tujuan_sasaran_report_data,
)

router = APIRouter(prefix="/laporan", tags=["Laporan"])


@router.get("/opd-list", response_model=List[Dict[str, Any]])
async def get_opd_list_for_report(session: AsyncSession = Depends(get_session)):
    """Get list of active OPDs for report selector."""
    stmt = select(TaOpd).order_by(TaOpd.kode_skpd)
    result = await session.exec(stmt)
    opds = result.all()
    return [
        {
            "id_skpd": o.id_skpd,
            "kode_skpd": o.kode_skpd,
            "nama_skpd": o.nama_skpd,
        }
        for o in opds
    ]


@router.get("/tujuan-sasaran/{id_skpd}", response_model=Dict[str, Any])
async def get_tujuan_sasaran_preview(
    id_skpd: int,
    tipe: str = Query(default="murni", description="Tipe target: 'murni' atau 'perubahan'"),
    session: AsyncSession = Depends(get_session),
):
    """Get Tujuan & Sasaran structured report preview data."""
    try:
        data = await get_tujuan_sasaran_report_data(session, id_skpd, tipe=tipe)
        return data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memuat data laporan: {str(e)}")


@router.get("/tujuan-sasaran/{id_skpd}/export-excel")
async def export_tujuan_sasaran_excel(
    id_skpd: int,
    tipe: str = Query(default="murni", description="Tipe target: 'murni' atau 'perubahan'"),
    session: AsyncSession = Depends(get_session),
):
    """Download Tabel 3.1 Tujuan dan Sasaran formatted Excel file."""
    try:
        data = await get_tujuan_sasaran_report_data(session, id_skpd, tipe=tipe)
        excel_buf = generate_tujuan_sasaran_excel(data)

        nama_skpd = data.get("opd", {}).get("nama_skpd", f"OPD_{id_skpd}")
        clean_nama = re.sub(r"[^\w\s-]", "", nama_skpd).strip().replace(" ", "_")
        filename = f"Tabel_3.1_Tujuan_dan_Sasaran_{clean_nama}.xlsx"

        return Response(
            content=excel_buf.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Access-Control-Expose-Headers": "Content-Disposition",
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal generate Excel: {str(e)}")


@router.get("/iku/{id_skpd}", response_model=Dict[str, Any])
async def get_iku_preview(
    id_skpd: int,
    tipe: str = Query(default="murni", description="Tipe target: 'murni' atau 'perubahan'"),
    session: AsyncSession = Depends(get_session),
):
    """Get Indikator Kinerja Utama (IKU) structured report preview data."""
    try:
        data = await get_iku_report_data(session, id_skpd, tipe=tipe)
        return data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memuat data laporan IKU: {str(e)}")


@router.get("/iku/{id_skpd}/export-excel")
async def export_iku_excel(
    id_skpd: int,
    tipe: str = Query(default="murni", description="Tipe target: 'murni' atau 'perubahan'"),
    session: AsyncSession = Depends(get_session),
):
    """Download Indikator Kinerja Utama (IKU) formatted Excel file."""
    try:
        data = await get_iku_report_data(session, id_skpd, tipe=tipe)
        excel_buf = generate_iku_excel(data)

        nama_skpd = data.get("opd", {}).get("nama_skpd", f"OPD_{id_skpd}")
        clean_nama = re.sub(r"[^\w\s-]", "", nama_skpd).strip().replace(" ", "_")
        filename = f"IKU_{clean_nama}.xlsx"

        return Response(
            content=excel_buf.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Access-Control-Expose-Headers": "Content-Disposition",
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal generate Excel IKU: {str(e)}")


@router.get("/program-kegiatan/{id_skpd}", response_model=Dict[str, Any])
async def get_program_kegiatan_preview(
    id_skpd: int,
    id_sub_skpd: Optional[int] = Query(default=None, description="Filter id_sub_skpd unit"),
    tipe: str = Query(default="murni", description="Tipe target: 'murni' atau 'perubahan'"),
    session: AsyncSession = Depends(get_session),
):
    """Get Tabel 4.1 Program, Kegiatan, Sub Kegiatan dan Pendanaan structured report preview data."""
    try:
        data = await get_program_kegiatan_report_data(
            session, id_skpd, id_sub_skpd=id_sub_skpd, tipe=tipe
        )
        return data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memuat data laporan Program Kegiatan: {str(e)}")


@router.get("/program-kegiatan/{id_skpd}/export-excel")
async def export_program_kegiatan_excel(
    id_skpd: int,
    id_sub_skpd: Optional[int] = Query(default=None, description="Filter id_sub_skpd unit"),
    tipe: str = Query(default="murni", description="Tipe target: 'murni' atau 'perubahan'"),
    session: AsyncSession = Depends(get_session),
):
    """Download Tabel 4.1 Program, Kegiatan, Sub Kegiatan dan Pendanaan formatted Excel file."""
    try:
        data = await get_program_kegiatan_report_data(
            session, id_skpd, id_sub_skpd=id_sub_skpd, tipe=tipe
        )
        excel_buf = generate_program_kegiatan_excel(data)

        nama_skpd = data.get("opd", {}).get("nama_skpd", f"OPD_{id_skpd}")
        clean_nama = re.sub(r"[^\w\s-]", "", nama_skpd).strip().replace(" ", "_")
        filename = f"Tabel_4.1_Program_Kegiatan_{clean_nama}.xlsx"

        return Response(
            content=excel_buf.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Access-Control-Expose-Headers": "Content-Disposition",
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal generate Excel Program Kegiatan: {str(e)}")


@router.get("/evaluasi-renstra/{id_skpd}", response_model=Dict[str, Any])
async def get_evaluasi_renstra_preview(
    id_skpd: int,
    id_sub_skpd: Optional[int] = Query(default=None, description="Filter id_sub_skpd unit"),
    tipe: str = Query(default="murni", description="Tipe target: 'murni' atau 'perubahan'"),
    session: AsyncSession = Depends(get_session),
):
    """Get Laporan Evaluasi Hasil Renstra structured report preview data (Permendagri 86/2017)."""
    try:
        data = await get_evaluasi_renstra_report_data(
            session, id_skpd, id_sub_skpd=id_sub_skpd, tipe=tipe
        )
        return data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memuat data evaluasi renstra: {str(e)}")


@router.get("/evaluasi-renstra/{id_skpd}/export-excel")
async def export_evaluasi_renstra_excel(
    id_skpd: int,
    id_sub_skpd: Optional[int] = Query(default=None, description="Filter id_sub_skpd unit"),
    tipe: str = Query(default="murni", description="Tipe target: 'murni' atau 'perubahan'"),
    session: AsyncSession = Depends(get_session),
):
    """Download Laporan Evaluasi Hasil Renstra formatted Excel file (38 Columns Permendagri 86/2017)."""
    try:
        data = await get_evaluasi_renstra_report_data(
            session, id_skpd, id_sub_skpd=id_sub_skpd, tipe=tipe
        )
        excel_buf = generate_evaluasi_renstra_excel(data)

        nama_skpd = data.get("opd", {}).get("nama_skpd", f"OPD_{id_skpd}")
        clean_nama = re.sub(r"[^\w\s-]", "", nama_skpd).strip().replace(" ", "_")
        filename = f"Evaluasi_Hasil_Renstra_{clean_nama}.xlsx"

        return Response(
            content=excel_buf.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Access-Control-Expose-Headers": "Content-Disposition",
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal generate Excel Evaluasi Renstra: {str(e)}")


