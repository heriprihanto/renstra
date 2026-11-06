from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel


class TaOpd(SQLModel, table=True):
    __tablename__ = "ta_opd"

    id_skpd: int = Field(default=None, primary_key=True)
    kode_skpd: Optional[str] = Field(default=None, index=True)
    nama_skpd: Optional[str] = Field(default=None, index=True)

    sub_pd_list: List["TaSubPd"] = Relationship(back_populates="opd")


class TaSubPd(SQLModel, table=True):
    __tablename__ = "ta_sub_pd"

    id_sub_skpd: int = Field(default=None, primary_key=True)
    id_skpd: Optional[int] = Field(default=None, foreign_key="ta_opd.id_skpd", index=True)
    kode_sub_skpd: Optional[str] = Field(default=None, index=True)
    nama_sub_skpd: Optional[str] = Field(default=None, index=True)

    opd: Optional[TaOpd] = Relationship(back_populates="sub_pd_list")
