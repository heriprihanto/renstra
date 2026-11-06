from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SubkegiatanContextItem(BaseModel):
    kodesubkegiatan: Optional[str] = None
    uraisubkegiatan: str
    kinerja: Optional[str] = None
    indikator_uraian: Optional[str] = None
    satuan: Optional[str] = None
    target: Optional[str] = None


class SmartBreakdown(BaseModel):
    specific: str = Field(description="Spesifik: menjawab apa, siapa, dan fokus pencapaian yang jelas")
    measurable: str = Field(description="Terukur: memiliki satuan ukur dan rumus/metrik pasti")
    achievable: str = Field(description="Dapat dicapai: realistis sesuai kapasitas dan sumber daya daerah")
    relevant: str = Field(description="Relevan: selaras dengan prioritas dan level cascading kinerja")
    time_bound: str = Field(description="Terikat waktu: periode pencapaian tahunan RENSTRA 2025-2029/2030")


class SmartIndicatorItem(BaseModel):
    uraian: str = Field(description="Rumusan nama indikator kinerja SMART")
    satuan: str = Field(description="Satuan pengukuran (contoh: %, Orang, Dokumen, Indeks, Paket)")
    status: str = Field(default="positif", description="Sifat indikator (positif / negatif / konstan)")
    definisi_operasional: str = Field(description="Definisi operasional, rumus perhitungan, atau cara pengukuran")
    smart_breakdown: SmartBreakdown = Field(description="Ulasan pemenuhan kriteria SMART")
    target_recommendation: Optional[Dict[str, str]] = Field(default=None, description="Contoh target tahunan 2025 s/d 2030")
    target_awal: Optional[str] = None
    target2026: Optional[str] = None
    target2027: Optional[str] = None
    target2028: Optional[str] = None
    target2029: Optional[str] = None
    target2030: Optional[str] = None


class SmartRecommendationRequest(BaseModel):
    level: str = Field(description="tujuan | sasaran | program | kegiatan | subkegiatan")
    uraian: Optional[str] = Field(default=None, description="Uraian dari Tujuan/Sasaran/Program/Kegiatan/Subkegiatan")
    entity_uraian: Optional[str] = Field(default=None, description="Alias untuk uraian")
    parent_uraian: Optional[str] = Field(default=None, description="Uraian induk/parent bila ada")
    kinerja: Optional[str] = Field(default=None, description="Tolak ukur kinerja entitas bila ada")
    opd_name: Optional[str] = Field(default=None, description="Nama OPD / Sub SKPD terkait")
    existing_indikator: Optional[str] = Field(default=None, description="Uraian indikator eksisting untuk perbaikan")
    subkegiatan_list: Optional[List[SubkegiatanContextItem]] = Field(
        default=None,
        description="Khusus level kegiatan: daftar subkegiatan dan indikatornya di bawah kegiatan ini",
    )

    def get_uraian(self) -> str:
        return (self.uraian or self.entity_uraian or "").strip()


class SmartRecommendationResponse(BaseModel):
    success: bool
    source: str = Field(description="hermes | openai | smart_fallback")
    message: Optional[str] = None
    notice: Optional[str] = None
    level: str
    input_uraian: str
    recommendations: List[SmartIndicatorItem]
