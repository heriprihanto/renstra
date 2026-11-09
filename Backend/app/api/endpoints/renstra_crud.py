import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, text
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import get_session
from app.models.opd import TaOpd, TaSubPd
from app.models.renstra import (
    RenstraIndikatorKegiatan,
    RenstraIndikatorProgram,
    RenstraIndikatorSasaran,
    RenstraIndikatorTujuan,
    RenstraKegiatan,
    RenstraProgram,
    RenstraSasaran,
    RenstraSubkegiatan,
    RenstraTujuan,
)
from app.schemas.renstra_crud import (
    IndikatorCreate,
    IndikatorKegiatanCreate,
    IndikatorKegiatanUpdate,
    IndikatorProgramUpdate,
    IndikatorUpdate,
    KegiatanCreate,
    KegiatanUpdate,
    ProgramCreate,
    ProgramUpdate,
    SasaranCreate,
    SasaranUpdate,
    SubkegiatanCreate,
    SubkegiatanUpdate,
    TujuanCreate,
    TujuanUpdate,
)

router = APIRouter(prefix="/renstra", tags=["RENSTRA CRUD"])


# =====================================================================
# 0. REFERENSI KEGIATAN & SUBKEGIATAN DARI REF_SUBKEGIATAN
# =====================================================================

@router.get("/ref/kegiatan")
async def get_ref_kegiatan(kode_program: str, session: AsyncSession = Depends(get_session)):
    """
    Mengambil daftar referensi Kegiatan dari ref_subkegiatan berdasarkan kode_program.
    Mendukung Program Penunjang (X.XX.01 / *.01).
    """
    kp = kode_program.strip()
    is_penunjang = kp.endswith(".01") or kp == "X.XX.01"
    search_prog = "X.XX.01" if is_penunjang else kp

    sql = text("""
        SELECT DISTINCT kodekegiatan, uraikegiatan 
        FROM ref_subkegiatan 
        WHERE kodeprogram = :kp OR kodeprogram = :sp
        ORDER BY kodekegiatan ASC
    """)
    res = await session.execute(sql, {"kp": kp, "sp": search_prog})
    rows = res.fetchall()

    results = []
    for r in rows:
        kk = r.kodekegiatan or ""
        if is_penunjang and kk.startswith("X.XX.01"):
            kk = kp + kk[7:]
        results.append({
            "kodekegiatan": kk,
            "uraikegiatan": r.uraikegiatan or "",
        })
    return results


@router.get("/ref/subkegiatan")
async def get_ref_subkegiatan(kode_kegiatan: str, session: AsyncSession = Depends(get_session)):
    """
    Mengambil daftar referensi Subkegiatan dari ref_subkegiatan berdasarkan kode_kegiatan.
    Mendukung Kegiatan Penunjang (*.01.*).
    """
    kk = kode_kegiatan.strip()
    parts = kk.split(".")
    is_penunjang = len(parts) >= 3 and parts[2] == "01"
    search_keg = "X.XX.01." + ".".join(parts[3:]) if is_penunjang else kk

    sql = text("""
        SELECT kodesubkegiatan, uraisubkegiatan, kinerja, indikator, satuan 
        FROM ref_subkegiatan 
        WHERE kodekegiatan = :kk OR kodekegiatan = :sk
        ORDER BY kodesubkegiatan ASC
    """)
    res = await session.execute(sql, {"kk": kk, "sk": search_keg})
    rows = res.fetchall()

    results = []
    for r in rows:
        ksk = r.kodesubkegiatan or ""
        if is_penunjang and ksk.startswith("X.XX.01"):
            ksk = ".".join(parts[:3]) + ksk[7:]
        results.append({
            "kodesubkegiatan": ksk,
            "uraisubkegiatan": r.uraisubkegiatan or "",
            "kinerja": r.kinerja or "",
            "indikator": r.indikator or "",
            "satuan": r.satuan or "-",
        })
    return results


@router.get("/ref/sasaran")
async def get_ref_sasaran(
    kodeskpd: Optional[str] = None,
    id_skpd: Optional[int] = None,
    id_sub_skpd: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
):
    """
    Mengambil daftar referensi Sasaran RENSTRA untuk OPD / Sub SKPD terkait,
    digunakan untuk tagging keterkaitan Program dengan Sasaran.
    """
    target_kodeskpd = (kodeskpd or "").strip()

    if id_sub_skpd:
        sub = await session.get(TaSubPd, id_sub_skpd)
        if sub:
            target_kodeskpd = sub.kode_sub_skpd or target_kodeskpd
            if sub.id_skpd and not id_skpd:
                id_skpd = sub.id_skpd

    parent_kodeskpd = target_kodeskpd
    if id_skpd:
        opd = await session.get(TaOpd, id_skpd)
        if opd and opd.kode_skpd:
            parent_kodeskpd = opd.kode_skpd

    if not parent_kodeskpd or parent_kodeskpd == target_kodeskpd:
        if len(target_kodeskpd) >= 22:
            parent_kodeskpd = target_kodeskpd[:-4] + "0000"

    stmt = (
        select(RenstraSasaran, RenstraTujuan)
        .outerjoin(RenstraTujuan, RenstraTujuan.idtujuan == RenstraSasaran.idtujuan)
        .where(
            (RenstraSasaran.kodeskpd == target_kodeskpd) |
            (RenstraSasaran.kodeskpd == parent_kodeskpd)
        )
        .order_by(RenstraSasaran.urut.asc(), RenstraSasaran.no.asc())
    )
    rows = (await session.exec(stmt)).all()

    result = []
    seen = set()
    for s, t in rows:
        s_id = str(s.idsasaran)
        if s_id in seen:
            continue
        seen.add(s_id)
        result.append({
            "idsasaran": s_id,
            "no": s.no or s.urut or 1,
            "uraisasaran": s.uraisasaran or "-",
            "uraitujuan": t.uraitujuan if t else "-",
            "idtujuan": str(t.idtujuan) if t else None,
        })
    return result


# =====================================================================
# 1. TUJUAN CRUD
# =====================================================================

@router.post("/tujuan", response_model=Dict[str, Any])
async def create_tujuan(data: TujuanCreate, session: AsyncSession = Depends(get_session)):
    opd = await session.get(TaOpd, data.id_skpd)
    if not opd:
        raise HTTPException(status_code=404, detail="Perangkat Daerah tidak ditemukan")

    new_id = uuid.uuid4()
    tujuan = RenstraTujuan(
        idtujuan=new_id,
        kodepemda="3376",
        idperiode="20252029",
        kodeskpd=opd.kode_skpd,
        uraitujuan=data.uraitujuan.strip(),
        no_urut=data.no_urut or 1,
        perubahan_status=data.perubahan_status or "baru",
    )
    session.add(tujuan)
    await session.commit()
    return {
        "success": True,
        "idtujuan": str(new_id),
        "message": "Tujuan berhasil ditambahkan",
    }


@router.put("/tujuan/{idtujuan}", response_model=Dict[str, Any])
async def update_tujuan(idtujuan: str, data: TujuanUpdate, session: AsyncSession = Depends(get_session)):
    try:
        t_uuid = uuid.UUID(idtujuan)
    except ValueError:
        raise HTTPException(status_code=400, detail="Format ID Tujuan tidak valid")

    tujuan = await session.get(RenstraTujuan, t_uuid)
    if not tujuan:
        raise HTTPException(status_code=404, detail="Tujuan tidak ditemukan")

    # Kalimat Tujuan tidak dapat diedit pada RENSTRA Perubahan
    if data.no_urut is not None:
        tujuan.no_urut = data.no_urut
    if data.perubahan_status is not None:
        tujuan.perubahan_status = data.perubahan_status

    session.add(tujuan)
    await session.commit()
    return {"success": True, "message": "Tujuan berhasil diperbarui"}


@router.delete("/tujuan/{idtujuan}", response_model=Dict[str, Any])
async def delete_tujuan(idtujuan: str, session: AsyncSession = Depends(get_session)):
    raise HTTPException(
        status_code=403,
        detail="Data Tujuan tidak dapat dihapus pada RENSTRA Perubahan",
    )


# =====================================================================
# 2. INDIKATOR TUJUAN CRUD
# =====================================================================

@router.post("/indikator-tujuan", response_model=Dict[str, Any])
async def create_indikator_tujuan(data: IndikatorCreate, session: AsyncSession = Depends(get_session)):
    try:
        t_uuid = uuid.UUID(data.parent_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Format ID Tujuan tidak valid")

    tujuan = await session.get(RenstraTujuan, t_uuid)
    if not tujuan:
        raise HTTPException(status_code=404, detail="Tujuan tidak ditemukan")

    new_id = uuid.uuid4()
    # target_awal = Baseline; target1 = 2026; target2 = 2027; target3 = 2028; target4 = 2029 (Target Akhir); target5 = 2030
    target_2029_val = data.target2029 if data.target2029 and data.target2029 != "-" else (data.target_akhir or "-")
    p_target_2029_val = data.p_target2029 if data.p_target2029 and data.p_target2029 != "-" else (data.p_target_akhir or "-")
    ind = RenstraIndikatorTujuan(
        idtujuan_indikator=new_id,
        idtujuan=t_uuid,
        kodepemda="3376",
        idperiode="20252029",
        kodeskpd=tujuan.kodeskpd,
        uraitujuan_indikator=data.uraian.strip(),
        satuan=data.satuan or "-",
        status=data.status or "positif",
        iku=data.iku or "0",
        perubahan_status=data.perubahan_status or "baru",
        definisi_operasional=data.definisi_operasional or "-",
        target_awal=data.target_awal or "-",
        target1=data.target2026 or "-",
        target2=data.target2027 or "-",
        target3=data.target2028 or "-",
        target4=target_2029_val,
        target5=data.target2030 or "-",
        p_target0=data.p_target2025 or "-",
        p_target1=data.p_target2026 or "-",
        p_target2=data.p_target2027 or "-",
        p_target3=data.p_target2028 or "-",
        p_target4=p_target_2029_val,
        p_target5=data.p_target2030 or "-",
        realisasi0=data.realisasi2025 or "-",
        realisasi1=data.realisasi2026 or "-",
        realisasi2=data.realisasi2027 or "-",
        realisasi3=data.realisasi2028 or "-",
        realisasi4=data.realisasi2029 or "-",
        realisasi5=data.realisasi2030 or "-",
        no_urut=data.no_urut or 1,
        urut=data.no_urut or 1,
    )
    session.add(ind)
    await session.commit()
    return {
        "success": True,
        "id": str(new_id),
        "message": "Indikator Tujuan berhasil ditambahkan",
    }


@router.put("/indikator-tujuan/{id}", response_model=Dict[str, Any])
async def update_indikator_tujuan(id: str, data: IndikatorUpdate, session: AsyncSession = Depends(get_session)):
    try:
        ind_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Format ID Indikator tidak valid")

    ind = await session.get(RenstraIndikatorTujuan, ind_uuid)
    if not ind:
        raise HTTPException(status_code=404, detail="Indikator Tujuan tidak ditemukan")

    # Kalimat uraian dan Target Murni tidak dapat diedit pada RENSTRA Perubahan
    # Hanya metadata dan TARGET PERUBAHAN yang dapat diedit:
    p_target_2029_val = data.p_target2029 if data.p_target2029 and data.p_target2029 != "-" else (data.p_target_akhir or ind.p_target4 or "-")

    # Metadata
    if data.satuan is not None:
        ind.satuan = data.satuan
    if data.status is not None:
        ind.status = data.status
    if data.iku is not None:
        ind.iku = data.iku
    if data.perubahan_status is not None:
        ind.perubahan_status = data.perubahan_status
    if data.definisi_operasional is not None:
        ind.definisi_operasional = data.definisi_operasional
    if data.no_urut is not None:
        ind.no_urut = data.no_urut
        ind.urut = data.no_urut

    # Target Perubahan
    if data.p_target2025 is not None:
        ind.p_target0 = data.p_target2025 or "-"
    if data.p_target2026 is not None:
        ind.p_target1 = data.p_target2026 or "-"
    if data.p_target2027 is not None:
        ind.p_target2 = data.p_target2027 or "-"
    if data.p_target2028 is not None:
        ind.p_target3 = data.p_target2028 or "-"
    if data.p_target2029 is not None or data.p_target_akhir is not None:
        ind.p_target4 = p_target_2029_val
    if data.p_target2030 is not None:
        ind.p_target5 = data.p_target2030 or "-"

    # Realisasi Capaian
    if data.realisasi2025 is not None:
        ind.realisasi0 = data.realisasi2025 or "-"
    if data.realisasi2026 is not None:
        ind.realisasi1 = data.realisasi2026 or "-"
    if data.realisasi2027 is not None:
        ind.realisasi2 = data.realisasi2027 or "-"
    if data.realisasi2028 is not None:
        ind.realisasi3 = data.realisasi2028 or "-"
    if data.realisasi2029 is not None:
        ind.realisasi4 = data.realisasi2029 or "-"
    if data.realisasi2030 is not None:
        ind.realisasi5 = data.realisasi2030 or "-"

    session.add(ind)
    await session.commit()
    return {"success": True, "message": "Metadata, Target Perubahan, dan Realisasi Indikator Tujuan berhasil diperbarui"}


@router.delete("/indikator-tujuan/{id}", response_model=Dict[str, Any])
async def delete_indikator_tujuan(id: str, session: AsyncSession = Depends(get_session)):
    raise HTTPException(
        status_code=403,
        detail="Data Indikator Tujuan tidak dapat dihapus pada RENSTRA Perubahan",
    )


# =====================================================================
# 3. SASARAN CRUD
# =====================================================================

@router.post("/sasaran", response_model=Dict[str, Any])
async def create_sasaran(data: SasaranCreate, session: AsyncSession = Depends(get_session)):
    try:
        t_uuid = uuid.UUID(data.idtujuan)
    except ValueError:
        raise HTTPException(status_code=400, detail="Format ID Tujuan tidak valid")

    tujuan = await session.get(RenstraTujuan, t_uuid)
    if not tujuan:
        raise HTTPException(status_code=404, detail="Tujuan tidak ditemukan")

    new_id = uuid.uuid4()
    sasaran = RenstraSasaran(
        idsasaran=new_id,
        kodepemda="3376",
        idperiode="20252029",
        kodeskpd=tujuan.kodeskpd,
        idtujuan=t_uuid,
        uraisasaran=data.uraisasaran.strip(),
        urut=data.no_urut or 1,
        no=data.no_urut or 1,
        perubahan_status=data.perubahan_status or "baru",
    )
    session.add(sasaran)
    await session.commit()
    return {
        "success": True,
        "idsasaran": str(new_id),
        "message": "Sasaran berhasil ditambahkan",
    }


@router.put("/sasaran/{idsasaran}", response_model=Dict[str, Any])
async def update_sasaran(idsasaran: str, data: SasaranUpdate, session: AsyncSession = Depends(get_session)):
    try:
        s_uuid = uuid.UUID(idsasaran)
    except ValueError:
        raise HTTPException(status_code=400, detail="Format ID Sasaran tidak valid")

    sasaran = await session.get(RenstraSasaran, s_uuid)
    if not sasaran:
        raise HTTPException(status_code=404, detail="Sasaran tidak ditemukan")

    # Kalimat Sasaran tidak dapat diedit pada RENSTRA Perubahan
    if data.no_urut is not None:
        sasaran.urut = data.no_urut
        sasaran.no = data.no_urut
    if data.perubahan_status is not None:
        sasaran.perubahan_status = data.perubahan_status

    session.add(sasaran)
    await session.commit()
    return {"success": True, "message": "Sasaran berhasil diperbarui"}


@router.delete("/sasaran/{idsasaran}", response_model=Dict[str, Any])
async def delete_sasaran(idsasaran: str, session: AsyncSession = Depends(get_session)):
    raise HTTPException(
        status_code=403,
        detail="Data Sasaran tidak dapat dihapus pada RENSTRA Perubahan",
    )


# =====================================================================
# 4. INDIKATOR SASARAN CRUD
# =====================================================================

@router.post("/indikator-sasaran", response_model=Dict[str, Any])
async def create_indikator_sasaran(data: IndikatorCreate, session: AsyncSession = Depends(get_session)):
    try:
        s_uuid = uuid.UUID(data.parent_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Format ID Sasaran tidak valid")

    sasaran = await session.get(RenstraSasaran, s_uuid)
    if not sasaran:
        raise HTTPException(status_code=404, detail="Sasaran tidak ditemukan")

    new_id = uuid.uuid4()
    # target_awal = Baseline; target1 = 2026; target2 = 2027; target3 = 2028; target4 = 2029 (Target Akhir); target5 = 2030
    target_2029_val = data.target2029 if data.target2029 and data.target2029 != "-" else (data.target_akhir or "-")
    p_target_2029_val = data.p_target2029 if data.p_target2029 and data.p_target2029 != "-" else (data.p_target_akhir or "-")
    ind = RenstraIndikatorSasaran(
        idsasaran_indikator=new_id,
        idsasaran=s_uuid,
        kodepemda="3376",
        idperiode="20252029",
        kodeskpd=sasaran.kodeskpd,
        uraisasaran_indikator=data.uraian.strip(),
        satuan=data.satuan or "-",
        status=data.status or "positif",
        iku=data.iku or "0",
        perubahan_status=data.perubahan_status or "baru",
        definisi_operasional=data.definisi_operasional or "-",
        target_awal=data.target_awal or "-",
        target1=data.target2026 or "-",
        target2=data.target2027 or "-",
        target3=data.target2028 or "-",
        target4=target_2029_val,
        target5=data.target2030 or "-",
        p_target0=data.p_target2025 or "-",
        p_target1=data.p_target2026 or "-",
        p_target2=data.p_target2027 or "-",
        p_target3=data.p_target2028 or "-",
        p_target4=p_target_2029_val,
        p_target5=data.p_target2030 or "-",
        realisasi0=data.realisasi2025 or "-",
        realisasi1=data.realisasi2026 or "-",
        realisasi2=data.realisasi2027 or "-",
        realisasi3=data.realisasi2028 or "-",
        realisasi4=data.realisasi2029 or "-",
        realisasi5=data.realisasi2030 or "-",
        no=data.no_urut or 1,
        urut=data.no_urut or 1,
    )
    session.add(ind)
    await session.commit()
    return {
        "success": True,
        "id": str(new_id),
        "message": "Indikator Sasaran berhasil ditambahkan",
    }


@router.put("/indikator-sasaran/{id}", response_model=Dict[str, Any])
async def update_indikator_sasaran(id: str, data: IndikatorUpdate, session: AsyncSession = Depends(get_session)):
    try:
        ind_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Format ID Indikator tidak valid")

    ind = await session.get(RenstraIndikatorSasaran, ind_uuid)
    if not ind:
        raise HTTPException(status_code=404, detail="Indikator Sasaran tidak ditemukan")

    # Kalimat uraian dan Target Murni tidak dapat diedit pada RENSTRA Perubahan
    # Hanya metadata dan TARGET PERUBAHAN yang dapat diedit:
    p_target_2029_val = data.p_target2029 if data.p_target2029 and data.p_target2029 != "-" else (data.p_target_akhir or ind.p_target4 or "-")

    # Metadata
    if data.satuan is not None:
        ind.satuan = data.satuan
    if data.status is not None:
        ind.status = data.status
    if data.iku is not None:
        ind.iku = data.iku
    if data.perubahan_status is not None:
        ind.perubahan_status = data.perubahan_status
    if data.definisi_operasional is not None:
        ind.definisi_operasional = data.definisi_operasional
    if data.no_urut is not None:
        ind.no = data.no_urut
        ind.urut = data.no_urut

    # Target Perubahan
    if data.p_target2025 is not None:
        ind.p_target0 = data.p_target2025 or "-"
    if data.p_target2026 is not None:
        ind.p_target1 = data.p_target2026 or "-"
    if data.p_target2027 is not None:
        ind.p_target2 = data.p_target2027 or "-"
    if data.p_target2028 is not None:
        ind.p_target3 = data.p_target2028 or "-"
    if data.p_target2029 is not None or data.p_target_akhir is not None:
        ind.p_target4 = p_target_2029_val
    if data.p_target2030 is not None:
        ind.p_target5 = data.p_target2030 or "-"

    # Realisasi Capaian
    if data.realisasi2025 is not None:
        ind.realisasi0 = data.realisasi2025 or "-"
    if data.realisasi2026 is not None:
        ind.realisasi1 = data.realisasi2026 or "-"
    if data.realisasi2027 is not None:
        ind.realisasi2 = data.realisasi2027 or "-"
    if data.realisasi2028 is not None:
        ind.realisasi3 = data.realisasi2028 or "-"
    if data.realisasi2029 is not None:
        ind.realisasi4 = data.realisasi2029 or "-"
    if data.realisasi2030 is not None:
        ind.realisasi5 = data.realisasi2030 or "-"

    session.add(ind)
    await session.commit()
    return {"success": True, "message": "Metadata, Target Perubahan, dan Realisasi Indikator Sasaran berhasil diperbarui"}


@router.delete("/indikator-sasaran/{id}", response_model=Dict[str, Any])
async def delete_indikator_sasaran(id: str, session: AsyncSession = Depends(get_session)):
    raise HTTPException(
        status_code=403,
        detail="Data Indikator Sasaran tidak dapat dihapus pada RENSTRA Perubahan",
    )


# =====================================================================
# 5. INDIKATOR KEGIATAN CRUD
# =====================================================================

@router.post("/indikator-kegiatan", response_model=Dict[str, Any])
async def create_indikator_kegiatan(data: IndikatorKegiatanCreate, session: AsyncSession = Depends(get_session)):
    p_target_2029_val = data.p_target2029 if data.p_target2029 and data.p_target2029 != "-" else (data.p_target_akhir or data.target_akhir or "-")
    target_2029_val = data.target2029 if data.target2029 and data.target2029 != "-" else (data.target_akhir or "-")

    # Ambil uraian kegiatan dan program bila belum diisi
    uraikeg = data.uraikegiatan
    kodeprog = data.kodeprogram
    if not uraikeg or not kodeprog:
        keg = (await session.exec(
            select(RenstraKegiatan).where(
                RenstraKegiatan.kodeskpd == data.kodeskpd,
                RenstraKegiatan.kodekegiatan == data.kodekegiatan,
            )
        )).first()
        if keg:
            if not uraikeg:
                uraikeg = keg.uraikegiatan
            if not kodeprog:
                kodeprog = keg.kodeprogram

    ind = RenstraIndikatorKegiatan(
        kodepemda="3376",
        idperiode="20252029",
        kodeskpd=data.kodeskpd,
        kodeprogram=kodeprog,
        kodekegiatan=data.kodekegiatan,
        uraikegiatan=uraikeg,
        uraiindikator=data.uraian.strip(),
        satuan=data.satuan or "-",
        status=data.status or "positif",
        iku=data.iku or "0",
        perubahan_status=data.perubahan_status or "baru",
        definisi_operasional=data.definisi_operasional,
        target_awal=data.target_awal or "-",
        target1=data.target2026 or "-",
        target2=data.target2027 or "-",
        target3=data.target2028 or "-",
        target4=target_2029_val,
        target5=data.target2030 or "-",
        target_akhir=data.target_akhir or target_2029_val,
        p_target0=data.p_target2025 or "-",
        p_target1=data.p_target2026 or "-",
        p_target2=data.p_target2027 or "-",
        p_target3=data.p_target2028 or "-",
        p_target4=p_target_2029_val,
        p_target5=data.p_target2030 or "-",
        p_target_akhir=data.p_target_akhir or p_target_2029_val,
        realisasi0=data.realisasi2025 or "-",
        realisasi1=data.realisasi2026 or "-",
        realisasi2=data.realisasi2027 or "-",
        realisasi3=data.realisasi2028 or "-",
        realisasi4=data.realisasi2029 or "-",
        realisasi5=data.realisasi2030 or "-",
        pagu1=data.pagu1 or 0.0,
        pagu2=data.pagu2 or 0.0,
        pagu3=data.pagu3 or 0.0,
        pagu4=data.pagu4 or 0.0,
        pagu5=data.pagu5 or 0.0,
        no=data.no_urut or 1,
        urut=data.no_urut or 1,
    )
    session.add(ind)
    await session.commit()
    await session.refresh(ind)
    return {
        "success": True,
        "id": ind.id,
        "message": "Indikator Kegiatan berhasil ditambahkan",
    }


@router.put("/indikator-kegiatan/{id}", response_model=Dict[str, Any])
async def update_indikator_kegiatan(id: int, data: IndikatorKegiatanUpdate, session: AsyncSession = Depends(get_session)):
    ind = await session.get(RenstraIndikatorKegiatan, id)
    if not ind:
        raise HTTPException(status_code=404, detail="Indikator Kegiatan tidak ditemukan")

    p_target_2029_val = data.p_target2029 if data.p_target2029 and data.p_target2029 != "-" else (data.p_target_akhir or ind.p_target4 or "-")

    if data.satuan is not None:
        ind.satuan = data.satuan
    if data.status is not None:
        ind.status = data.status
    if data.iku is not None:
        ind.iku = data.iku
    if data.perubahan_status is not None:
        ind.perubahan_status = data.perubahan_status
    if data.definisi_operasional is not None:
        ind.definisi_operasional = data.definisi_operasional
    if data.no_urut is not None:
        ind.no = data.no_urut
        ind.urut = data.no_urut

    # Target Perubahan
    if data.p_target2025 is not None:
        ind.p_target0 = data.p_target2025 or "-"
    if data.p_target2026 is not None:
        ind.p_target1 = data.p_target2026 or "-"
    if data.p_target2027 is not None:
        ind.p_target2 = data.p_target2027 or "-"
    if data.p_target2028 is not None:
        ind.p_target3 = data.p_target2028 or "-"
    if data.p_target2029 is not None or data.p_target_akhir is not None:
        ind.p_target4 = p_target_2029_val
        ind.p_target_akhir = data.p_target_akhir or p_target_2029_val
    if data.p_target2030 is not None:
        ind.p_target5 = data.p_target2030 or "-"

    # Realisasi Capaian
    if data.realisasi2025 is not None:
        ind.realisasi0 = data.realisasi2025 or "-"
    if data.realisasi2026 is not None:
        ind.realisasi1 = data.realisasi2026 or "-"
    if data.realisasi2027 is not None:
        ind.realisasi2 = data.realisasi2027 or "-"
    if data.realisasi2028 is not None:
        ind.realisasi3 = data.realisasi2028 or "-"
    if data.realisasi2029 is not None:
        ind.realisasi4 = data.realisasi2029 or "-"
    if data.realisasi2030 is not None:
        ind.realisasi5 = data.realisasi2030 or "-"

    # Pagu jika diupdate
    if data.pagu1 is not None:
        ind.pagu1 = data.pagu1
    if data.pagu2 is not None:
        ind.pagu2 = data.pagu2
    if data.pagu3 is not None:
        ind.pagu3 = data.pagu3
    if data.pagu4 is not None:
        ind.pagu4 = data.pagu4
    if data.pagu5 is not None:
        ind.pagu5 = data.pagu5

    # Pagu Perubahan
    if data.p_pagu1 is not None:
        ind.p_pagu1 = data.p_pagu1
    if data.p_pagu2 is not None:
        ind.p_pagu2 = data.p_pagu2
    if data.p_pagu3 is not None:
        ind.p_pagu3 = data.p_pagu3
    if data.p_pagu4 is not None:
        ind.p_pagu4 = data.p_pagu4
    if data.p_pagu5 is not None:
        ind.p_pagu5 = data.p_pagu5

    session.add(ind)
    await session.commit()
    return {"success": True, "message": "Metadata, Target & Pagu Perubahan Indikator Kegiatan berhasil diperbarui"}


@router.put("/indikator-program/{id}", response_model=Dict[str, Any])
async def update_indikator_program(id: int, data: IndikatorProgramUpdate, session: AsyncSession = Depends(get_session)):
    ind = await session.get(RenstraIndikatorProgram, id)
    if not ind:
        raise HTTPException(status_code=404, detail="Indikator Program tidak ditemukan")

    if data.satuan is not None:
        ind.satuan = data.satuan.strip()
    if data.status is not None:
        ind.status = data.status.strip()
    if data.perubahan_status is not None:
        ind.perubahan_status = data.perubahan_status.strip()
    if data.definisi_operasional is not None:
        ind.definisi_operasional = data.definisi_operasional.strip()

    if data.p_target2025 is not None:
        ind.p_target0 = data.p_target2025 or "-"
    if data.p_target2026 is not None:
        ind.p_target1 = data.p_target2026 or "-"
    if data.p_target2027 is not None:
        ind.p_target2 = data.p_target2027 or "-"
    if data.p_target2028 is not None:
        ind.p_target3 = data.p_target2028 or "-"
    if data.p_target2029 is not None:
        p_target_2029_val = data.p_target2029 or "-"
        ind.p_target4 = p_target_2029_val
        ind.p_target_akhir = data.p_target_akhir or p_target_2029_val
    if data.p_target2030 is not None:
        ind.p_target5 = data.p_target2030 or "-"

    # Realisasi Capaian
    if data.realisasi2025 is not None:
        ind.realisasi0 = data.realisasi2025 or "-"
    if data.realisasi2026 is not None:
        ind.realisasi1 = data.realisasi2026 or "-"
    if data.realisasi2027 is not None:
        ind.realisasi2 = data.realisasi2027 or "-"
    if data.realisasi2028 is not None:
        ind.realisasi3 = data.realisasi2028 or "-"
    if data.realisasi2029 is not None:
        ind.realisasi4 = data.realisasi2029 or "-"
    if data.realisasi2030 is not None:
        ind.realisasi5 = data.realisasi2030 or "-"

    session.add(ind)
    await session.commit()
    return {"success": True, "message": "Metadata, Target Perubahan, dan Realisasi Indikator Program berhasil diperbarui"}


@router.delete("/indikator-kegiatan/{id}", response_model=Dict[str, Any])
async def delete_indikator_kegiatan(id: int, session: AsyncSession = Depends(get_session)):
    raise HTTPException(
        status_code=403,
        detail="Data Indikator Kegiatan tidak dapat dihapus pada RENSTRA Perubahan",
    )


# =====================================================================
# 5. PROGRAM CRUD
# =====================================================================

@router.post("/program", response_model=Dict[str, Any])
async def create_program(data: ProgramCreate, session: AsyncSession = Depends(get_session)):
    new_id = uuid.uuid4()
    next_idx = (await session.execute(text("SELECT nextval('renstra_program_idx_seq')"))).scalar()

    target_kodeskpd = data.kodeskpd.strip()
    parent_kodeskpd = target_kodeskpd[:-4] + "0000" if len(target_kodeskpd) >= 22 else target_kodeskpd
    sasaran_tags = []
    if data.sasaran_ids:
        for sid in data.sasaran_ids:
            clean_id = str(sid).strip()
            if len(clean_id) == 36:
                sasaran_tags.append(f"{parent_kodeskpd}{clean_id}")
            else:
                sasaran_tags.append(clean_id)

    program = RenstraProgram(
        id=new_id,
        idx=next_idx,
        kodepemda="3376",
        idperiode="20252029",
        kodeskpd=data.kodeskpd,
        kodebidang=data.kodebidang,
        uraibidang=data.uraibidang,
        kodeprogram=data.kodeprogram.strip(),
        uraiprogram=data.uraiprogram.strip(),
        urai=data.kinerja.strip() if data.kinerja else None,
        kinerja=data.kinerja.strip() if data.kinerja else None,
        no=data.no or 1,
        renstra_sasaran=sasaran_tags if sasaran_tags else None,
    )
    session.add(program)
    await session.commit()
    await session.refresh(program)
    return {
        "success": True,
        "message": "Program berhasil ditambahkan",
        "data": {
            "id": str(program.id),
            "kodeprogram": program.kodeprogram,
            "uraiprogram": program.uraiprogram,
            "kinerja": program.kinerja,
            "renstra_sasaran": program.renstra_sasaran,
        },
    }


@router.put("/program/{id}", response_model=Dict[str, Any])
async def update_program(id: str, data: ProgramUpdate, session: AsyncSession = Depends(get_session)):
    try:
        prog_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID Program tidak valid")

    program = await session.get(RenstraProgram, prog_uuid)
    if not program:
        raise HTTPException(status_code=404, detail="Program tidak ditemukan")

    if data.kodeprogram is not None:
        program.kodeprogram = data.kodeprogram.strip()
    if data.uraiprogram is not None:
        program.uraiprogram = data.uraiprogram.strip()
    if data.kinerja is not None:
        program.kinerja = data.kinerja.strip()
        program.urai = data.kinerja.strip()
    if data.no is not None:
        program.no = data.no

    if data.sasaran_ids is not None:
        target_kodeskpd = (program.kodeskpd or "").strip()
        parent_kodeskpd = target_kodeskpd[:-4] + "0000" if len(target_kodeskpd) >= 22 else target_kodeskpd
        sasaran_tags = []
        for sid in data.sasaran_ids:
            clean_id = str(sid).strip()
            if len(clean_id) == 36:
                sasaran_tags.append(f"{parent_kodeskpd}{clean_id}")
            else:
                sasaran_tags.append(clean_id)
        program.renstra_sasaran = sasaran_tags

    session.add(program)
    await session.commit()
    await session.refresh(program)
    return {
        "success": True,
        "message": "Program berhasil diperbarui",
        "data": {
            "id": str(program.id),
            "kodeprogram": program.kodeprogram,
            "uraiprogram": program.uraiprogram,
            "kinerja": program.kinerja,
            "renstra_sasaran": program.renstra_sasaran,
        },
    }


@router.delete("/program/{id}", response_model=Dict[str, Any])
async def delete_program(id: str, session: AsyncSession = Depends(get_session)):
    try:
        prog_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID Program tidak valid")

    program = await session.get(RenstraProgram, prog_uuid)
    if not program:
        raise HTTPException(status_code=404, detail="Program tidak ditemukan")

    # Cascade delete child kegiatans & subkegiatans
    kegiatans = (await session.exec(
        select(RenstraKegiatan).where(
            RenstraKegiatan.kodeskpd == program.kodeskpd,
            RenstraKegiatan.kodeprogram == program.kodeprogram,
        )
    )).all()
    for k in kegiatans:
        # Delete subkegiatans
        subkegs = (await session.exec(
            select(RenstraSubkegiatan).where(
                RenstraSubkegiatan.kodeskpd == k.kodeskpd,
                RenstraSubkegiatan.kodekegiatan == k.kodekegiatan,
            )
        )).all()
        for sk in subkegs:
            await session.delete(sk)

        # Delete indikator kegiatan
        ind_kegs = (await session.exec(
            select(RenstraIndikatorKegiatan).where(
                RenstraIndikatorKegiatan.kodeskpd == k.kodeskpd,
                RenstraIndikatorKegiatan.kodekegiatan == k.kodekegiatan,
            )
        )).all()
        for ik in ind_kegs:
            await session.delete(ik)

        await session.delete(k)

    await session.delete(program)
    await session.commit()
    return {"success": True, "message": "Program dan seluruh turunannya berhasil dihapus"}


# =====================================================================
# 6. KEGIATAN CRUD
# =====================================================================

@router.post("/kegiatan", response_model=Dict[str, Any])
async def create_kegiatan(data: KegiatanCreate, session: AsyncSession = Depends(get_session)):
    kegiatan = RenstraKegiatan(
        kodepemda="3376",
        idperiode="20252029",
        kodeskpd=data.kodeskpd,
        kodebidang=data.kodebidang,
        kodeprogram=data.kodeprogram,
        kodekegiatan=data.kodekegiatan.strip(),
        uraikegiatan=data.uraikegiatan.strip(),
        kinerja=data.kinerja.strip() if data.kinerja else None,
        no=data.no or 1,
    )
    session.add(kegiatan)
    await session.commit()
    await session.refresh(kegiatan)
    return {
        "success": True,
        "message": "Kegiatan berhasil ditambahkan",
        "data": {
            "id": kegiatan.id,
            "kodekegiatan": kegiatan.kodekegiatan,
            "uraikegiatan": kegiatan.uraikegiatan,
            "kinerja": kegiatan.kinerja,
        },
    }


@router.put("/kegiatan/{id}", response_model=Dict[str, Any])
async def update_kegiatan(id: int, data: KegiatanUpdate, session: AsyncSession = Depends(get_session)):
    kegiatan = await session.get(RenstraKegiatan, id)
    if not kegiatan:
        raise HTTPException(status_code=404, detail="Kegiatan tidak ditemukan")

    if data.kodekegiatan is not None:
        kegiatan.kodekegiatan = data.kodekegiatan.strip()
    if data.uraikegiatan is not None:
        kegiatan.uraikegiatan = data.uraikegiatan.strip()
    if data.kinerja is not None:
        kegiatan.kinerja = data.kinerja.strip()
    if data.no is not None:
        kegiatan.no = data.no

    session.add(kegiatan)
    await session.commit()
    await session.refresh(kegiatan)
    return {
        "success": True,
        "message": "Kegiatan berhasil diperbarui",
        "data": {
            "id": kegiatan.id,
            "kodekegiatan": kegiatan.kodekegiatan,
            "uraikegiatan": kegiatan.uraikegiatan,
            "kinerja": kegiatan.kinerja,
        },
    }


@router.delete("/kegiatan/{id}", response_model=Dict[str, Any])
async def delete_kegiatan(id: int, session: AsyncSession = Depends(get_session)):
    kegiatan = await session.get(RenstraKegiatan, id)
    if not kegiatan:
        raise HTTPException(status_code=404, detail="Kegiatan tidak ditemukan")

    # Cascade delete child subkegiatans and indikator kegiatan
    subkegs = (await session.exec(
        select(RenstraSubkegiatan).where(
            RenstraSubkegiatan.kodeskpd == kegiatan.kodeskpd,
            RenstraSubkegiatan.kodekegiatan == kegiatan.kodekegiatan,
        )
    )).all()
    for sk in subkegs:
        await session.delete(sk)

    ind_kegs = (await session.exec(
        select(RenstraIndikatorKegiatan).where(
            RenstraIndikatorKegiatan.kodeskpd == kegiatan.kodeskpd,
            RenstraIndikatorKegiatan.kodekegiatan == kegiatan.kodekegiatan,
        )
    )).all()
    for ik in ind_kegs:
        await session.delete(ik)

    await session.delete(kegiatan)
    await session.commit()
    return {"success": True, "message": "Kegiatan dan seluruh turunannya berhasil dihapus"}


# =====================================================================
# 7. SUBKEGIATAN CRUD
# =====================================================================

@router.post("/subkegiatan", response_model=Dict[str, Any])
async def create_subkegiatan(data: SubkegiatanCreate, session: AsyncSession = Depends(get_session)):
    subkeg = RenstraSubkegiatan(
        kodepemda="3376",
        idperiode="20252029",
        kodeskpd=data.kodeskpd,
        kodebidang=data.kodebidang,
        kodeprogram=data.kodeprogram,
        kodekegiatan=data.kodekegiatan,
        kodesubkegiatan=data.kodesubkegiatan.strip(),
        uraisubkegiatan=data.uraisubkegiatan.strip(),
        kinerja=data.kinerja.strip() if data.kinerja else None,
        kodesubkegiatan_indikator=data.kodesubkegiatan_indikator or data.kodesubkegiatan.strip(),
        uraisubkegiatan_indikator=data.uraisubkegiatan_indikator.strip() if data.uraisubkegiatan_indikator else None,
        satuan=data.satuan or "-",
        status=data.status or "positif",
        volume_awal=data.volume_awal or "-",
        volume_0=data.volume_0 or "-",
        volume_1=data.volume_1 or "-",
        volume_2=data.volume_2 or "-",
        volume_3=data.volume_3 or "-",
        volume_4=data.volume_4 or "-",
        volume_5=data.volume_5 or "-",
        p_volume_0=data.p_volume_0 or "-",
        p_volume_1=data.p_volume_1 or "-",
        p_volume_2=data.p_volume_2 or "-",
        p_volume_3=data.p_volume_3 or "-",
        p_volume_4=data.p_volume_4 or "-",
        p_volume_5=data.p_volume_5 or "-",
        p_volume_akhir=data.p_volume_akhir or data.p_volume_4 or "-",
        realisasi0=data.realisasi2025 or "-",
        realisasi1=data.realisasi2026 or "-",
        realisasi2=data.realisasi2027 or "-",
        realisasi3=data.realisasi2028 or "-",
        realisasi4=data.realisasi2029 or "-",
        realisasi5=data.realisasi2030 or "-",
        perubahan_status=data.perubahan_status or "tetap",
        pagu1=data.pagu1 or 0.0,
        pagu2=data.pagu2 or 0.0,
        pagu3=data.pagu3 or 0.0,
        pagu4=data.pagu4 or 0.0,
        pagu5=data.pagu5 or 0.0,
        p_pagu1=data.p_pagu1 or 0.0,
        p_pagu2=data.p_pagu2 or 0.0,
        p_pagu3=data.p_pagu3 or 0.0,
        p_pagu4=data.p_pagu4 or 0.0,
        p_pagu5=data.p_pagu5 or 0.0,
        no=data.no or 1,
    )
    session.add(subkeg)
    await session.commit()
    await session.refresh(subkeg)
    return {
        "success": True,
        "message": "Subkegiatan berhasil ditambahkan",
        "data": {
            "id": subkeg.id,
            "kodesubkegiatan": subkeg.kodesubkegiatan,
            "uraisubkegiatan": subkeg.uraisubkegiatan,
            "kinerja": subkeg.kinerja,
        },
    }


@router.put("/subkegiatan/{id}", response_model=Dict[str, Any])
async def update_subkegiatan(id: int, data: SubkegiatanUpdate, session: AsyncSession = Depends(get_session)):
    subkeg = await session.get(RenstraSubkegiatan, id)
    if not subkeg:
        raise HTTPException(status_code=404, detail="Subkegiatan tidak ditemukan")

    if data.kodesubkegiatan is not None:
        subkeg.kodesubkegiatan = data.kodesubkegiatan.strip()
    if data.uraisubkegiatan is not None:
        subkeg.uraisubkegiatan = data.uraisubkegiatan.strip()
    if data.kinerja is not None:
        subkeg.kinerja = data.kinerja.strip()
    if data.kodesubkegiatan_indikator is not None:
        subkeg.kodesubkegiatan_indikator = data.kodesubkegiatan_indikator.strip()
    if data.uraisubkegiatan_indikator is not None:
        subkeg.uraisubkegiatan_indikator = data.uraisubkegiatan_indikator.strip()
    if data.satuan is not None:
        subkeg.satuan = data.satuan
    if data.status is not None:
        subkeg.status = data.status
    if data.volume_awal is not None:
        subkeg.volume_awal = data.volume_awal
    if data.volume_0 is not None:
        subkeg.volume_0 = data.volume_0
    if data.volume_1 is not None:
        subkeg.volume_1 = data.volume_1
    if data.volume_2 is not None:
        subkeg.volume_2 = data.volume_2
    if data.volume_3 is not None:
        subkeg.volume_3 = data.volume_3
    if data.volume_4 is not None:
        subkeg.volume_4 = data.volume_4
    if data.volume_5 is not None:
        subkeg.volume_5 = data.volume_5
    if data.p_volume_0 is not None:
        subkeg.p_volume_0 = data.p_volume_0
    if data.p_volume_1 is not None:
        subkeg.p_volume_1 = data.p_volume_1
    if data.p_volume_2 is not None:
        subkeg.p_volume_2 = data.p_volume_2
    if data.p_volume_3 is not None:
        subkeg.p_volume_3 = data.p_volume_3
    if data.p_volume_4 is not None:
        subkeg.p_volume_4 = data.p_volume_4
        subkeg.p_volume_akhir = data.p_volume_akhir or data.p_volume_4
    if data.p_volume_5 is not None:
        subkeg.p_volume_5 = data.p_volume_5
    if data.p_volume_akhir is not None:
        subkeg.p_volume_akhir = data.p_volume_akhir
    if data.realisasi2025 is not None:
        subkeg.realisasi0 = data.realisasi2025
    if data.realisasi2026 is not None:
        subkeg.realisasi1 = data.realisasi2026
    if data.realisasi2027 is not None:
        subkeg.realisasi2 = data.realisasi2027
    if data.realisasi2028 is not None:
        subkeg.realisasi3 = data.realisasi2028
    if data.realisasi2029 is not None:
        subkeg.realisasi4 = data.realisasi2029
    if data.realisasi2030 is not None:
        subkeg.realisasi5 = data.realisasi2030
    if data.perubahan_status is not None:
        subkeg.perubahan_status = data.perubahan_status
    if data.definisi_operasional is not None:
        subkeg.definisi_operasional = data.definisi_operasional.strip()
    if data.pagu1 is not None:
        subkeg.pagu1 = data.pagu1
    if data.pagu2 is not None:
        subkeg.pagu2 = data.pagu2
    if data.pagu3 is not None:
        subkeg.pagu3 = data.pagu3
    if data.pagu4 is not None:
        subkeg.pagu4 = data.pagu4
    if data.pagu5 is not None:
        subkeg.pagu5 = data.pagu5
    if data.p_pagu1 is not None:
        subkeg.p_pagu1 = data.p_pagu1
    if data.p_pagu2 is not None:
        subkeg.p_pagu2 = data.p_pagu2
    if data.p_pagu3 is not None:
        subkeg.p_pagu3 = data.p_pagu3
    if data.p_pagu4 is not None:
        subkeg.p_pagu4 = data.p_pagu4
    if data.p_pagu5 is not None:
        subkeg.p_pagu5 = data.p_pagu5
    if data.no is not None:
        subkeg.no = data.no

    session.add(subkeg)
    await session.commit()
    await session.refresh(subkeg)
    return {
        "success": True,
        "message": "Subkegiatan berhasil diperbarui",
        "data": {
            "id": subkeg.id,
            "kodesubkegiatan": subkeg.kodesubkegiatan,
            "uraisubkegiatan": subkeg.uraisubkegiatan,
            "kinerja": subkeg.kinerja,
        },
    }


@router.delete("/subkegiatan/{id}", response_model=Dict[str, Any])
async def delete_subkegiatan(id: int, session: AsyncSession = Depends(get_session)):
    subkeg = await session.get(RenstraSubkegiatan, id)
    if not subkeg:
        raise HTTPException(status_code=404, detail="Subkegiatan tidak ditemukan")

    await session.delete(subkeg)
    await session.commit()
    return {"success": True, "message": "Subkegiatan berhasil dihapus"}

