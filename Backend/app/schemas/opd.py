from typing import List, Optional
from pydantic import BaseModel


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


class OpdListItem(BaseModel):
    id_skpd: int
    kode_skpd: Optional[str] = None
    nama_skpd: Optional[str] = None
    sub_count: int = 0

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
