from typing import List, Optional
from pydantic import BaseModel


class IndikatorTargetItem(BaseModel):
    id: str
    uraian: str
    satuan: Optional[str] = "-"
    status: Optional[str] = "-"
    iku: Optional[str] = "0"
    perubahan_status: Optional[str] = "tetap"
    is_baru: bool = False
    is_perubahan: bool = False
    changed_targets: List[str] = []
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
    realisasi2025: Optional[str] = "-"
    realisasi2026: Optional[str] = "-"
    realisasi2027: Optional[str] = "-"
    realisasi2028: Optional[str] = "-"
    realisasi2029: Optional[str] = "-"
    realisasi2030: Optional[str] = "-"


class SasaranCascadingItem(BaseModel):
    idsasaran: str
    uraisasaran: str
    no_urut: Optional[int] = None
    perubahan_status: Optional[str] = None
    is_baru: bool = False
    total_perubahan: int = 0
    total_baru: int = 0
    indikator_sasaran: List[IndikatorTargetItem] = []


class TujuanCascadingItem(BaseModel):
    idtujuan: str
    uraitujuan: str
    no_urut: Optional[int] = None
    perubahan_status: Optional[str] = None
    is_baru: bool = False
    total_perubahan: int = 0
    total_baru: int = 0
    indikator_tujuan: List[IndikatorTargetItem] = []
    sasaran: List[SasaranCascadingItem] = []


class OpdRenstraCascadingResponse(BaseModel):
    id_skpd: int
    kode_skpd: str
    nama_skpd: str
    total_tujuan: int
    total_sasaran: int
    total_indikator: int = 0
    total_indikator_perubahan: int = 0
    total_indikator_baru: int = 0
    tujuan_list: List[TujuanCascadingItem] = []


# =====================================================================
# PROGRAM / KEGIATAN / SUBKEGIATAN (SUB SKPD) CASCADING SCHEMAS
# =====================================================================

class IndikatorSubkegiatanItem(BaseModel):
    id: int
    kode: Optional[str] = "-"
    uraian: str
    satuan: Optional[str] = "-"
    status: Optional[str] = "-"
    volume_awal: Optional[str] = "-"
    volume_0: Optional[str] = "-"
    volume_1: Optional[str] = "-"
    volume_2: Optional[str] = "-"
    volume_3: Optional[str] = "-"
    volume_4: Optional[str] = "-"
    volume_5: Optional[str] = "-"
    volume_akhir: Optional[str] = "-"
    p_volume_0: Optional[str] = "-"
    p_volume_1: Optional[str] = "-"
    p_volume_2: Optional[str] = "-"
    p_volume_3: Optional[str] = "-"
    p_volume_4: Optional[str] = "-"
    p_volume_5: Optional[str] = "-"
    p_volume_akhir: Optional[str] = "-"
    realisasi2025: Optional[str] = "-"
    realisasi2026: Optional[str] = "-"
    realisasi2027: Optional[str] = "-"
    realisasi2028: Optional[str] = "-"
    realisasi2029: Optional[str] = "-"
    realisasi2030: Optional[str] = "-"
    perubahan_status: Optional[str] = "tetap"
    is_baru: bool = False
    is_perubahan: bool = False
    changed_targets: List[str] = []
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


class SubkegiatanCascadingItem(BaseModel):
    id: int
    kodesubkegiatan: str
    uraisubkegiatan: str
    kinerja: Optional[str] = "-"
    kodebidang: Optional[str] = None
    kodeprogram: Optional[str] = None
    kodekegiatan: Optional[str] = None
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
    indikator: Optional[IndikatorSubkegiatanItem] = None


class IndikatorKegiatanItem(BaseModel):
    id: Optional[str] = None
    kodekegiatan: Optional[str] = "-"
    kodeskpd: Optional[str] = "-"
    uraian: str
    satuan: Optional[str] = "-"
    status: Optional[str] = "-"
    iku: Optional[str] = "0"
    perubahan_status: Optional[str] = "tetap"
    is_baru: bool = False
    is_perubahan: bool = False
    changed_targets: List[str] = []
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
    realisasi2025: Optional[str] = "-"
    realisasi2026: Optional[str] = "-"
    realisasi2027: Optional[str] = "-"
    realisasi2028: Optional[str] = "-"
    realisasi2029: Optional[str] = "-"
    realisasi2030: Optional[str] = "-"
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
    definisi_operasional: Optional[str] = None
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
    realisasi2025: Optional[str] = "-"
    realisasi2026: Optional[str] = "-"
    realisasi2027: Optional[str] = "-"
    realisasi2028: Optional[str] = "-"
    realisasi2029: Optional[str] = "-"
    realisasi2030: Optional[str] = "-"
    pagu1: Optional[float] = 0.0
    pagu2: Optional[float] = 0.0
    pagu3: Optional[float] = 0.0
    pagu4: Optional[float] = 0.0
    pagu5: Optional[float] = 0.0
    no_urut: Optional[int] = 1


class IndikatorKegiatanUpdate(BaseModel):
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
    realisasi2025: Optional[str] = None
    realisasi2026: Optional[str] = None
    realisasi2027: Optional[str] = None
    realisasi2028: Optional[str] = None
    realisasi2029: Optional[str] = None
    realisasi2030: Optional[str] = None
    pagu1: Optional[float] = None
    pagu2: Optional[float] = None
    pagu3: Optional[float] = None
    pagu4: Optional[float] = None
    pagu5: Optional[float] = None
    no_urut: Optional[int] = None


class KegiatanCascadingItem(BaseModel):
    id: int
    kodekegiatan: str
    uraikegiatan: str
    kinerja: Optional[str] = "-"
    kodeprogram: Optional[str] = None
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
    indikator_kegiatan: List[IndikatorKegiatanItem] = []
    subkegiatan: List[SubkegiatanCascadingItem] = []


class IndikatorProgramItem(BaseModel):
    id: int
    uraian: str
    satuan: Optional[str] = "-"
    status: Optional[str] = "-"
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
    realisasi2025: Optional[str] = "-"
    realisasi2026: Optional[str] = "-"
    realisasi2027: Optional[str] = "-"
    realisasi2028: Optional[str] = "-"
    realisasi2029: Optional[str] = "-"
    realisasi2030: Optional[str] = "-"
    perubahan_status: Optional[str] = "tetap"
    is_baru: bool = False
    is_perubahan: bool = False
    changed_targets: List[str] = []


class ProgramSasaranTagItem(BaseModel):
    idsasaran: str
    uraisasaran: str
    no: Optional[int] = None
    uraitujuan: Optional[str] = None


class ProgramCascadingItem(BaseModel):
    id: str
    kodeprogram: str
    uraiprogram: str
    kinerja: Optional[str] = "-"
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
    renstra_sasaran: List[str] = []
    sasaran_list: List[ProgramSasaranTagItem] = []
    indikator_program: List[IndikatorProgramItem] = []
    kegiatan: List[KegiatanCascadingItem] = []


class SubSkpdCascadingResponse(BaseModel):
    id_sub_skpd: int
    id_skpd: int
    kode_sub_skpd: str
    nama_sub_skpd: str
    nama_skpd: Optional[str] = None
    total_program: int = 0
    total_kegiatan: int = 0
    total_subkegiatan: int = 0
    total_indikator_program: int = 0
    total_pagu: float = 0.0
    total_p_pagu: Optional[float] = 0.0
    program_list: List[ProgramCascadingItem] = []
