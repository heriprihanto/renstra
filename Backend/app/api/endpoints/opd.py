from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.core.db import get_session
from app.models.opd import TaOpd, TaSubPd
from app.schemas.opd import DashboardStats, OpdDetail, OpdListItem, SubPdDetail, SubPdItem

router = APIRouter(prefix="/opd", tags=["Perangkat Daerah"])


@router.get("", response_model=List[OpdListItem])
async def list_opd(
    search: Optional[str] = Query(default=None, description="Cari nama atau kode SKPD"),
    has_sub: Optional[bool] = Query(default=None, description="Filter SKPD yang memiliki sub unit"),
    session: AsyncSession = Depends(get_session),
):
    """
    Mengambil daftar seluruh Perangkat Daerah (ta_opd) beserta jumlah Sub SKPD.
    """
    # Query OPD with count of sub units via LEFT OUTER JOIN
    query = (
        select(
            TaOpd.id_skpd,
            TaOpd.kode_skpd,
            TaOpd.nama_skpd,
            func.count(TaSubPd.id_sub_skpd).label("sub_count"),
        )
        .outerjoin(TaSubPd, TaOpd.id_skpd == TaSubPd.id_skpd)
        .group_by(TaOpd.id_skpd, TaOpd.kode_skpd, TaOpd.nama_skpd)
        .order_by(TaOpd.kode_skpd.asc())
    )

    if search:
        search_term = f"%{search.strip()}%"
        query = query.where(
            (TaOpd.nama_skpd.ilike(search_term)) | (TaOpd.kode_skpd.ilike(search_term))
        )

    if has_sub is True:
        query = query.having(func.count(TaSubPd.id_sub_skpd) > 0)
    elif has_sub is False:
        query = query.having(func.count(TaSubPd.id_sub_skpd) == 0)

    results = (await session.exec(query)).all()

    items: List[OpdListItem] = []
    for row in results:
        items.append(
            OpdListItem(
                id_skpd=row.id_skpd,
                kode_skpd=row.kode_skpd,
                nama_skpd=row.nama_skpd,
                sub_count=row.sub_count,
            )
        )
    return items


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(session: AsyncSession = Depends(get_session)):
    """
    Mengambil statistik umum untuk dashboard eksekutif RENSTRA.
    """
    total_opd = (await session.exec(select(func.count(TaOpd.id_skpd)))).one() or 0
    total_sub_pd = (await session.exec(select(func.count(TaSubPd.id_sub_skpd)))).one() or 0

    # Count distinct opds that have at least 1 sub pd
    opd_with_sub = (
        (await session.exec(
            select(func.count(func.distinct(TaSubPd.id_skpd))).where(
                TaSubPd.id_skpd.isnot(None)
            )
        )).one()
        or 0
    )

    opd_without_sub = max(0, total_opd - opd_with_sub)

    return DashboardStats(
        total_opd=total_opd,
        total_sub_pd=total_sub_pd,
        opd_with_sub=opd_with_sub,
        opd_without_sub=opd_without_sub,
        tahun_anggaran=settings.TAHUN_ANGGARAN,
        project_name=settings.PROJECT_NAME,
    )


@router.get("/{id_skpd}", response_model=OpdDetail)
async def get_opd_detail(id_skpd: int, session: AsyncSession = Depends(get_session)):
    """
    Mengambil detail satu Perangkat Daerah beserta seluruh Sub SKPD terkait.
    """
    opd = await session.get(TaOpd, id_skpd)
    if not opd:
        raise HTTPException(status_code=404, detail="Perangkat Daerah tidak ditemukan")

    sub_units = (await session.exec(
        select(TaSubPd)
        .where(TaSubPd.id_skpd == id_skpd)
        .order_by(TaSubPd.kode_sub_skpd.asc())
    )).all()

    return OpdDetail(
        id_skpd=opd.id_skpd,
        kode_skpd=opd.kode_skpd,
        nama_skpd=opd.nama_skpd,
        sub_count=len(sub_units),
        sub_pd_list=[
            SubPdItem(
                id_sub_skpd=s.id_sub_skpd,
                id_skpd=s.id_skpd,
                kode_sub_skpd=s.kode_sub_skpd,
                nama_sub_skpd=s.nama_sub_skpd,
            )
            for s in sub_units
        ],
    )


@router.get("/{id_skpd}/sub", response_model=List[SubPdItem])
async def list_sub_pd_by_opd(
    id_skpd: int,
    search: Optional[str] = Query(default=None, description="Cari nama atau kode Sub SKPD"),
    session: AsyncSession = Depends(get_session),
):
    """
    Mengambil daftar Sub SKPD untuk Perangkat Daerah tertentu.
    """
    opd = await session.get(TaOpd, id_skpd)
    if not opd:
        raise HTTPException(status_code=404, detail="Perangkat Daerah tidak ditemukan")

    query = select(TaSubPd).where(TaSubPd.id_skpd == id_skpd).order_by(TaSubPd.kode_sub_skpd.asc())

    if search:
        term = f"%{search.strip()}%"
        query = query.where(
            (TaSubPd.nama_sub_skpd.ilike(term)) | (TaSubPd.kode_sub_skpd.ilike(term))
        )

    sub_units = (await session.exec(query)).all()
    return [
        SubPdItem(
            id_sub_skpd=s.id_sub_skpd,
            id_skpd=s.id_skpd,
            kode_sub_skpd=s.kode_sub_skpd,
            nama_sub_skpd=s.nama_sub_skpd,
        )
        for s in sub_units
    ]


@router.get("/sub/{id_sub_skpd}", response_model=SubPdDetail)
async def get_sub_pd_detail(id_sub_skpd: int, session: AsyncSession = Depends(get_session)):
    """
    Mengambil detail satu Sub SKPD beserta data SKPD induknya.
    """
    sub = await session.get(TaSubPd, id_sub_skpd)
    if not sub:
        raise HTTPException(status_code=404, detail="Sub SKPD tidak ditemukan")

    opd_dict = None
    if sub.id_skpd:
        opd = await session.get(TaOpd, sub.id_skpd)
        if opd:
            opd_dict = {
                "id_skpd": opd.id_skpd,
                "kode_skpd": opd.kode_skpd,
                "nama_skpd": opd.nama_skpd,
            }

    return SubPdDetail(
        id_sub_skpd=sub.id_sub_skpd,
        id_skpd=sub.id_skpd,
        kode_sub_skpd=sub.kode_sub_skpd,
        nama_sub_skpd=sub.nama_sub_skpd,
        opd=opd_dict,
    )

    return SubPdDetail(
        id_sub_skpd=sub.id_sub_skpd,
        id_skpd=sub.id_skpd,
        kode_sub_skpd=sub.kode_sub_skpd,
        nama_sub_skpd=sub.nama_sub_skpd,
        opd=opd_dict,
    )


from app.models.renstra import (
    RenstraIndikatorKegiatan,
    RenstraIndikatorProgram,
    RenstraIndikatorSasaran,
    RenstraIndikatorTujuan,
    RenstraKegiatan,
    RenstraOutputKegiatan,
    RenstraProgram,
    RenstraSasaran,
    RenstraSubkegiatan,
    RenstraTujuan,
)
from app.schemas.renstra import (
    IndikatorKegiatanItem,
    IndikatorProgramItem,
    IndikatorSubkegiatanItem,
    IndikatorTargetItem,
    KegiatanCascadingItem,
    OpdRenstraCascadingResponse,
    ProgramCascadingItem,
    SasaranCascadingItem,
    SubkegiatanCascadingItem,
    SubSkpdCascadingResponse,
    TujuanCascadingItem,
)


def evaluate_perubahan(
    explicit_status: Optional[str],
    target_awal: Optional[str],
    target1: Optional[str],
    target2: Optional[str],
    target3: Optional[str],
    target4: Optional[str],
    target5: Optional[str],
    p_target0: Optional[str],
    p_target1: Optional[str],
    p_target2: Optional[str],
    p_target3: Optional[str],
    p_target4: Optional[str],
    p_target5: Optional[str],
):
    def norm(v):
        if v is None:
            return "-"
        s = str(v).strip()
        return "-" if s in ("", "-") else s

    m_awal = norm(target_awal)
    m_1 = norm(target1)
    m_2 = norm(target2)
    m_3 = norm(target3)
    m_4 = norm(target4)
    m_5 = norm(target5)
    m_akhir = m_4

    p_0 = norm(p_target0)
    p_1 = norm(p_target1)
    p_2 = norm(p_target2)
    p_3 = norm(p_target3)
    p_4 = norm(p_target4)
    p_5 = norm(p_target5)
    p_akhir = p_4

    all_murni_empty = all(t == "-" for t in [m_awal, m_1, m_2, m_3, m_4, m_5])
    has_any_perubahan = any(pt != "-" for pt in [p_0, p_1, p_2, p_3, p_4, p_5])

    pairs = [
        ("2025", m_awal, p_0),
        ("2026", m_1, p_1),
        ("2027", m_2, p_2),
        ("2028", m_3, p_3),
        ("2029", m_4, p_4),
        ("2030", m_5, p_5),
        ("akhir", m_akhir, p_akhir),
    ]

    changed_targets = []
    for key, m_val, p_val in pairs:
        if p_val != "-" and p_val != m_val:
            changed_targets.append(key)

    is_baru = False
    is_perubahan = False
    status = "tetap"

    if explicit_status in ("baru", "data_baru"):
        is_baru = True
        status = "baru"
    elif explicit_status in ("perubahan", "berubah"):
        is_perubahan = True
        status = "perubahan"
    elif all_murni_empty and has_any_perubahan:
        is_baru = True
        status = "baru"
    elif len(changed_targets) > 0:
        is_perubahan = True
        status = "perubahan"

    return status, is_baru, is_perubahan, changed_targets


@router.get("/{id_skpd}/renstra-cascading", response_model=OpdRenstraCascadingResponse)
async def get_opd_renstra_cascading(id_skpd: int, session: AsyncSession = Depends(get_session)):
    """
    Mengambil data cascading RENSTRA: Tujuan -> Indikator Tujuan -> Sasaran -> Indikator Sasaran
    lengkap dengan target tahunan (Awal, 2026, 2027, 2028, 2029, Akhir) dan penanda perubahan / data baru.
    """
    opd = await session.get(TaOpd, id_skpd)
    if not opd:
        raise HTTPException(status_code=404, detail="Perangkat Daerah tidak ditemukan")

    # Ambil Tujuan berdasarkan kodeskpd
    tujuan_rows = (await session.exec(
        select(RenstraTujuan)
        .where(RenstraTujuan.kodeskpd == opd.kode_skpd)
        .order_by(RenstraTujuan.no_urut.asc())
    )).all()

    tujuan_items: List[TujuanCascadingItem] = []
    total_sasaran = 0
    total_indikator_all = 0
    total_indikator_perubahan_all = 0
    total_indikator_baru_all = 0

    for t in tujuan_rows:
        # Ambil indikator tujuan
        ind_tujuan_rows = (await session.exec(
            select(RenstraIndikatorTujuan)
            .where(RenstraIndikatorTujuan.idtujuan == t.idtujuan)
            .order_by(RenstraIndikatorTujuan.urut.asc(), RenstraIndikatorTujuan.no_urut.asc())
        )).all()

        tujuan_perubahan_count = 0
        tujuan_baru_count = 0

        ind_tujuan_list: List[IndikatorTargetItem] = []
        for it in ind_tujuan_rows:
            total_indikator_all += 1
            status_calc, is_baru, is_perubahan, changed_targets = evaluate_perubahan(
                explicit_status=it.perubahan_status,
                target_awal=it.target_awal,
                target1=it.target1,
                target2=it.target2,
                target3=it.target3,
                target4=it.target4,
                target5=it.target5,
                p_target0=it.p_target0,
                p_target1=it.p_target1,
                p_target2=it.p_target2,
                p_target3=it.p_target3,
                p_target4=it.p_target4,
                p_target5=it.p_target5,
            )
            if is_perubahan:
                tujuan_perubahan_count += 1
                total_indikator_perubahan_all += 1
            if is_baru:
                tujuan_baru_count += 1
                total_indikator_baru_all += 1

            ind_tujuan_list.append(
                IndikatorTargetItem(
                    id=str(it.idtujuan_indikator),
                    uraian=it.uraitujuan_indikator or "-",
                    satuan=it.satuan or "-",
                    status=it.status or "-",
                    iku=it.iku or "0",
                    perubahan_status=status_calc,
                    is_baru=is_baru,
                    is_perubahan=is_perubahan,
                    changed_targets=changed_targets,
                    definisi_operasional=it.definisi_operasional or "-",
                    target_awal=it.target_awal or "-",  # Baseline
                    target2026=it.target1 or "-",       # t1: 2026
                    target2027=it.target2 or "-",       # t2: 2027
                    target2028=it.target3 or "-",       # t3: 2028
                    target2029=it.target4 or "-",       # t4: 2029
                    target2030=it.target5 or "-",       # t5: 2030
                    target_akhir=it.target4 or "-",      # Target Akhir memakai tahun 2029 (t4)
                    p_target2025=it.p_target0 or "-",
                    p_target2026=it.p_target1 or "-",
                    p_target2027=it.p_target2 or "-",
                    p_target2028=it.p_target3 or "-",
                    p_target2029=it.p_target4 or "-",
                    p_target2030=it.p_target5 or "-",
                    p_target_akhir=it.p_target4 or "-",
                )
            )

        # Ambil sasaran
        sasaran_rows = (await session.exec(
            select(RenstraSasaran)
            .where(RenstraSasaran.idtujuan == t.idtujuan)
            .order_by(RenstraSasaran.urut.asc(), RenstraSasaran.no.asc())
        )).all()

        sasaran_items: List[SasaranCascadingItem] = []
        for s in sasaran_rows:
            total_sasaran += 1
            # Ambil indikator sasaran
            ind_sasaran_rows = (await session.exec(
                select(RenstraIndikatorSasaran)
                .where(RenstraIndikatorSasaran.idsasaran == s.idsasaran)
                .order_by(RenstraIndikatorSasaran.urut.asc(), RenstraIndikatorSasaran.no.asc())
            )).all()

            sasaran_perubahan_count = 0
            sasaran_baru_count = 0

            ind_sasaran_list: List[IndikatorTargetItem] = []
            for isas in ind_sasaran_rows:
                total_indikator_all += 1
                status_calc, is_baru, is_perubahan, changed_targets = evaluate_perubahan(
                    explicit_status=isas.perubahan_status,
                    target_awal=isas.target_awal,
                    target1=isas.target1,
                    target2=isas.target2,
                    target3=isas.target3,
                    target4=isas.target4,
                    target5=isas.target5,
                    p_target0=isas.p_target0,
                    p_target1=isas.p_target1,
                    p_target2=isas.p_target2,
                    p_target3=isas.p_target3,
                    p_target4=isas.p_target4,
                    p_target5=isas.p_target5,
                )
                if is_perubahan:
                    sasaran_perubahan_count += 1
                    tujuan_perubahan_count += 1
                    total_indikator_perubahan_all += 1
                if is_baru:
                    sasaran_baru_count += 1
                    tujuan_baru_count += 1
                    total_indikator_baru_all += 1

                ind_sasaran_list.append(
                    IndikatorTargetItem(
                        id=str(isas.idsasaran_indikator),
                        uraian=isas.uraisasaran_indikator or "-",
                        satuan=isas.satuan or "-",
                        status=isas.status or "-",
                        iku=isas.iku or "0",
                        perubahan_status=status_calc,
                        is_baru=is_baru,
                        is_perubahan=is_perubahan,
                        changed_targets=changed_targets,
                        definisi_operasional=isas.definisi_operasional or "-",
                        target_awal=isas.target_awal or "-",  # Baseline
                        target2026=isas.target1 or "-",       # t1: 2026
                        target2027=isas.target2 or "-",       # t2: 2027
                        target2028=isas.target3 or "-",       # t3: 2028
                        target2029=isas.target4 or "-",       # t4: 2029
                        target2030=isas.target5 or "-",       # t5: 2030
                        target_akhir=isas.target4 or "-",      # Target Akhir memakai tahun 2029 (t4)
                        p_target2025=isas.p_target0 or "-",
                        p_target2026=isas.p_target1 or "-",
                        p_target2027=isas.p_target2 or "-",
                        p_target2028=isas.p_target3 or "-",
                        p_target2029=isas.p_target4 or "-",
                        p_target2030=isas.p_target5 or "-",
                        p_target_akhir=isas.p_target4 or "-",
                    )
                )

            sasaran_is_baru = (s.perubahan_status == "baru") or (sasaran_baru_count > 0 and sasaran_perubahan_count == 0 and len(ind_sasaran_rows) == sasaran_baru_count)

            sasaran_items.append(
                SasaranCascadingItem(
                    idsasaran=str(s.idsasaran),
                    uraisasaran=s.uraisasaran or "-",
                    no_urut=s.urut or s.no,
                    perubahan_status=s.perubahan_status or ("baru" if sasaran_is_baru else ("perubahan" if sasaran_perubahan_count > 0 else "tetap")),
                    is_baru=sasaran_is_baru,
                    total_perubahan=sasaran_perubahan_count,
                    total_baru=sasaran_baru_count,
                    indikator_sasaran=ind_sasaran_list,
                )
            )

        tujuan_is_baru = (t.perubahan_status == "baru")

        tujuan_items.append(
            TujuanCascadingItem(
                idtujuan=str(t.idtujuan),
                uraitujuan=t.uraitujuan or "-",
                no_urut=t.no_urut,
                perubahan_status=t.perubahan_status or ("baru" if tujuan_is_baru else ("perubahan" if tujuan_perubahan_count > 0 else "tetap")),
                is_baru=tujuan_is_baru,
                total_perubahan=tujuan_perubahan_count,
                total_baru=tujuan_baru_count,
                indikator_tujuan=ind_tujuan_list,
                sasaran=sasaran_items,
            )
        )

    return OpdRenstraCascadingResponse(
        id_skpd=opd.id_skpd,
        kode_skpd=opd.kode_skpd or "-",
        nama_skpd=opd.nama_skpd or "-",
        total_tujuan=len(tujuan_items),
        total_sasaran=total_sasaran,
        total_indikator=total_indikator_all,
        total_indikator_perubahan=total_indikator_perubahan_all,
        total_indikator_baru=total_indikator_baru_all,
        tujuan_list=tujuan_items,
    )


# =====================================================================
# CASCADING PROGRAM / KEGIATAN / SUBKEGIATAN (SUB SKPD)
# =====================================================================

@router.get("/sub/{id_sub_skpd}/cascading", response_model=SubSkpdCascadingResponse)
async def get_sub_skpd_cascading(id_sub_skpd: int, session: AsyncSession = Depends(get_session)):
    """
    Mengambil data cascading Program -> Indikator Program -> Kegiatan -> Indikator Kegiatan -> Subkegiatan -> Indikator Subkegiatan
    berdasarkan id_sub_skpd dari ta_sub_pd.
    """
    sub = await session.get(TaSubPd, id_sub_skpd)
    if not sub:
        raise HTTPException(status_code=404, detail="Sub SKPD tidak ditemukan")

    opd = (await session.get(TaOpd, sub.id_skpd)) if sub.id_skpd else None
    kode_sub = sub.kode_sub_skpd

    # Query Programs
    programs = (await session.exec(
        select(RenstraProgram)
        .where(RenstraProgram.kodeskpd == kode_sub)
        .order_by(RenstraProgram.no.asc(), RenstraProgram.kodeprogram.asc())
    )).all()

    total_kegiatan = 0
    total_subkegiatan = 0
    total_indikator_program = 0
    total_pagu = 0.0
    total_p_pagu = 0.0

    program_items: List[ProgramCascadingItem] = []

    for p in programs:
        # 1. Indikator Program
        ind_prog_rows = (await session.exec(
            select(RenstraIndikatorProgram)
            .where(
                RenstraIndikatorProgram.kodeskpd == kode_sub,
                RenstraIndikatorProgram.kodeprogram == p.kodeprogram,
            )
            .order_by(
                RenstraIndikatorProgram.no.asc(),
                RenstraIndikatorProgram.urut.asc(),
                RenstraIndikatorProgram.id.asc(),
            )
        )).all()

        ind_prog_items: List[IndikatorProgramItem] = []
        for ip in ind_prog_rows:
            total_indikator_program += 1
            ip_status, ip_baru, ip_perubahan, ip_changed = evaluate_perubahan(
                explicit_status=ip.perubahan_status,
                target_awal=ip.target_awal,
                target1=ip.target1,
                target2=ip.target2,
                target3=ip.target3,
                target4=ip.target4,
                target5=ip.target5,
                p_target0=ip.p_target0,
                p_target1=ip.p_target1,
                p_target2=ip.p_target2,
                p_target3=ip.p_target3,
                p_target4=ip.p_target4,
                p_target5=ip.p_target5,
            )
            ind_prog_items.append(
                IndikatorProgramItem(
                    id=ip.id,
                    uraian=ip.uraiindikator or "-",
                    satuan=ip.satuan or "-",
                    status=ip.status or "-",
                    target_awal=ip.target_awal or "-",
                    target2026=ip.target1 or "-",
                    target2027=ip.target2 or "-",
                    target2028=ip.target3 or "-",
                    target2029=ip.target4 or "-",
                    target2030=ip.target5 or "-",
                    target_akhir=ip.target4 or "-",
                    p_target2025=ip.p_target0 or "-",
                    p_target2026=ip.p_target1 or "-",
                    p_target2027=ip.p_target2 or "-",
                    p_target2028=ip.p_target3 or "-",
                    p_target2029=ip.p_target4 or "-",
                    p_target2030=ip.p_target5 or "-",
                    p_target_akhir=ip.p_target_akhir or ip.p_target4 or "-",
                    perubahan_status=ip_status,
                    is_baru=ip_baru,
                    is_perubahan=ip_perubahan,
                    changed_targets=ip_changed,
                )
            )

        # 2. Kegiatan
        keg_rows = (await session.exec(
            select(RenstraKegiatan)
            .where(
                RenstraKegiatan.kodeskpd == kode_sub,
                RenstraKegiatan.kodeprogram == p.kodeprogram,
            )
            .order_by(RenstraKegiatan.no.asc(), RenstraKegiatan.kodekegiatan.asc())
        )).all()

        keg_items: List[KegiatanCascadingItem] = []
        for k in keg_rows:
            total_kegiatan += 1

            # 2.1 Indikator Kegiatan
            ind_keg_rows = (await session.exec(
                select(RenstraIndikatorKegiatan)
                .where(
                    RenstraIndikatorKegiatan.kodeskpd == kode_sub,
                    RenstraIndikatorKegiatan.kodekegiatan == k.kodekegiatan,
                )
                .order_by(RenstraIndikatorKegiatan.no.asc(), RenstraIndikatorKegiatan.urut.asc(), RenstraIndikatorKegiatan.id.asc())
            )).all()

            ind_keg_items: List[IndikatorKegiatanItem] = []
            for ik in ind_keg_rows:
                status_calc, is_baru, is_perubahan, changed_targets = evaluate_perubahan(
                    explicit_status=ik.perubahan_status,
                    target_awal=ik.target_awal,
                    target1=ik.target1,
                    target2=ik.target2,
                    target3=ik.target3,
                    target4=ik.target4,
                    target5=ik.target5,
                    p_target0=ik.p_target0,
                    p_target1=ik.p_target1,
                    p_target2=ik.p_target2,
                    p_target3=ik.p_target3,
                    p_target4=ik.p_target4,
                    p_target5=ik.p_target5,
                )

                ind_keg_items.append(
                    IndikatorKegiatanItem(
                        id=str(ik.id),
                        kodekegiatan=ik.kodekegiatan,
                        kodeskpd=ik.kodeskpd,
                        uraian=ik.uraiindikator or "-",
                        satuan=ik.satuan or "-",
                        status=ik.status or "-",
                        iku=ik.iku or "0",
                        perubahan_status=status_calc,
                        is_baru=is_baru,
                        is_perubahan=is_perubahan,
                        changed_targets=changed_targets,
                        definisi_operasional=ik.definisi_operasional or "-",
                        target_awal=ik.target_awal or "-",
                        target2026=ik.target1 or "-",
                        target2027=ik.target2 or "-",
                        target2028=ik.target3 or "-",
                        target2029=ik.target4 or "-",
                        target2030=ik.target5 or "-",
                        target_akhir=ik.target_akhir or ik.target4 or "-",
                        p_target2025=ik.p_target0 or "-",
                        p_target2026=ik.p_target1 or "-",
                        p_target2027=ik.p_target2 or "-",
                        p_target2028=ik.p_target3 or "-",
                        p_target2029=ik.p_target4 or "-",
                        p_target2030=ik.p_target5 or "-",
                        p_target_akhir=ik.p_target_akhir or ik.p_target4 or "-",
                        pagu1=float(ik.pagu1 or 0),
                        pagu2=float(ik.pagu2 or 0),
                        pagu3=float(ik.pagu3 or 0),
                        pagu4=float(ik.pagu4 or 0),
                        pagu5=float(ik.pagu5 or 0),
                        p_pagu1=float(ik.p_pagu1 or 0),
                        p_pagu2=float(ik.p_pagu2 or 0),
                        p_pagu3=float(ik.p_pagu3 or 0),
                        p_pagu4=float(ik.p_pagu4 or 0),
                        p_pagu5=float(ik.p_pagu5 or 0),
                    )
                )

            # 2.2 Subkegiatan
            subkeg_rows = (await session.exec(
                select(RenstraSubkegiatan)
                .where(
                    RenstraSubkegiatan.kodeskpd == kode_sub,
                    RenstraSubkegiatan.kodekegiatan == k.kodekegiatan,
                )
                .order_by(RenstraSubkegiatan.no.asc(), RenstraSubkegiatan.kodesubkegiatan.asc())
            )).all()

            subkeg_items: List[SubkegiatanCascadingItem] = []
            for sk in subkeg_rows:
                total_subkegiatan += 1
                sk_pagu1 = float(sk.pagu1 or 0)
                sk_pagu2 = float(sk.pagu2 or 0)
                sk_pagu3 = float(sk.pagu3 or 0)
                sk_pagu4 = float(sk.pagu4 or 0)
                sk_pagu5 = float(sk.pagu5 or 0)

                sk_p_pagu1 = float(sk.p_pagu1 or 0)
                sk_p_pagu2 = float(sk.p_pagu2 or 0)
                sk_p_pagu3 = float(sk.p_pagu3 or 0)
                sk_p_pagu4 = float(sk.p_pagu4 or 0)
                sk_p_pagu5 = float(sk.p_pagu5 or 0)

                # Indikator Subkegiatan (stored directly on row)
                ind_sub_item = None
                if sk.uraisubkegiatan_indikator or sk.kodesubkegiatan_indikator:
                    sk_status, sk_baru, sk_perubahan, sk_changed = evaluate_perubahan(
                        explicit_status=sk.perubahan_status,
                        target_awal=sk.volume_awal,
                        target1=sk.volume_1,
                        target2=sk.volume_2,
                        target3=sk.volume_3,
                        target4=sk.volume_4,
                        target5=sk.volume_5,
                        p_target0=sk.p_volume_0,
                        p_target1=sk.p_volume_1,
                        p_target2=sk.p_volume_2,
                        p_target3=sk.p_volume_3,
                        p_target4=sk.p_volume_4,
                        p_target5=sk.p_volume_5,
                    )
                    ind_sub_item = IndikatorSubkegiatanItem(
                        id=sk.id,
                        kode=sk.kodesubkegiatan_indikator or "-",
                        uraian=sk.uraisubkegiatan_indikator or "-",
                        satuan=sk.satuan or "-",
                        status=sk.status or "-",
                        volume_awal=sk.volume_awal or "-",
                        volume_0=sk.volume_0 or "-",
                        volume_1=sk.volume_1 or "-",
                        volume_2=sk.volume_2 or "-",
                        volume_3=sk.volume_3 or "-",
                        volume_4=sk.volume_4 or "-",
                        volume_5=sk.volume_5 or "-",
                        volume_akhir=sk.volume_4 or "-",
                        p_volume_0=sk.p_volume_0 or "-",
                        p_volume_1=sk.p_volume_1 or "-",
                        p_volume_2=sk.p_volume_2 or "-",
                        p_volume_3=sk.p_volume_3 or "-",
                        p_volume_4=sk.p_volume_4 or "-",
                        p_volume_5=sk.p_volume_5 or "-",
                        p_volume_akhir=sk.p_volume_akhir or sk.p_volume_4 or "-",
                        perubahan_status=sk_status,
                        is_baru=sk_baru,
                        is_perubahan=sk_perubahan,
                        changed_targets=sk_changed,
                        pagu1=sk_pagu1,
                        pagu2=sk_pagu2,
                        pagu3=sk_pagu3,
                        pagu4=sk_pagu4,
                        pagu5=sk_pagu5,
                        p_pagu1=sk_p_pagu1,
                        p_pagu2=sk_p_pagu2,
                        p_pagu3=sk_p_pagu3,
                        p_pagu4=sk_p_pagu4,
                        p_pagu5=sk_p_pagu5,
                    )

                subkeg_items.append(
                    SubkegiatanCascadingItem(
                        id=sk.id,
                        kodesubkegiatan=sk.kodesubkegiatan or "-",
                        uraisubkegiatan=sk.uraisubkegiatan or "-",
                        kinerja=sk.kinerja or "-",
                        kodebidang=sk.kodebidang,
                        kodeprogram=sk.kodeprogram,
                        kodekegiatan=sk.kodekegiatan,
                        pagu1=sk_pagu1,
                        pagu2=sk_pagu2,
                        pagu3=sk_pagu3,
                        pagu4=sk_pagu4,
                        pagu5=sk_pagu5,
                        p_pagu1=sk_p_pagu1,
                        p_pagu2=sk_p_pagu2,
                        p_pagu3=sk_p_pagu3,
                        p_pagu4=sk_p_pagu4,
                        p_pagu5=sk_p_pagu5,
                        indikator=ind_sub_item,
                    )
                )

            # Hitung Pagu Kegiatan dari Indikator atau Subkegiatan
            ind_pagu_sum = sum((ik.pagu1 or 0) for ik in ind_keg_items)
            if ind_pagu_sum > 0:
                k_pagu1 = sum(ik.pagu1 or 0 for ik in ind_keg_items)
                k_pagu2 = sum(ik.pagu2 or 0 for ik in ind_keg_items)
                k_pagu3 = sum(ik.pagu3 or 0 for ik in ind_keg_items)
                k_pagu4 = sum(ik.pagu4 or 0 for ik in ind_keg_items)
                k_pagu5 = sum(ik.pagu5 or 0 for ik in ind_keg_items)
            else:
                k_pagu1 = sum(sk.pagu1 or 0 for sk in subkeg_items)
                k_pagu2 = sum(sk.pagu2 or 0 for sk in subkeg_items)
                k_pagu3 = sum(sk.pagu3 or 0 for sk in subkeg_items)
                k_pagu4 = sum(sk.pagu4 or 0 for sk in subkeg_items)
                k_pagu5 = sum(sk.pagu5 or 0 for sk in subkeg_items)

            ind_p_pagu_sum = sum((ik.p_pagu1 or 0) for ik in ind_keg_items)
            if ind_p_pagu_sum > 0:
                k_p_pagu1 = sum(ik.p_pagu1 or 0 for ik in ind_keg_items)
                k_p_pagu2 = sum(ik.p_pagu2 or 0 for ik in ind_keg_items)
                k_p_pagu3 = sum(ik.p_pagu3 or 0 for ik in ind_keg_items)
                k_p_pagu4 = sum(ik.p_pagu4 or 0 for ik in ind_keg_items)
                k_p_pagu5 = sum(ik.p_pagu5 or 0 for ik in ind_keg_items)
            else:
                k_p_pagu1 = sum(sk.p_pagu1 or 0 for sk in subkeg_items)
                k_p_pagu2 = sum(sk.p_pagu2 or 0 for sk in subkeg_items)
                k_p_pagu3 = sum(sk.p_pagu3 or 0 for sk in subkeg_items)
                k_p_pagu4 = sum(sk.p_pagu4 or 0 for sk in subkeg_items)
                k_p_pagu5 = sum(sk.p_pagu5 or 0 for sk in subkeg_items)

            keg_items.append(
                KegiatanCascadingItem(
                    id=k.id,
                    kodekegiatan=k.kodekegiatan or "-",
                    uraikegiatan=k.uraikegiatan or "-",
                    kinerja=k.kinerja or "-",
                    kodeprogram=k.kodeprogram,
                    pagu1=k_pagu1,
                    pagu2=k_pagu2,
                    pagu3=k_pagu3,
                    pagu4=k_pagu4,
                    pagu5=k_pagu5,
                    p_pagu1=k_p_pagu1,
                    p_pagu2=k_p_pagu2,
                    p_pagu3=k_p_pagu3,
                    p_pagu4=k_p_pagu4,
                    p_pagu5=k_p_pagu5,
                    indikator_kegiatan=ind_keg_items,
                    subkegiatan=subkeg_items,
                )
            )

        p_pagu1 = sum(k.pagu1 or 0 for k in keg_items)
        p_pagu2 = sum(k.pagu2 or 0 for k in keg_items)
        p_pagu3 = sum(k.pagu3 or 0 for k in keg_items)
        p_pagu4 = sum(k.pagu4 or 0 for k in keg_items)
        p_pagu5 = sum(k.pagu5 or 0 for k in keg_items)
        total_pagu += (p_pagu1 + p_pagu2 + p_pagu3 + p_pagu4 + p_pagu5)

        p_p_pagu1 = sum(k.p_pagu1 or 0 for k in keg_items)
        p_p_pagu2 = sum(k.p_pagu2 or 0 for k in keg_items)
        p_p_pagu3 = sum(k.p_pagu3 or 0 for k in keg_items)
        p_p_pagu4 = sum(k.p_pagu4 or 0 for k in keg_items)
        p_p_pagu5 = sum(k.p_pagu5 or 0 for k in keg_items)
        total_p_pagu += (p_p_pagu1 + p_p_pagu2 + p_p_pagu3 + p_p_pagu4 + p_p_pagu5)

        program_items.append(
            ProgramCascadingItem(
                id=str(p.id),
                kodeprogram=p.kodeprogram or "-",
                uraiprogram=p.uraiprogram or "-",
                kinerja=p.kinerja or p.urai or "-",
                pagu1=p_pagu1,
                pagu2=p_pagu2,
                pagu3=p_pagu3,
                pagu4=p_pagu4,
                pagu5=p_pagu5,
                p_pagu1=p_p_pagu1,
                p_pagu2=p_p_pagu2,
                p_pagu3=p_p_pagu3,
                p_pagu4=p_p_pagu4,
                p_pagu5=p_p_pagu5,
                indikator_program=ind_prog_items,
                kegiatan=keg_items,
            )
        )

    return SubSkpdCascadingResponse(
        id_sub_skpd=sub.id_sub_skpd,
        id_skpd=sub.id_skpd or 0,
        kode_sub_skpd=sub.kode_sub_skpd or "-",
        nama_sub_skpd=sub.nama_sub_skpd or "-",
        nama_skpd=opd.nama_skpd if opd else None,
        total_program=len(program_items),
        total_kegiatan=total_kegiatan,
        total_subkegiatan=total_subkegiatan,
        total_indikator_program=total_indikator_program,
        total_pagu=total_pagu,
        total_p_pagu=total_p_pagu,
        program_list=program_items,
    )


