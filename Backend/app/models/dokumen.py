from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


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

