from datetime import datetime
from typing import Any, Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB


class DokumenPerencanaan(SQLModel, table=True):
    __tablename__ = "dokumen_perencanaan"

    id: Optional[int] = Field(default=None, primary_key=True)
    id_ref_dokumen: int = Field(index=True)
    id_sub_pd: int = Field(index=True)
    nama_file: str
    file_id_gd: Optional[str] = Field(default=None)
    link_gd: Optional[str] = Field(default=None)
    uploaded_by: Optional[int] = Field(default=None)
    uploaded_at: Optional[datetime] = Field(default=None)


class RenstraDokumenAudit(SQLModel, table=True):
    __tablename__ = "renstra_dokumen_audit"

    id: Optional[int] = Field(default=None, primary_key=True)
    id_skpd: int = Field(index=True)
    kode_skpd: Optional[str] = None
    nama_skpd: Optional[str] = None
    id_dokumen: int = Field(index=True)
    id_ref_dokumen: int
    tahap: str
    nama_file: str
    file_url: Optional[str] = None
    uploaded_at: Optional[str] = None
    source: Optional[str] = "ai"
    skor_kesesuaian: int = 100
    status: str = "Sesuai"
    ringkasan_analisis: Optional[str] = None
    total_pages: int = 0
    analyzed_pages: int = 0
    total_program_db: int = 0
    total_program_cocok: int = 0
    total_program_selisih: int = 0
    total_kegiatan_db: int = 0
    total_kegiatan_cocok: int = 0
    total_subkegiatan_db: int = 0
    total_subkegiatan_cocok: int = 0
    total_tujuan_db: int = 0
    total_sasaran_db: int = 0
    total_iku_db: int = 0
    audit_tujuan_sasaran: Optional[Any] = Field(default=None, sa_column=Column(JSONB))
    audit_pagu: Optional[Any] = Field(default=None, sa_column=Column(JSONB))
    audit_indikator: Optional[Any] = Field(default=None, sa_column=Column(JSONB))
    audit_kegiatan: Optional[Any] = Field(default=None, sa_column=Column(JSONB))
    audit_subkegiatan: Optional[Any] = Field(default=None, sa_column=Column(JSONB))
    audit_nomenklatur: Optional[Any] = Field(default=None, sa_column=Column(JSONB))
    rekomendasi: Optional[Any] = Field(default=None, sa_column=Column(JSONB))
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

