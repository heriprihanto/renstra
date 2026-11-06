from typing import Optional
from pydantic import BaseModel


# === TUJUAN ===
class TujuanCreate(BaseModel):
    id_skpd: int
    uraitujuan: str
    no_urut: Optional[int] = 1
    perubahan_status: Optional[str] = "baru"


class TujuanUpdate(BaseModel):
    uraitujuan: str
    no_urut: Optional[int] = None
    perubahan_status: Optional[str] = None


# === SASARAN ===
class SasaranCreate(BaseModel):
    idtujuan: str
    uraisasaran: str
    no_urut: Optional[int] = 1
    perubahan_status: Optional[str] = "baru"


class SasaranUpdate(BaseModel):
    uraisasaran: str
    no_urut: Optional[int] = None
    perubahan_status: Optional[str] = None


# === INDIKATOR (TUJUAN / SASARAN) ===
class IndikatorCreate(BaseModel):
    parent_id: str  # idtujuan atau idsasaran
    uraian: str
    satuan: Optional[str] = "-"
    status: Optional[str] = "positif"
    iku: Optional[str] = "0"
    perubahan_status: Optional[str] = None
    definisi_operasional: Optional[str] = "-"
    target_awal: Optional[str] = "-"
    target2026: Optional[str] = "-"
    target2027: Optional[str] = "-"
    target2028: Optional[str] = "-"
    target2029: Optional[str] = "-"
    target2030: Optional[str] = "-"
    target_akhir: Optional[str] = "-"
    p_target2025: Optional[str] = "-"
    p_target2026: Optional[str] = "-"
    p_target2027: Optional[str] = "-"
    p_target2028: Optional[str] = "-"
    p_target2029: Optional[str] = "-"
    p_target2030: Optional[str] = "-"
    p_target_akhir: Optional[str] = "-"
    no_urut: Optional[int] = 1


class IndikatorUpdate(BaseModel):
    uraian: str
    satuan: Optional[str] = "-"
    status: Optional[str] = "positif"
    iku: Optional[str] = None
    perubahan_status: Optional[str] = None
    definisi_operasional: Optional[str] = "-"
    target_awal: Optional[str] = "-"
    target2026: Optional[str] = "-"
    target2027: Optional[str] = "-"
    target2028: Optional[str] = "-"
    target2029: Optional[str] = "-"
    target2030: Optional[str] = "-"
    target_akhir: Optional[str] = "-"
    p_target2025: Optional[str] = "-"
    p_target2026: Optional[str] = "-"
    p_target2027: Optional[str] = "-"
    p_target2028: Optional[str] = "-"
    p_target2029: Optional[str] = "-"
    p_target2030: Optional[str] = "-"
    p_target_akhir: Optional[str] = "-"
    no_urut: Optional[int] = None


# === INDIKATOR KEGIATAN ===
class IndikatorKegiatanCreate(BaseModel):
    kodeskpd: str
    kodekegiatan: str
    kodeprogram: Optional[str] = None
    uraikegiatan: Optional[str] = None
    uraian: str
    satuan: Optional[str] = "-"
    status: Optional[str] = "positif"
    iku: Optional[str] = "0"
    perubahan_status: Optional[str] = "baru"
    definisi_operasional: Optional[str] = "-"
    target_awal: Optional[str] = "-"
    target2026: Optional[str] = "-"
    target2027: Optional[str] = "-"
    target2028: Optional[str] = "-"
    target2029: Optional[str] = "-"
    target2030: Optional[str] = "-"
    target_akhir: Optional[str] = "-"
    p_target2025: Optional[str] = "-"
    p_target2026: Optional[str] = "-"
    p_target2027: Optional[str] = "-"
    p_target2028: Optional[str] = "-"
    p_target2029: Optional[str] = "-"
    p_target2030: Optional[str] = "-"
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
    no_urut: Optional[int] = 1


class IndikatorKegiatanUpdate(BaseModel):
    uraian: Optional[str] = None
    satuan: Optional[str] = None
    status: Optional[str] = None
    iku: Optional[str] = None
    perubahan_status: Optional[str] = None
    definisi_operasional: Optional[str] = None
    p_target2025: Optional[str] = None
    p_target2026: Optional[str] = None
    p_target2027: Optional[str] = None
    p_target2028: Optional[str] = None
    p_target2029: Optional[str] = None
    p_target2030: Optional[str] = None
    p_target_akhir: Optional[str] = None
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
    no_urut: Optional[int] = None


class IndikatorProgramUpdate(BaseModel):
    uraian: Optional[str] = None
    satuan: Optional[str] = None
    status: Optional[str] = None
    perubahan_status: Optional[str] = None
    p_target2025: Optional[str] = None
    p_target2026: Optional[str] = None
    p_target2027: Optional[str] = None
    p_target2028: Optional[str] = None
    p_target2029: Optional[str] = None
    p_target2030: Optional[str] = None
    p_target_akhir: Optional[str] = None


# === PROGRAM ===
class ProgramCreate(BaseModel):
    kodeskpd: str
    kodebidang: Optional[str] = None
    uraibidang: Optional[str] = None
    kodeprogram: str
    uraiprogram: str
    kinerja: Optional[str] = None
    no: Optional[int] = 1


class ProgramUpdate(BaseModel):
    kodeprogram: Optional[str] = None
    uraiprogram: Optional[str] = None
    kinerja: Optional[str] = None
    no: Optional[int] = None


# === KEGIATAN ===
class KegiatanCreate(BaseModel):
    kodeskpd: str
    kodebidang: Optional[str] = None
    kodeprogram: str
    kodekegiatan: str
    uraikegiatan: str
    kinerja: Optional[str] = None
    no: Optional[int] = 1


class KegiatanUpdate(BaseModel):
    kodekegiatan: Optional[str] = None
    uraikegiatan: Optional[str] = None
    kinerja: Optional[str] = None
    no: Optional[int] = None


# === SUBKEGIATAN ===
class SubkegiatanCreate(BaseModel):
    kodeskpd: str
    kodebidang: Optional[str] = None
    kodeprogram: str
    kodekegiatan: str
    kodesubkegiatan: str
    uraisubkegiatan: str
    kinerja: Optional[str] = None
    kodesubkegiatan_indikator: Optional[str] = None
    uraisubkegiatan_indikator: Optional[str] = None
    satuan: Optional[str] = "-"
    status: Optional[str] = "positif"
    volume_awal: Optional[str] = "-"
    volume_0: Optional[str] = "-"
    volume_1: Optional[str] = "-"
    volume_2: Optional[str] = "-"
    volume_3: Optional[str] = "-"
    volume_4: Optional[str] = "-"
    volume_5: Optional[str] = "-"
    p_volume_0: Optional[str] = "-"
    p_volume_1: Optional[str] = "-"
    p_volume_2: Optional[str] = "-"
    p_volume_3: Optional[str] = "-"
    p_volume_4: Optional[str] = "-"
    p_volume_5: Optional[str] = "-"
    p_volume_akhir: Optional[str] = "-"
    perubahan_status: Optional[str] = "tetap"
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
    no: Optional[int] = 1


class SubkegiatanUpdate(BaseModel):
    kodesubkegiatan: Optional[str] = None
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
    p_volume_0: Optional[str] = None
    p_volume_1: Optional[str] = None
    p_volume_2: Optional[str] = None
    p_volume_3: Optional[str] = None
    p_volume_4: Optional[str] = None
    p_volume_5: Optional[str] = None
    p_volume_akhir: Optional[str] = None
    perubahan_status: Optional[str] = None
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

