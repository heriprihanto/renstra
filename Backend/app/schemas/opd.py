from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class DokumenItem(BaseModel):
    id: int
    id_ref_dokumen: int
    tahap: str  # "Rancangan", "Rancangan Akhir", "Penetapan"
    nama_file: str
    link_gd: Optional[str] = None
    file_url: Optional[str] = None
    uploaded_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SubPdItem(BaseModel):
    id_sub_skpd: int
    id_skpd: Optional[int] = None
    kode_sub_skpd: Optional[str] = None
    nama_sub_skpd: Optional[str] = None

    class Config:
        from_attributes = True


class SubPdDetail(BaseModel):
    id_sub_skpd: int
    id_skpd: Optional[int] = None
    kode_sub_skpd: Optional[str] = None
    nama_sub_skpd: Optional[str] = None
    opd: Optional[dict] = None

    class Config:
        from_attributes = True


class OpdAuditSummaryItem(BaseModel):
    id_dokumen: int
    tahap: str
    skor_kesesuaian: int
    status: str
    audited_at: Optional[str] = None
    source: Optional[str] = "ai"

    class Config:
        from_attributes = True


class OpdListItem(BaseModel):
    id_skpd: int
    kode_skpd: Optional[str] = None
    nama_skpd: Optional[str] = None
    sub_count: int = 0
    dokumen: List[DokumenItem] = []
    latest_audit: Optional[OpdAuditSummaryItem] = None

    class Config:
        from_attributes = True


class OpdDetail(BaseModel):
    id_skpd: int
    kode_skpd: Optional[str] = None
    nama_skpd: Optional[str] = None
    sub_count: int = 0
    sub_pd_list: List[SubPdItem] = []

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_opd: int
    total_sub_pd: int
    opd_with_sub: int
    opd_without_sub: int
    tahun_anggaran: int
    project_name: str
