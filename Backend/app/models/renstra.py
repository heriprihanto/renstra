from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel


class RenstraTujuan(SQLModel, table=True):
    __tablename__ = "renstra_tujuan"

    idtujuan: UUID = Field(primary_key=True)
    kodepemda: Optional[str] = None
    idperiode: Optional[str] = None
    kodeskpd: Optional[str] = Field(default=None, index=True)
    no_urut: Optional[int] = None
    uraitujuan: Optional[str] = None
    perubahan_status: Optional[str] = None


class RenstraIndikatorTujuan(SQLModel, table=True):
    __tablename__ = "renstra_indikator_tujuan"

    idtujuan_indikator: UUID = Field(primary_key=True)
    idtujuan: Optional[UUID] = Field(default=None, index=True)
    kodepemda: Optional[str] = None
    idperiode: Optional[str] = None
    kodeskpd: Optional[str] = None
    uraitujuan_indikator: Optional[str] = None
    status: Optional[str] = None
    satuan: Optional[str] = None
    iku: Optional[str] = None
    perubahan_status: Optional[str] = None
    target_awal: Optional[str] = None
    target0: Optional[str] = None
    target1: Optional[str] = None
    target2: Optional[str] = None
    target3: Optional[str] = None
    target4: Optional[str] = None
    target5: Optional[str] = None
    no_urut: Optional[int] = None
    urut: Optional[int] = None
    definisi_operasional: Optional[str] = None
    p_target0: Optional[str] = None
    p_target1: Optional[str] = None
    p_target2: Optional[str] = None
    p_target3: Optional[str] = None
    p_target4: Optional[str] = None
    p_target5: Optional[str] = None


class RenstraSasaran(SQLModel, table=True):
    __tablename__ = "renstra_sasaran"

    idsasaran: UUID = Field(primary_key=True)
    kodepemda: Optional[str] = None
    idperiode: Optional[str] = None
    kodeskpd: Optional[str] = Field(default=None, index=True)
    idtujuan: Optional[UUID] = Field(default=None, index=True)
    uraisasaran: Optional[str] = None
    total_indikator: Optional[int] = None
    urut: Optional[int] = None
    no: Optional[int] = None
    perubahan_status: Optional[str] = None


class RenstraIndikatorSasaran(SQLModel, table=True):
    __tablename__ = "renstra_indikator_sasaran"

    idsasaran_indikator: UUID = Field(primary_key=True)
    kodepemda: Optional[str] = None
    idperiode: Optional[str] = None
    kodeskpd: Optional[str] = None
    idsasaran: Optional[UUID] = Field(default=None, index=True)
    uraisasaran_indikator: Optional[str] = None
    status: Optional[str] = None
    satuan: Optional[str] = None
    iku: Optional[str] = None
    perubahan_status: Optional[str] = None
    target_awal: Optional[str] = None
    target0: Optional[str] = None
    target1: Optional[str] = None
    target2: Optional[str] = None
    target3: Optional[str] = None
    target4: Optional[str] = None
    target5: Optional[str] = None
    urut: Optional[int] = None
    no: Optional[int] = None
    definisi_operasional: Optional[str] = None
    p_target0: Optional[str] = None
    p_target1: Optional[str] = None
    p_target2: Optional[str] = None
    p_target3: Optional[str] = None
    p_target4: Optional[str] = None
    p_target5: Optional[str] = None


class RenstraProgram(SQLModel, table=True):
    __tablename__ = "renstra_program"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    kodepemda: Optional[str] = None
    idperiode: Optional[str] = None
    kodeskpd: Optional[str] = Field(default=None, index=True)
    kodebidang: Optional[str] = None
    uraibidang: Optional[str] = None
    kodeprogram: Optional[str] = Field(default=None, index=True)
    uraiprogram: Optional[str] = None
    urai: Optional[str] = None
    kinerja: Optional[str] = None
    no: Optional[int] = None
    idx: Optional[int] = None


class RenstraIndikatorProgram(SQLModel, table=True):
    __tablename__ = "renstra_indikator_program"

    id: int = Field(primary_key=True)
    kodepemda: Optional[str] = None
    kodeskpd: Optional[str] = Field(default=None, index=True)
    idperiode: Optional[str] = None
    kodeprogram: Optional[str] = Field(default=None, index=True)
    uraiprogram: Optional[str] = None
    kodeindikator: Optional[UUID] = None
    uraiindikator: Optional[str] = None
    satuan: Optional[str] = None
    status: Optional[str] = None
    target_awal: Optional[str] = None
    target0: Optional[str] = None
    target1: Optional[str] = None
    target2: Optional[str] = None
    target3: Optional[str] = None
    target4: Optional[str] = None
    target5: Optional[str] = None
    p_target0: Optional[str] = "-"
    p_target1: Optional[str] = "-"
    p_target2: Optional[str] = "-"
    p_target3: Optional[str] = "-"
    p_target4: Optional[str] = "-"
    p_target5: Optional[str] = "-"
    p_target_akhir: Optional[str] = "-"
    perubahan_status: Optional[str] = "tetap"
    urut: Optional[int] = None
    no: Optional[int] = None


class RenstraKegiatan(SQLModel, table=True):
    __tablename__ = "renstra_kegiatan"

    id: Optional[int] = Field(default=None, primary_key=True)
    kodepemda: Optional[str] = "3376"
    idperiode: Optional[str] = "20252029"
    kodeskpd: Optional[str] = Field(default=None, index=True)
    kodebidang: Optional[str] = None
    kodeprogram: Optional[str] = Field(default=None, index=True)
    kodekegiatan: Optional[str] = Field(default=None, index=True)
    uraikegiatan: Optional[str] = None
    kinerja: Optional[str] = None
    no: Optional[int] = None


class RenstraOutputKegiatan(SQLModel, table=True):
    __tablename__ = "renstra_output_kegiatan"

    id: UUID = Field(primary_key=True)
    kodepemda: Optional[str] = None
    idperiode: Optional[str] = None
    kodeskpd: Optional[str] = Field(default=None, index=True)
    kodebidang: Optional[str] = None
    kodeprogram: Optional[str] = Field(default=None, index=True)
    kodekegiatan: Optional[str] = Field(default=None, index=True)
    urai: Optional[str] = None
    pagu1: Optional[float] = None
    pagu2: Optional[float] = None
    pagu3: Optional[float] = None
    pagu4: Optional[float] = None
    pagu5: Optional[float] = None
    urut: Optional[int] = None
    no: Optional[int] = None


class RenstraIndikatorKegiatan(SQLModel, table=True):
    __tablename__ = "renstra_indikator_kegiatan"

    id: Optional[int] = Field(default=None, primary_key=True)
    kodepemda: Optional[str] = "3376"
    idperiode: Optional[str] = "20252029"
    kodeskpd: Optional[str] = Field(default=None, index=True)
    kodebidang: Optional[str] = None
    kodeprogram: Optional[str] = Field(default=None, index=True)
    uraiprogram: Optional[str] = None
    kodekegiatan: Optional[str] = Field(default=None, index=True)
    uraikegiatan: Optional[str] = None
    kodeindikator: Optional[str] = None
    uraiindikator: str
    satuan: Optional[str] = "-"
    status: Optional[str] = "positif"
    target_awal: Optional[str] = "-"
    target0: Optional[str] = "-"
    target1: Optional[str] = "-"
    target2: Optional[str] = "-"
    target3: Optional[str] = "-"
    target4: Optional[str] = "-"
    target5: Optional[str] = "-"
    target_akhir: Optional[str] = "-"
    p_target0: Optional[str] = "-"
    p_target1: Optional[str] = "-"
    p_target2: Optional[str] = "-"
    p_target3: Optional[str] = "-"
    p_target4: Optional[str] = "-"
    p_target5: Optional[str] = "-"
    p_target_akhir: Optional[str] = "-"
    pagu1: Optional[float] = 0.0
    pagu2: Optional[float] = 0.0
    pagu3: Optional[float] = 0.0
    pagu4: Optional[float] = 0.0
    pagu5: Optional[float] = 0.0
    p_pagu1: Optional[float] = 0.0
    p_pagu2: Optional[float] = 0.0
    p_pagu3: Optional[float] = 0.0
    p_pagu4: Optional[float] = 0.0
    p_pagu5: Optional[float] = 0.0
    iku: Optional[str] = "0"
    definisi_operasional: Optional[str] = None
    perubahan_status: Optional[str] = "tetap"
    urut: Optional[int] = 1
    no: Optional[int] = 1


class RenstraSubkegiatan(SQLModel, table=True):
    __tablename__ = "renstra_subkegiatan"

    id: Optional[int] = Field(default=None, primary_key=True)
    kodepemda: Optional[str] = "3376"
    idperiode: Optional[str] = "20252029"
    kodeskpd: Optional[str] = Field(default=None, index=True)
    kodebidang: Optional[str] = None
    kodeprogram: Optional[str] = Field(default=None, index=True)
    kodekegiatan: Optional[str] = Field(default=None, index=True)
    kodesubkegiatan: Optional[str] = Field(default=None, index=True)
    uraisubkegiatan: Optional[str] = None
    kinerja: Optional[str] = None
    kodesubkegiatan_indikator: Optional[str] = None
    uraisubkegiatan_indikator: Optional[str] = None
    satuan: Optional[str] = None
    status: Optional[str] = None
    volume_awal: Optional[str] = None
    volume_0: Optional[str] = None
    volume_1: Optional[str] = None
    volume_2: Optional[str] = None
    volume_3: Optional[str] = None
    volume_4: Optional[str] = None
    volume_5: Optional[str] = None
    p_volume_0: Optional[str] = "-"
    p_volume_1: Optional[str] = "-"
    p_volume_2: Optional[str] = "-"
    p_volume_3: Optional[str] = "-"
    p_volume_4: Optional[str] = "-"
    p_volume_5: Optional[str] = "-"
    p_volume_akhir: Optional[str] = "-"
    perubahan_status: Optional[str] = "tetap"
    pagu1: Optional[float] = None
    pagu2: Optional[float] = None
    pagu3: Optional[float] = None
    pagu4: Optional[float] = None
    pagu5: Optional[float] = None
    p_pagu1: Optional[float] = None
    p_pagu2: Optional[float] = None
    p_pagu3: Optional[float] = None
    p_pagu4: Optional[float] = None
    p_pagu5: Optional[float] = None
    no: Optional[int] = None


class RefSubkegiatan(SQLModel, table=True):
    __tablename__ = "ref_subkegiatan"

    id: Optional[int] = Field(default=None, primary_key=True)
    tahun: Optional[str] = None
    versipemutakhiran: Optional[str] = None
    idpemutakhiran: Optional[str] = Field(default=None, index=True)
    jnspemda: Optional[str] = Field(default=None, index=True)
    kodebidang: Optional[str] = Field(default=None, index=True)
    uraibidang: Optional[str] = None
    kodeprogram: Optional[str] = Field(default=None, index=True)
    uraiprogram: Optional[str] = None
    kodekegiatan: Optional[str] = Field(default=None, index=True)
    uraikegiatan: Optional[str] = None
    kodesubkegiatan: Optional[str] = Field(default=None, index=True)
    uraisubkegiatan: Optional[str] = None
    referensi_kodesubkegiatan: Optional[str] = None
    referensi_uraisubkegiatan: Optional[str] = None
    referensi_subkegiatan: Optional[str] = None
    definisi_operasional: Optional[str] = None
    bidang_pelaksana: Optional[str] = None
    spm: Optional[str] = None
    jenis: Optional[str] = None
    bidang: Optional[str] = None
    program: Optional[str] = None
    kegiatan: Optional[str] = None
    subkegiatan: Optional[str] = None
    subkegiatan_tampil: Optional[str] = None
    kinerja: Optional[str] = None
    indikator: Optional[str] = None
    status_indikator: Optional[str] = None
    satuan: Optional[str] = None
    disabled: Optional[str] = None
    tag: Optional[str] = None
    pemda: Optional[str] = None
    ketergunaan: Optional[str] = None
    no: Optional[int] = None

