import io
import re
from typing import Any, Dict, List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from app.models.opd import TaOpd, TaSubPd
from app.models.renstra import (
    RefSubkegiatan,
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


def format_target_val(val: Optional[str]) -> str:
    """Format target value for display while preserving decimals or dash."""
    if val is None or val == "" or str(val).strip() == "-":
        return "-"
    s_val = str(val).strip()
    try:
        # Check if float/int
        f = float(s_val.replace(",", "."))
        if f.is_integer() and abs(f) >= 1000:
            # Thousands format for large numbers (e.g. 91.000.000)
            return f"{int(f):,}".replace(",", ".")
        elif not f.is_integer() and abs(f) >= 1000:
            parts = f"{f:,.2f}".split(".")
            int_part = parts[0].replace(",", ".")
            dec_part = parts[1]
            return f"{int_part},{dec_part}"
        elif "," not in s_val and "." in s_val:
            # Replace dot with comma for Indonesian standard if < 1000 (e.g. 94.12 -> 94,12)
            # but keep original string precision
            return s_val.replace(".", ",")
        return s_val
    except Exception:
        return s_val


async def get_tujuan_sasaran_report_data(
    session: AsyncSession, id_skpd: int, tipe: str = "murni"
) -> Dict[str, Any]:
    """Fetch structured Tujuan and Sasaran data for a given OPD."""
    # 1. Fetch OPD
    opd = await session.get(TaOpd, id_skpd)
    if not opd:
        raise ValueError(f"Perangkat Daerah dengan ID {id_skpd} tidak ditemukan")

    kode_skpd = opd.kode_skpd

    # 2. Fetch Tujuan
    stmt_tujuan = (
        select(RenstraTujuan)
        .where(RenstraTujuan.kodeskpd == kode_skpd)
        .order_by(RenstraTujuan.no_urut, RenstraTujuan.idtujuan)
    )
    res_tujuan = await session.exec(stmt_tujuan)
    tujuans = res_tujuan.all()

    use_perubahan = tipe.lower() == "perubahan"

    tujuan_list = []
    for idx_t, t in enumerate(tujuans, 1):
        # 3. Fetch Indikator Tujuan
        stmt_ind_tujuan = (
            select(RenstraIndikatorTujuan)
            .where(RenstraIndikatorTujuan.idtujuan == t.idtujuan)
            .order_by(
                RenstraIndikatorTujuan.no_urut,
                RenstraIndikatorTujuan.urut,
                RenstraIndikatorTujuan.idtujuan_indikator,
            )
        )
        res_ind_tujuan = await session.exec(stmt_ind_tujuan)
        ind_tujuans = res_ind_tujuan.all()

        indikator_tujuan_data = []
        for it_idx, it in enumerate(ind_tujuans, 1):
            t0 = it.p_target0 if use_perubahan and it.p_target0 else (it.target0 or "-")
            t1 = it.p_target1 if use_perubahan and it.p_target1 else (it.target1 or "-")
            t2 = it.p_target2 if use_perubahan and it.p_target2 else (it.target2 or "-")
            t3 = it.p_target3 if use_perubahan and it.p_target3 else (it.target3 or "-")
            t4 = it.p_target4 if use_perubahan and it.p_target4 else (it.target4 or "-")
            t5 = it.p_target5 if use_perubahan and it.p_target5 else (it.target5 or "-")

            # Metadata / Definisi Operasional di kolom Ket
            meta_it = it.definisi_operasional if (it.definisi_operasional and it.definisi_operasional.strip() and it.definisi_operasional.strip() != "-") else "-"

            indikator_tujuan_data.append({
                "no_label": f"Indikator Tujuan - {it_idx}",
                "uraian": it.uraitujuan_indikator or "-",
                "satuan": it.satuan or "-",
                "target_awal": format_target_val(it.target_awal),
                "target0": format_target_val(t0),
                "target1": format_target_val(t1),
                "target2": format_target_val(t2),
                "target3": format_target_val(t3),
                "target4": format_target_val(t4),
                "target5": format_target_val(t5),
                "ket": meta_it,
            })

        # 4. Fetch Sasaran
        stmt_sasaran = (
            select(RenstraSasaran)
            .where(RenstraSasaran.idtujuan == t.idtujuan)
            .order_by(
                RenstraSasaran.no,
                RenstraSasaran.urut,
                RenstraSasaran.idsasaran,
            )
        )
        res_sasaran = await session.exec(stmt_sasaran)
        sasarans = res_sasaran.all()

        sasaran_data_list = []
        for s_idx, s in enumerate(sasarans, 1):
            # 5. Fetch Indikator Sasaran
            stmt_ind_sas = (
                select(RenstraIndikatorSasaran)
                .where(RenstraIndikatorSasaran.idsasaran == s.idsasaran)
                .order_by(
                    RenstraIndikatorSasaran.no,
                    RenstraIndikatorSasaran.urut,
                    RenstraIndikatorSasaran.idsasaran_indikator,
                )
            )
            res_ind_sas = await session.exec(stmt_ind_sas)
            ind_sasarans = res_ind_sas.all()

            indikator_sasaran_data = []
            for is_idx, isas in enumerate(ind_sasarans, 1):
                st0 = isas.p_target0 if use_perubahan and isas.p_target0 else (isas.target0 or "-")
                st1 = isas.p_target1 if use_perubahan and isas.p_target1 else (isas.target1 or "-")
                st2 = isas.p_target2 if use_perubahan and isas.p_target2 else (isas.target2 or "-")
                st3 = isas.p_target3 if use_perubahan and isas.p_target3 else (isas.target3 or "-")
                st4 = isas.p_target4 if use_perubahan and isas.p_target4 else (isas.target4 or "-")
                st5 = isas.p_target5 if use_perubahan and isas.p_target5 else (isas.target5 or "-")

                # Metadata / Definisi Operasional di kolom Ket
                meta_isas = isas.definisi_operasional if (isas.definisi_operasional and isas.definisi_operasional.strip() and isas.definisi_operasional.strip() != "-") else "-"

                indikator_sasaran_data.append({
                    "no_label": f"Indikator Sasaran - {is_idx}",
                    "uraian": isas.uraisasaran_indikator or "-",
                    "satuan": isas.satuan or "-",
                    "target_awal": format_target_val(isas.target_awal),
                    "target0": format_target_val(st0),
                    "target1": format_target_val(st1),
                    "target2": format_target_val(st2),
                    "target3": format_target_val(st3),
                    "target4": format_target_val(st4),
                    "target5": format_target_val(st5),
                    "ket": meta_isas,
                })

            sasaran_data_list.append({
                "no_label": f"Sasaran-{s_idx}",
                "uraisasaran": s.uraisasaran or "-",
                "indikator_list": indikator_sasaran_data,
            })

        tujuan_list.append({
            "no": t.no_urut or idx_t,
            "uraitujuan": t.uraitujuan or "-",
            "indikator_tujuan_list": indikator_tujuan_data,
            "sasaran_list": sasaran_data_list,
        })

    return {
        "opd": {
            "id_skpd": opd.id_skpd,
            "kode_skpd": opd.kode_skpd,
            "nama_skpd": opd.nama_skpd,
        },
        "tipe": "perubahan" if use_perubahan else "murni",
        "tahun_awal": 2025,
        "tahun_akhir": 2029,
        "kondisi_awal_tahun": 2024,
        "tujuan_list": tujuan_list,
    }


def generate_tujuan_sasaran_excel(report_data: Dict[str, Any]) -> io.BytesIO:
    """Generate Excel (.xlsx) file matching the exact standard layout from sample image."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Tujuan dan Sasaran"
    ws.views.sheetView[0].showGridLines = True

    # Palette
    COLOR_PRIMARY_HEADER = "3B6998"   # Dark steel blue (Row 6 & 7)
    COLOR_NUM_HEADER     = "5885AF"   # Medium steel blue (Row 8 numbering)
    COLOR_NO_COL         = "4A709C"   # Deep blue for Column A (No)
    COLOR_WHITE          = "FFFFFF"
    COLOR_BORDER         = "94A3B8"   # Slate border

    font_title_bold = Font(name="Calibri", size=11, bold=True)
    font_header = Font(name="Calibri", size=10, bold=True, color=COLOR_WHITE)
    font_num_header = Font(name="Calibri", size=9, bold=True, color=COLOR_WHITE)
    font_no_data = Font(name="Calibri", size=10, bold=True, color=COLOR_WHITE)
    font_data = Font(name="Calibri", size=10)
    font_data_bold = Font(name="Calibri", size=10, bold=True)

    fill_primary = PatternFill(start_color=COLOR_PRIMARY_HEADER, end_color=COLOR_PRIMARY_HEADER, fill_type="solid")
    fill_num = PatternFill(start_color=COLOR_NUM_HEADER, end_color=COLOR_NUM_HEADER, fill_type="solid")
    fill_no_col = PatternFill(start_color=COLOR_NO_COL, end_color=COLOR_NO_COL, fill_type="solid")

    thin_border_side = Side(border_style="thin", color=COLOR_BORDER)
    border_cell = Border(
        left=thin_border_side,
        right=thin_border_side,
        top=thin_border_side,
        bottom=thin_border_side,
    )

    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
    align_top_left = Alignment(horizontal="left", vertical="top", wrap_text=True)
    align_right = Alignment(horizontal="right", vertical="center", wrap_text=True)

    nama_skpd = report_data.get("opd", {}).get("nama_skpd", "Perangkat Daerah")

    # 1. Title Block (Rows 2, 3, 4)
    ws.merge_cells("A2:M2")
    ws["A2"] = "Tabel 3.1"
    ws["A2"].font = font_title_bold
    ws["A2"].alignment = align_center

    ws.merge_cells("A3:M3")
    ws["A3"] = f"Tujuan dan Sasaran {nama_skpd} Kota Tegal"
    ws["A3"].font = font_title_bold
    ws["A3"].alignment = align_center

    ws.merge_cells("A4:M4")
    ws["A4"] = "Tahun 2025-2029"
    ws["A4"].font = font_title_bold
    ws["A4"].alignment = align_center

    # 2. Table Headers (Row 6 & 7)
    # Col A: No.
    ws.merge_cells("A6:A7")
    ws["A6"] = "No."
    # Col B: Tujuan
    ws.merge_cells("B6:B7")
    ws["B6"] = "Tujuan"
    # Col C: Sasaran
    ws.merge_cells("C6:C7")
    ws["C6"] = "Sasaran"
    # Col D: Indikator
    ws.merge_cells("D6:D7")
    ws["D6"] = "Indikator"
    # Col E: Satuan
    ws.merge_cells("E6:E7")
    ws["E6"] = "Satuan"
    # Col F: Kondisi Awal (Row 6) / 2024 (Row 7)
    ws["F6"] = "Kondisi\nAwal"
    ws["F7"] = "2024"
    # Cols G-L: Target (Row 6) / 2025-2030 (Row 7)
    ws.merge_cells("G6:L6")
    ws["G6"] = "Target"
    ws["G7"] = "2025"
    ws["H7"] = "2026"
    ws["I7"] = "2027"
    ws["J7"] = "2028"
    ws["K7"] = "2029"
    ws["L7"] = "2030"
    # Col M: Ket
    ws.merge_cells("M6:M7")
    ws["M6"] = "Ket"

    # Style Header Rows 6 & 7
    for r in [6, 7]:
        for c in range(1, 14):
            cell = ws.cell(row=r, column=c)
            cell.fill = fill_primary
            cell.font = font_header
            cell.alignment = align_center
            cell.border = border_cell

    # 3. Header Row 8 (Column Numbering: 1 to 13)
    for c in range(1, 14):
        cell = ws.cell(row=8, column=c)
        cell.value = c
        cell.fill = fill_num
        cell.font = font_num_header
        cell.alignment = align_center
        cell.border = border_cell

    current_row = 9
    tujuan_list = report_data.get("tujuan_list", [])

    for t_idx, t in enumerate(tujuan_list, 1):
        tujuan_start_row = current_row
        no_val = t.get("no") or t_idx
        uraitujuan = t.get("uraitujuan", "-")

        # 4.1 Process Indikator Tujuan
        ind_tujuan_list = t.get("indikator_tujuan_list", [])
        for it in ind_tujuan_list:
            r = current_row
            # Col A: No.
            cell_a = ws.cell(row=r, column=1, value=no_val)
            cell_a.fill = fill_no_col
            cell_a.font = font_no_data
            cell_a.alignment = align_center
            cell_a.border = border_cell

            # Col B: Tujuan
            cell_b = ws.cell(row=r, column=2, value=uraitujuan)
            cell_b.font = font_data
            cell_b.alignment = align_left
            cell_b.border = border_cell

            # Col C: Sasaran (blank for Indikator Tujuan row)
            cell_c = ws.cell(row=r, column=3, value="")
            cell_c.font = font_data
            cell_c.alignment = align_left
            cell_c.border = border_cell

            # Col D: Indikator (e.g. "Indikator Tujuan - 1\nTingkat Kesempatan Kerja")
            label_ind = f"{it.get('no_label', '')}\n{it.get('uraian', '')}".strip()
            cell_d = ws.cell(row=r, column=4, value=label_ind)
            cell_d.font = font_data
            cell_d.alignment = align_left
            cell_d.border = border_cell

            # Col E: Satuan
            cell_e = ws.cell(row=r, column=5, value=it.get("satuan", "-"))
            cell_e.font = font_data
            cell_e.alignment = align_center
            cell_e.border = border_cell

            # Cols F-L: Targets
            targets = [
                it.get("target_awal", "-"),
                it.get("target0", "-"),
                it.get("target1", "-"),
                it.get("target2", "-"),
                it.get("target3", "-"),
                it.get("target4", "-"),
                it.get("target5", "-"),
            ]
            for col_idx, t_val in enumerate(targets, 6):
                cell_t = ws.cell(row=r, column=col_idx, value=t_val)
                cell_t.font = font_data
                cell_t.alignment = align_center
                cell_t.border = border_cell

            # Col M: Ket (Metadata)
            val_m = it.get("ket", "-")
            cell_m = ws.cell(row=r, column=13, value=val_m)
            cell_m.font = font_data
            cell_m.alignment = align_left if val_m and val_m != "-" else align_center
            cell_m.border = border_cell

            current_row += 1

        # 4.2 Process Sasarans under this Tujuan
        sasaran_list = t.get("sasaran_list", [])
        for s in sasaran_list:
            s_label = f"{s.get('no_label', '')}\n{s.get('uraisasaran', '')}".strip()
            ind_sas_list = s.get("indikator_list", [])

            if ind_sas_list:
                sas_start_row = current_row
                for isas in ind_sas_list:
                    r = current_row
                    # Col A: No.
                    cell_a = ws.cell(row=r, column=1, value=no_val)
                    cell_a.fill = fill_no_col
                    cell_a.font = font_no_data
                    cell_a.alignment = align_center
                    cell_a.border = border_cell

                    # Col B: Tujuan
                    cell_b = ws.cell(row=r, column=2, value=uraitujuan)
                    cell_b.font = font_data
                    cell_b.alignment = align_left
                    cell_b.border = border_cell

                    # Col C: Sasaran
                    cell_c = ws.cell(row=r, column=3, value=s_label)
                    cell_c.font = font_data
                    cell_c.alignment = align_left
                    cell_c.border = border_cell

                    # Col D: Indikator Sasaran
                    cell_d = ws.cell(row=r, column=4, value=isas.get("uraian", "-"))
                    cell_d.font = font_data
                    cell_d.alignment = align_left
                    cell_d.border = border_cell

                    # Col E: Satuan
                    cell_e = ws.cell(row=r, column=5, value=isas.get("satuan", "-"))
                    cell_e.font = font_data
                    cell_e.alignment = align_center
                    cell_e.border = border_cell

                    # Cols F-L: Targets
                    s_targets = [
                        isas.get("target_awal", "-"),
                        isas.get("target0", "-"),
                        isas.get("target1", "-"),
                        isas.get("target2", "-"),
                        isas.get("target3", "-"),
                        isas.get("target4", "-"),
                        isas.get("target5", "-"),
                    ]
                    for col_idx, t_val in enumerate(s_targets, 6):
                        cell_t = ws.cell(row=r, column=col_idx, value=t_val)
                        cell_t.font = font_data
                        cell_t.alignment = align_center
                        cell_t.border = border_cell

                    # Col M: Ket (Metadata)
                    val_sm = isas.get("ket", "-")
                    cell_m = ws.cell(row=r, column=13, value=val_sm)
                    cell_m.font = font_data
                    cell_m.alignment = align_left if val_sm and val_sm != "-" else align_center
                    cell_m.border = border_cell

                    current_row += 1

                # Merge Sasaran column if multiple indicators
                if len(ind_sas_list) > 1:
                    ws.merge_cells(start_row=sas_start_row, start_column=3, end_row=current_row - 1, end_column=3)

            else:
                # Sasaran without indicator (single row)
                r = current_row
                cell_a = ws.cell(row=r, column=1, value=no_val)
                cell_a.fill = fill_no_col
                cell_a.font = font_no_data
                cell_a.alignment = align_center
                cell_a.border = border_cell

                cell_b = ws.cell(row=r, column=2, value=uraitujuan)
                cell_b.font = font_data
                cell_b.alignment = align_left
                cell_b.border = border_cell

                cell_c = ws.cell(row=r, column=3, value=s_label)
                cell_c.font = font_data
                cell_c.alignment = align_left
                cell_c.border = border_cell

                for c in range(4, 14):
                    cell_blank = ws.cell(row=r, column=c, value="-")
                    cell_blank.font = font_data
                    cell_blank.alignment = align_center
                    cell_blank.border = border_cell

                current_row += 1

        # 4.3 If Tujuan has no indikator and no sasaran (single row)
        if not ind_tujuan_list and not sasaran_list:
            r = current_row
            cell_a = ws.cell(row=r, column=1, value=no_val)
            cell_a.fill = fill_no_col
            cell_a.font = font_no_data
            cell_a.alignment = align_center
            cell_a.border = border_cell

            cell_b = ws.cell(row=r, column=2, value=uraitujuan)
            cell_b.font = font_data
            cell_b.alignment = align_left
            cell_b.border = border_cell

            for c in range(3, 14):
                cell_blank = ws.cell(row=r, column=c, value="-")
                cell_blank.font = font_data
                cell_blank.alignment = align_center
                cell_blank.border = border_cell

            current_row += 1

        # 4.4 Merge Col A (No) and Col B (Tujuan) vertically across all rows of this Tujuan
        tujuan_end_row = current_row - 1
        if tujuan_end_row > tujuan_start_row:
            ws.merge_cells(start_row=tujuan_start_row, start_column=1, end_row=tujuan_end_row, end_column=1)
            ws.merge_cells(start_row=tujuan_start_row, start_column=2, end_row=tujuan_end_row, end_column=2)

    # Set column widths
    column_widths = {
        "A": 6,    # No.
        "B": 32,   # Tujuan
        "C": 30,   # Sasaran
        "D": 36,   # Indikator
        "E": 12,   # Satuan
        "F": 15,   # Kondisi Awal 2024
        "G": 13,   # 2025
        "H": 13,   # 2026
        "I": 13,   # 2027
        "J": 13,   # 2028
        "K": 13,   # 2029
        "L": 13,   # 2030
        "M": 32,   # Ket (Metadata)
    }
    for col_letter, width in column_widths.items():
        ws.column_dimensions[col_letter].width = width

    # Row Heights
    ws.row_dimensions[2].height = 20
    ws.row_dimensions[3].height = 20
    ws.row_dimensions[4].height = 20
    ws.row_dimensions[6].height = 24
    ws.row_dimensions[7].height = 24
    ws.row_dimensions[8].height = 18

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


# =====================================================================
# 3. TABEL 4.1: RENCANA PROGRAM, KEGIATAN, SUB KEGIATAN & PENDANAAN
# =====================================================================

def clean_bidang_name(uraibidang: Optional[str]) -> str:
    if not uraibidang:
        return "Bidang Urusan"
    txt = uraibidang.strip()
    if txt.upper().startswith("URUSAN PEMERINTAHAN BIDANG "):
        return f"Bidang Urusan {txt[27:].strip().title()}"
    elif txt.upper().startswith("BIDANG URUSAN "):
        return f"Bidang Urusan {txt[14:].strip().title()}"
    elif txt.upper().startswith("BIDANG "):
        return f"Bidang Urusan {txt[7:].strip().title()}"
    elif txt.upper().startswith("URUSAN PEMERINTAHAN "):
        return f"Bidang Urusan {txt[20:].strip().title()}"
    return f"Bidang Urusan {txt.strip().title()}"


async def get_program_kegiatan_report_data(
    session: AsyncSession, id_skpd: int, id_sub_skpd: Optional[int] = None, tipe: str = "murni"
) -> Dict[str, Any]:
    """
    Mengambil data terstruktur Tabel 4.1 Rencana Program, Kegiatan, Sub Kegiatan dan Pendanaan Perangkat Daerah.
    """
    opd = await session.get(TaOpd, id_skpd)
    if not opd:
        raise ValueError("Perangkat Daerah tidak ditemukan")

    target_kode = opd.kode_skpd
    sub_title = None

    subs = (await session.exec(
        select(TaSubPd).where(TaSubPd.id_skpd == id_skpd).order_by(TaSubPd.kode_sub_skpd.asc())
    )).all()
    has_multiple_subs = len(subs) > 1
    sub_map = {s.kode_sub_skpd: s.nama_sub_skpd for s in subs if s.kode_sub_skpd}

    if id_sub_skpd:
        sub = await session.get(TaSubPd, id_sub_skpd)
        if sub and sub.kode_sub_skpd:
            target_kodes = [sub.kode_sub_skpd]
            sub_title = sub.nama_sub_skpd
        else:
            target_kodes = [opd.kode_skpd]
    elif has_multiple_subs:
        target_kodes = [s.kode_sub_skpd for s in subs if s.kode_sub_skpd]
        if opd.kode_skpd not in target_kodes:
            target_kodes.append(opd.kode_skpd)
    else:
        target_kodes = [opd.kode_skpd]

    # Query all programs for this OPD / Sub SKPD
    programs = (await session.exec(
        select(RenstraProgram)
        .where(RenstraProgram.kodeskpd.in_(target_kodes))
        .order_by(RenstraProgram.kodeskpd.asc(), RenstraProgram.kodebidang.asc(), RenstraProgram.kodeprogram.asc())
    )).all()

    kodeprog_list = [p.kodeprogram for p in programs]

    # Preload indicators and children using composite keys (kodeskpd, kode) to prevent crosstalk between sub units
    ind_prog_rows = (await session.exec(
        select(RenstraIndikatorProgram)
        .where(RenstraIndikatorProgram.kodeskpd.in_(target_kodes))
        .order_by(RenstraIndikatorProgram.no.asc(), RenstraIndikatorProgram.urut.asc(), RenstraIndikatorProgram.id.asc())
    )).all() if target_kodes else []
    ind_prog_map: Dict[tuple, List[RenstraIndikatorProgram]] = {}
    for ip in ind_prog_rows:
        ind_prog_map.setdefault((ip.kodeskpd, ip.kodeprogram), []).append(ip)

    keg_rows = (await session.exec(
        select(RenstraKegiatan)
        .where(RenstraKegiatan.kodeskpd.in_(target_kodes))
        .order_by(RenstraKegiatan.no.asc(), RenstraKegiatan.kodekegiatan.asc())
    )).all() if target_kodes else []
    keg_map: Dict[tuple, List[RenstraKegiatan]] = {}
    for k in keg_rows:
        keg_map.setdefault((k.kodeskpd, k.kodeprogram), []).append(k)

    ind_keg_rows = (await session.exec(
        select(RenstraIndikatorKegiatan)
        .where(RenstraIndikatorKegiatan.kodeskpd.in_(target_kodes))
        .order_by(RenstraIndikatorKegiatan.no.asc(), RenstraIndikatorKegiatan.urut.asc(), RenstraIndikatorKegiatan.id.asc())
    )).all() if target_kodes else []
    ind_keg_map: Dict[tuple, List[RenstraIndikatorKegiatan]] = {}
    for ik in ind_keg_rows:
        ind_keg_map.setdefault((ik.kodeskpd, ik.kodekegiatan), []).append(ik)

    subkeg_rows = (await session.exec(
        select(RenstraSubkegiatan)
        .where(RenstraSubkegiatan.kodeskpd.in_(target_kodes))
        .order_by(RenstraSubkegiatan.no.asc(), RenstraSubkegiatan.kodesubkegiatan.asc())
    )).all() if target_kodes else []
    subkeg_map: Dict[tuple, List[RenstraSubkegiatan]] = {}
    for sk in subkeg_rows:
        subkeg_map.setdefault((sk.kodeskpd, sk.kodekegiatan), []).append(sk)

    # Preload metadata / definisi operasional from ref_subkegiatan
    ref_subkeg_rows = (await session.exec(
        select(RefSubkegiatan.kodesubkegiatan, RefSubkegiatan.definisi_operasional)
        .where(RefSubkegiatan.definisi_operasional.isnot(None))
    )).all()
    ref_def_map: Dict[str, str] = {}
    for rk, rdef in ref_subkeg_rows:
        if rk and rdef and rdef.strip() and rdef.strip() != "-":
            ref_def_map[rk.strip()] = rdef.strip()

    def build_program_item(p: RenstraProgram) -> Dict[str, Any]:
        p_indicators = []
        for ip in ind_prog_map.get((p.kodeskpd, p.kodeprogram), []):
            b_val = format_target_val(ip.target_awal or ip.target0)
            t2026 = format_target_val(ip.p_target1 if tipe == "perubahan" and ip.p_target1 not in (None, "-", "") else ip.target1)
            t2027 = format_target_val(ip.p_target2 if tipe == "perubahan" and ip.p_target2 not in (None, "-", "") else ip.target2)
            t2028 = format_target_val(ip.p_target3 if tipe == "perubahan" and ip.p_target3 not in (None, "-", "") else ip.target3)
            t2029 = format_target_val(ip.p_target4 if tipe == "perubahan" and ip.p_target4 not in (None, "-", "") else ip.target4)
            t2030 = format_target_val(ip.p_target5 if tipe == "perubahan" and ip.p_target5 not in (None, "-", "") else ip.target5)

            meta_p = getattr(ip, "definisi_operasional", None)
            if not meta_p or meta_p.strip() in ("", "-"):
                meta_p = getattr(ip, "formula", None)
            if not meta_p or meta_p.strip() in ("", "-"):
                meta_p = "-"
            else:
                meta_p = meta_p.strip()

            p_indicators.append({
                "uraian": ip.uraiindikator or "-",
                "satuan": ip.satuan or "-",
                "baseline": b_val,
                "targets": {
                    "2026": t2026,
                    "2027": t2027,
                    "2028": t2028,
                    "2029": t2029,
                    "2030": t2030,
                },
                "ket": meta_p,
            })

        p_kegiatans = []
        prog_pagu = {"2026": 0.0, "2027": 0.0, "2028": 0.0, "2029": 0.0, "2030": 0.0}

        for k in keg_map.get((p.kodeskpd, p.kodeprogram), []):
            k_indicators = []
            for ik in ind_keg_map.get((k.kodeskpd, k.kodekegiatan), []):
                b_val = format_target_val(ik.target_awal or ik.target0)
                t2026 = format_target_val(ik.p_target1 if tipe == "perubahan" and ik.p_target1 not in (None, "-", "") else ik.target1)
                t2027 = format_target_val(ik.p_target2 if tipe == "perubahan" and ik.p_target2 not in (None, "-", "") else ik.target2)
                t2028 = format_target_val(ik.p_target3 if tipe == "perubahan" and ik.p_target3 not in (None, "-", "") else ik.target3)
                t2029 = format_target_val(ik.p_target4 if tipe == "perubahan" and ik.p_target4 not in (None, "-", "") else ik.target4)
                t2030 = format_target_val(ik.p_target5 if tipe == "perubahan" and ik.p_target5 not in (None, "-", "") else ik.target5)

                meta_k = getattr(ik, "definisi_operasional", None)
                if not meta_k or meta_k.strip() in ("", "-"):
                    meta_k = "-"
                else:
                    meta_k = meta_k.strip()

                k_indicators.append({
                    "uraian": ik.uraiindikator or "-",
                    "satuan": ik.satuan or "-",
                    "baseline": b_val,
                    "targets": {
                        "2026": t2026,
                        "2027": t2027,
                        "2028": t2028,
                        "2029": t2029,
                        "2030": t2030,
                    },
                    "ket": meta_k,
                })

            k_subkegiatans = []
            keg_pagu = {"2026": 0.0, "2027": 0.0, "2028": 0.0, "2029": 0.0, "2030": 0.0}

            for sk in subkeg_map.get((k.kodeskpd, k.kodekegiatan), []):
                sk_b_val = format_target_val(sk.volume_awal or sk.volume_0)
                sk_t2026 = format_target_val(sk.p_volume_1 if tipe == "perubahan" and sk.p_volume_1 not in (None, "-", "") else sk.volume_1)
                sk_t2027 = format_target_val(sk.p_volume_2 if tipe == "perubahan" and sk.p_volume_2 not in (None, "-", "") else sk.volume_2)
                sk_t2028 = format_target_val(sk.p_volume_3 if tipe == "perubahan" and sk.p_volume_3 not in (None, "-", "") else sk.volume_3)
                sk_t2029 = format_target_val(sk.p_volume_4 if tipe == "perubahan" and sk.p_volume_4 not in (None, "-", "") else sk.volume_4)
                sk_t2030 = format_target_val(sk.p_volume_5 if tipe == "perubahan" and sk.p_volume_5 not in (None, "-", "") else sk.volume_5)

                sk_p1 = float(sk.p_pagu1) if tipe == "perubahan" and sk.p_pagu1 is not None and sk.p_pagu1 > 0 else float(sk.pagu1 or 0)
                sk_p2 = float(sk.p_pagu2) if tipe == "perubahan" and sk.p_pagu2 is not None and sk.p_pagu2 > 0 else float(sk.pagu2 or 0)
                sk_p3 = float(sk.p_pagu3) if tipe == "perubahan" and sk.p_pagu3 is not None and sk.p_pagu3 > 0 else float(sk.pagu3 or 0)
                sk_p4 = float(sk.p_pagu4) if tipe == "perubahan" and sk.p_pagu4 is not None and sk.p_pagu4 > 0 else float(sk.pagu4 or 0)
                sk_p5 = float(sk.p_pagu5) if tipe == "perubahan" and sk.p_pagu5 is not None and sk.p_pagu5 > 0 else float(sk.pagu5 or 0)

                keg_pagu["2026"] += sk_p1
                keg_pagu["2027"] += sk_p2
                keg_pagu["2028"] += sk_p3
                keg_pagu["2029"] += sk_p4
                keg_pagu["2030"] += sk_p5

                sk_code = (sk.kodesubkegiatan or "").strip()
                parts = sk_code.split(".")
                penunjang_key = "X.XX.01." + ".".join(parts[3:]) if len(parts) >= 3 and parts[2] == "01" else sk_code

                meta_sk = getattr(sk, "definisi_operasional", None)
                if not meta_sk or meta_sk.strip() in ("", "-"):
                    meta_sk = ref_def_map.get(sk_code) or ref_def_map.get(penunjang_key)
                if not meta_sk or meta_sk.strip() in ("", "-"):
                    meta_sk = "-"
                else:
                    meta_sk = meta_sk.strip()

                k_subkegiatans.append({
                    "kodesubkegiatan": sk.kodesubkegiatan,
                    "uraisubkegiatan": sk.uraisubkegiatan or "-",
                    "kinerja": sk.kinerja or "-",
                    "indikator": sk.uraisubkegiatan_indikator or "-",
                    "satuan": sk.satuan or "-",
                    "baseline": sk_b_val,
                    "targets": {
                        "2026": sk_t2026,
                        "2027": sk_t2027,
                        "2028": sk_t2028,
                        "2029": sk_t2029,
                        "2030": sk_t2030,
                    },
                    "pagu": {
                        "2026": sk_p1,
                        "2027": sk_p2,
                        "2028": sk_p3,
                        "2029": sk_p4,
                        "2030": sk_p5,
                    },
                    "ket": meta_sk,
                })

            for y in ["2026", "2027", "2028", "2029", "2030"]:
                prog_pagu[y] += keg_pagu[y]

            raw_keg_nama = (k.uraikegiatan or "-").strip()
            display_keg_nama = raw_keg_nama if raw_keg_nama.lower().startswith("kegiatan") else f"Kegiatan {raw_keg_nama}"

            keg_sasaran = k.kinerja or getattr(k, "urai", None)
            if not keg_sasaran or keg_sasaran.strip() in ("", "-"):
                keg_sasaran = f"Terlaksananya {raw_keg_nama}"

            # If no indicators are explicitly registered for this kegiatan, generate standard default matching Renstra format
            if not k_indicators:
                k_indicators = [{
                    "uraian": f"Presentase {raw_keg_nama.lower()} tercapai",
                    "satuan": "%",
                    "baseline": "100",
                    "targets": {
                        y: "100" if keg_pagu[y] > 0 else "-"
                        for y in ["2026", "2027", "2028", "2029", "2030"]
                    },
                    "ket": "-",
                }]

            p_kegiatans.append({
                "kodekegiatan": k.kodekegiatan,
                "uraikegiatan": display_keg_nama,
                "kinerja": keg_sasaran,
                "indicators": k_indicators,
                "pagu": keg_pagu,
                "subkegiatans": k_subkegiatans,
            })

        raw_prog_nama = (p.uraiprogram or "-").strip()
        display_prog_nama = raw_prog_nama if raw_prog_nama.lower().startswith("program") else f"Program {raw_prog_nama}"
        prog_sasaran = p.kinerja or p.urai
        if not prog_sasaran or prog_sasaran.strip() in ("", "-"):
            prog_sasaran = f"Meningkatnya {raw_prog_nama}"

        return {
            "kodeprogram": p.kodeprogram,
            "kodeskpd": p.kodeskpd,
            "uraiprogram": display_prog_nama,
            "kinerja": prog_sasaran,
            "indicators": p_indicators,
            "pagu": prog_pagu,
            "kegiatans": p_kegiatans,
        }

    def group_programs_by_bidang(prog_list: List[RenstraProgram]) -> List[Dict[str, Any]]:
        b_dict: Dict[str, Dict[str, Any]] = {}
        for p in prog_list:
            kbidang = getattr(p, "kode_bidang", None) or getattr(p, "kodebidang", None) or "0.00"
            ubidang = getattr(p, "uraibidang", None) or "URUSAN PEMERINTAHAN LAINNYA"
            if kbidang not in b_dict:
                b_dict[kbidang] = {
                    "kode_bidang": kbidang,
                    "kodebidang": kbidang,
                    "uraibidang": ubidang,
                    "nama_bidang": ubidang,
                    "programs": [],
                }
            prog_item = build_program_item(p)
            b_dict[kbidang]["programs"].append(prog_item)
        return list(b_dict.values())

    bidang_list = group_programs_by_bidang(programs)

    total_all_pagu = {y: 0.0 for y in ["2026", "2027", "2028", "2029", "2030"]}
    for b in bidang_list:
        for pr in b["programs"]:
            for y in ["2026", "2027", "2028", "2029", "2030"]:
                total_all_pagu[y] += pr["pagu"].get(y, 0.0)

    # Build Sub Unit Groups if OPD has multiple sub units
    sub_unit_groups = []
    if has_multiple_subs and not id_sub_skpd:
        progs_by_sub: Dict[str, List[RenstraProgram]] = {}
        for p in programs:
            progs_by_sub.setdefault(p.kodeskpd, []).append(p)

        for s in subs:
            s_progs = progs_by_sub.get(s.kode_sub_skpd, [])
            if s_progs:
                s_bidang_list = group_programs_by_bidang(s_progs)
                s_total_pagu = {y: 0.0 for y in ["2026", "2027", "2028", "2029", "2030"]}
                for b in s_bidang_list:
                    for pr in b["programs"]:
                        for y in ["2026", "2027", "2028", "2029", "2030"]:
                            s_total_pagu[y] += pr["pagu"].get(y, 0.0)

                sub_unit_groups.append({
                    "kode_sub_skpd": s.kode_sub_skpd,
                    "nama_sub_skpd": s.nama_sub_skpd,
                    "bidang_list": s_bidang_list,
                    "total_pagu": s_total_pagu,
                })

    total_prog_count = sum(len(b["programs"]) for b in bidang_list)
    total_keg_count = sum(sum(len(p["kegiatans"]) for p in b["programs"]) for b in bidang_list)
    total_sub_count = sum(sum(sum(len(k["subkegiatans"]) for k in p["kegiatans"]) for p in b["programs"]) for b in bidang_list)

    return {
        "opd": {
            "id_skpd": opd.id_skpd,
            "kode_skpd": opd.kode_skpd,
            "nama_skpd": opd.nama_skpd,
            "sub_title": sub_title,
        },
        "tipe": tipe,
        "tahun_awal": 2026,
        "tahun_akhir": 2030,
        "has_multiple_subs": has_multiple_subs and not id_sub_skpd,
        "sub_unit_groups": sub_unit_groups,
        "total_bidang": len(bidang_list),
        "total_program": total_prog_count,
        "total_kegiatan": total_keg_count,
        "total_subkegiatan": total_sub_count,
        "total_pagu": total_all_pagu,
        "bidang_list": bidang_list,
    }


def generate_program_kegiatan_excel(report_data: Dict[str, Any]) -> io.BytesIO:
    """
    Generate Excel (.xlsx) file matching the exact standard layout of Tabel 4.1 from the sample image.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Tabel 4.1"
    ws.views.sheetView[0].showGridLines = True

    # Color Palette from the sample image
    COLOR_HEADER_BG    = "B4C6E7"  # Soft periwinkle / steel blue
    COLOR_GUIDE_BG     = "D9E1F2"  # Lighter periwinkle blue
    COLOR_SUBUNIT_BG   = "BDD7EE"  # Soft blue for Sub Unit
    COLOR_BIDANG_BG    = "D9E1F2"  # Soft blue for Bidang Urusan
    COLOR_PROGRAM_BG   = "FCE4D6"  # Soft peach / pinkish coral for Program
    COLOR_KEGIATAN_BG  = "E2EFDA"  # Soft pastel green for Kegiatan
    COLOR_WHITE        = "FFFFFF"  # White for Subkegiatan
    COLOR_BORDER       = "94A3B8"  # Slate thin border
    COLOR_BLACK        = "000000"

    font_title_bold = Font(name="Calibri", size=11, bold=True)
    font_header_bold = Font(name="Calibri", size=9.5, bold=True, color=COLOR_BLACK)
    font_guide = Font(name="Calibri", size=8.5, bold=True, color=COLOR_BLACK)
    font_subunit = Font(name="Calibri", size=10, bold=True, color=COLOR_BLACK)
    font_bidang = Font(name="Calibri", size=9.5, bold=True, color=COLOR_BLACK)
    font_program = Font(name="Calibri", size=9, bold=True, color=COLOR_BLACK)
    font_kegiatan = Font(name="Calibri", size=8.5, bold=True, color=COLOR_BLACK)
    font_subkegiatan = Font(name="Calibri", size=8.5, color=COLOR_BLACK)

    fill_header = PatternFill(start_color=COLOR_HEADER_BG, end_color=COLOR_HEADER_BG, fill_type="solid")
    fill_guide = PatternFill(start_color=COLOR_GUIDE_BG, end_color=COLOR_GUIDE_BG, fill_type="solid")
    fill_subunit = PatternFill(start_color=COLOR_SUBUNIT_BG, end_color=COLOR_SUBUNIT_BG, fill_type="solid")
    fill_bidang = PatternFill(start_color=COLOR_BIDANG_BG, end_color=COLOR_BIDANG_BG, fill_type="solid")
    fill_program = PatternFill(start_color=COLOR_PROGRAM_BG, end_color=COLOR_PROGRAM_BG, fill_type="solid")
    fill_kegiatan = PatternFill(start_color=COLOR_KEGIATAN_BG, end_color=COLOR_KEGIATAN_BG, fill_type="solid")
    fill_subkegiatan = PatternFill(start_color=COLOR_WHITE, end_color=COLOR_WHITE, fill_type="solid")

    thin_border_side = Side(border_style="thin", color=COLOR_BORDER)
    border_cell = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)

    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
    align_top_left = Alignment(horizontal="left", vertical="top", wrap_text=True)
    align_right = Alignment(horizontal="right", vertical="center", wrap_text=True)

    nama_skpd = report_data.get("opd", {}).get("nama_skpd", "Perangkat Daerah")
    tipe_label = " (Perubahan)" if report_data.get("tipe") == "perubahan" else ""

    # 1. Title Block (Rows 2, 3, 4)
    ws.merge_cells("A2:Q2")
    ws["A2"] = "Tabel 4.1"
    ws["A2"].font = font_title_bold
    ws["A2"].alignment = align_center

    ws.merge_cells("A3:Q3")
    ws["A3"] = f"Rencana Program, Kegiatan, Sub Kegiatan dan Pendanaan Perangkat Daerah{tipe_label}"
    ws["A3"].font = font_title_bold
    ws["A3"].alignment = align_center

    ws.merge_cells("A4:Q4")
    ws["A4"] = f"{nama_skpd} Kota Tegal Tahun 2026-2030"
    ws["A4"].font = font_title_bold
    ws["A4"].alignment = align_center

    # 2. Table Headers (Row 6, 7, 8)
    # A6:A8: Kode
    ws.merge_cells("A6:A8")
    ws["A6"] = "Kode"

    # B6:B8: Bidang Urusan/ Program/Kegiatan/ Sub Kegiatan
    ws.merge_cells("B6:B8")
    ws["B6"] = "Bidang Urusan/\nProgram/Kegiatan/ Sub Kegiatan"

    # C6:C8: Sasaran Program/Sasaran Kegiatan/Sasaran Sub Kegiatan
    ws.merge_cells("C6:C8")
    ws["C6"] = "Sasaran\nProgram/Sasaran\nKegiatan/Sasaran\nSub Kegiatan"

    # D6:D8: Indikator Outcome/Output
    ws.merge_cells("D6:D8")
    ws["D6"] = "Indikator\nOutcome/Output"

    # E6:E8: Satuan
    ws.merge_cells("E6:E8")
    ws["E6"] = "Satuan"

    # F6:F8: Baseline 2024
    ws.merge_cells("F6:F8")
    ws["F6"] = "Baseline\n2024"

    # G6:P6: Target dan Pagu Indikatif Tahun
    ws.merge_cells("G6:P6")
    ws["G6"] = "Target dan Pagu Indikatif Tahun"

    # Q6:Q8: Ket
    ws.merge_cells("Q6:Q8")
    ws["Q6"] = "Ket"

    # Row 7 (Years under G6:P6)
    ws.merge_cells("G7:H7")
    ws["G7"] = "2026"

    ws.merge_cells("I7:J7")
    ws["I7"] = "2027"

    ws.merge_cells("K7:L7")
    ws["K7"] = "2028"

    ws.merge_cells("M7:N7")
    ws["M7"] = "2029"

    ws.merge_cells("O7:P7")
    ws["O7"] = "2030"

    # Row 8 (Target | Pagu)
    ws["G8"] = "Target"
    ws["H8"] = "Pagu"
    ws["I8"] = "Target"
    ws["J8"] = "Pagu"
    ws["K8"] = "Target"
    ws["L8"] = "Pagu"
    ws["M8"] = "Target"
    ws["N8"] = "Pagu"
    ws["O8"] = "Target"
    ws["P8"] = "Pagu"

    # Style Header Rows 6..8
    for r in range(6, 9):
        ws.row_dimensions[r].height = 20
        for col in range(1, 18):
            cell = ws.cell(row=r, column=col)
            cell.fill = fill_header
            cell.font = font_header_bold
            cell.alignment = align_center
            cell.border = border_cell

    # Row 9 (Column Numbering Guide 1..17)
    ws.row_dimensions[9].height = 16
    for col in range(1, 18):
        cell = ws.cell(row=9, column=col, value=col)
        cell.fill = fill_guide
        cell.font = font_guide
        cell.alignment = align_center
        cell.border = border_cell

    current_row = 10
    bidang_num = 1

    def render_bidangs(b_list: List[Dict[str, Any]], start_row: int) -> int:
        r = start_row
        for b in b_list:
            # 1. Bidang Urusan Row
            ws.row_dimensions[r].height = 22
            cell_kode = ws.cell(row=r, column=1, value=b.get("kode_bidang") or b.get("kodebidang") or "")
            cell_kode.alignment = align_left
            cell_kode.font = font_bidang

            cell_nama = ws.cell(row=r, column=2, value=b.get("uraibidang") or b.get("nama_bidang"))
            cell_nama.alignment = align_left
            cell_nama.font = font_bidang

            for c in range(1, 18):
                cell = ws.cell(row=r, column=c)
                cell.fill = fill_bidang
                cell.border = border_cell

            r += 1

            for prog in b.get("programs", []):
                prog_indicators = prog.get("indicators", [])
                # 2. Program Row(s)
                ws.row_dimensions[r].height = 22

                # Col A: Kode Program
                cell_prog_kode = ws.cell(row=r, column=1, value=prog.get("kodeprogram") or "")
                cell_prog_kode.alignment = align_left
                cell_prog_kode.font = font_program

                # Col B: Program Name
                ws.cell(row=r, column=2, value=prog["uraiprogram"]).alignment = align_left
                # Col C: Sasaran Program (Kinerja)
                ws.cell(row=r, column=3, value=prog["kinerja"]).alignment = align_left

                first_ind = prog_indicators[0] if prog_indicators else {}
                ws.cell(row=r, column=4, value=first_ind.get("uraian", "-")).alignment = align_left
                ws.cell(row=r, column=5, value=first_ind.get("satuan", "-")).alignment = align_center
                ws.cell(row=r, column=6, value=first_ind.get("baseline", "-")).alignment = align_center

                # Targets & Pagu
                targets = first_ind.get("targets", {})
                pagu = prog.get("pagu", {})
                years = ["2026", "2027", "2028", "2029", "2030"]

                for idx, yr in enumerate(years):
                    t_col = 7 + (idx * 2)   # G, I, K, M, O
                    p_col = t_col + 1        # H, J, L, N, P

                    # Target
                    c_target = ws.cell(row=r, column=t_col, value=targets.get(yr, "-"))
                    c_target.alignment = align_center

                    # Pagu
                    p_val = pagu.get(yr, 0)
                    c_pagu = ws.cell(row=r, column=p_col, value=p_val)
                    c_pagu.number_format = "#,##0"
                    c_pagu.alignment = align_right

                p_ket_val = first_ind.get("ket", "-")
                c_p_ket = ws.cell(row=r, column=17, value=p_ket_val)
                c_p_ket.alignment = align_top_left if p_ket_val and p_ket_val != "-" else align_center

                for c in range(1, 18):
                    cell = ws.cell(row=r, column=c)
                    cell.fill = fill_program
                    cell.font = font_program
                    cell.border = border_cell

                r += 1

                # Extra program indicators (if any)
                for extra_ind in prog_indicators[1:]:
                    ws.row_dimensions[r].height = 20
                    ws.cell(row=r, column=4, value=extra_ind.get("uraian", "-")).alignment = align_left
                    ws.cell(row=r, column=5, value=extra_ind.get("satuan", "-")).alignment = align_center
                    ws.cell(row=r, column=6, value=extra_ind.get("baseline", "-")).alignment = align_center

                    ex_targets = extra_ind.get("targets", {})
                    for idx, yr in enumerate(years):
                        t_col = 7 + (idx * 2)
                        p_col = t_col + 1
                        ws.cell(row=r, column=t_col, value=ex_targets.get(yr, "-")).alignment = align_center
                        ws.cell(row=r, column=p_col, value="-").alignment = align_center

                    ex_ket_val = extra_ind.get("ket", "-")
                    c_ex_ket = ws.cell(row=r, column=17, value=ex_ket_val)
                    c_ex_ket.alignment = align_top_left if ex_ket_val and ex_ket_val != "-" else align_center

                    for c in range(1, 18):
                        cell = ws.cell(row=r, column=c)
                        cell.fill = fill_program
                        cell.font = font_program
                        cell.border = border_cell
                    r += 1

                # 3. Kegiatan Rows
                for keg in prog.get("kegiatans", []):
                    keg_indicators = keg.get("indicators", [])
                    ws.row_dimensions[r].height = 22

                    # Col A: Kode Kegiatan
                    cell_keg_kode = ws.cell(row=r, column=1, value=keg.get("kodekegiatan") or "")
                    cell_keg_kode.alignment = align_left
                    cell_keg_kode.font = font_kegiatan

                    ws.cell(row=r, column=2, value=keg["uraikegiatan"]).alignment = align_left
                    ws.cell(row=r, column=3, value=keg["kinerja"]).alignment = align_left

                    first_k_ind = keg_indicators[0] if keg_indicators else {}
                    ws.cell(row=r, column=4, value=first_k_ind.get("uraian", "-")).alignment = align_left
                    ws.cell(row=r, column=5, value=first_k_ind.get("satuan", "-")).alignment = align_center
                    ws.cell(row=r, column=6, value=first_k_ind.get("baseline", "-")).alignment = align_center

                    k_targets = first_k_ind.get("targets", {})
                    k_pagu = keg.get("pagu", {})

                    for idx, yr in enumerate(years):
                        t_col = 7 + (idx * 2)
                        p_col = t_col + 1

                        ws.cell(row=r, column=t_col, value=k_targets.get(yr, "-")).alignment = align_center

                        p_val = k_pagu.get(yr, 0)
                        c_pagu = ws.cell(row=r, column=p_col, value=p_val)
                        c_pagu.number_format = "#,##0"
                        c_pagu.alignment = align_right

                    k_ket_val = first_k_ind.get("ket", "-")
                    c_k_ket = ws.cell(row=r, column=17, value=k_ket_val)
                    c_k_ket.alignment = align_top_left if k_ket_val and k_ket_val != "-" else align_center

                    for c in range(1, 18):
                        cell = ws.cell(row=r, column=c)
                        cell.fill = fill_kegiatan
                        cell.font = font_kegiatan
                        cell.border = border_cell

                    r += 1

                    # Extra kegiatan indicators (if any)
                    for extra_k_ind in keg_indicators[1:]:
                        ws.row_dimensions[r].height = 20
                        ws.cell(row=r, column=4, value=extra_k_ind.get("uraian", "-")).alignment = align_left
                        ws.cell(row=r, column=5, value=extra_k_ind.get("satuan", "-")).alignment = align_center
                        ws.cell(row=r, column=6, value=extra_k_ind.get("baseline", "-")).alignment = align_center

                        ex_k_targets = extra_k_ind.get("targets", {})
                        for idx, yr in enumerate(years):
                            t_col = 7 + (idx * 2)
                            p_col = t_col + 1
                            ws.cell(row=r, column=t_col, value=ex_k_targets.get(yr, "-")).alignment = align_center
                            ws.cell(row=r, column=p_col, value="-").alignment = align_center

                        ex_k_ket_val = extra_k_ind.get("ket", "-")
                        c_ex_k_ket = ws.cell(row=r, column=17, value=ex_k_ket_val)
                        c_ex_k_ket.alignment = align_top_left if ex_k_ket_val and ex_k_ket_val != "-" else align_center

                        for c in range(1, 18):
                            cell = ws.cell(row=r, column=c)
                            cell.fill = fill_kegiatan
                            cell.font = font_kegiatan
                            cell.border = border_cell
                        r += 1

                    # 4. Subkegiatan Rows
                    for subk in keg.get("subkegiatans", []):
                        ws.row_dimensions[r].height = 22

                        # Col A: Kode Sub Kegiatan
                        cell_sub_kode = ws.cell(row=r, column=1, value=subk.get("kodesubkegiatan") or "")
                        cell_sub_kode.alignment = align_left
                        cell_sub_kode.font = font_subkegiatan

                        ws.cell(row=r, column=2, value=subk["uraisubkegiatan"]).alignment = align_left
                        ws.cell(row=r, column=3, value=subk["kinerja"]).alignment = align_left
                        ws.cell(row=r, column=4, value=subk["indikator"]).alignment = align_left
                        ws.cell(row=r, column=5, value=subk["satuan"]).alignment = align_center
                        ws.cell(row=r, column=6, value=subk["baseline"]).alignment = align_center

                        sk_targets = subk.get("targets", {})
                        sk_pagu = subk.get("pagu", {})

                        for idx, yr in enumerate(years):
                            t_col = 7 + (idx * 2)
                            p_col = t_col + 1

                            ws.cell(row=r, column=t_col, value=sk_targets.get(yr, "-")).alignment = align_center

                            p_val = sk_pagu.get(yr, 0)
                            c_pagu = ws.cell(row=r, column=p_col, value=p_val)
                            c_pagu.number_format = "#,##0"
                            c_pagu.alignment = align_right

                        subk_ket_val = subk.get("ket", "-")
                        c_subk_ket = ws.cell(row=r, column=17, value=subk_ket_val)
                        c_subk_ket.alignment = align_top_left if subk_ket_val and subk_ket_val != "-" else align_center

                        for c in range(1, 18):
                            cell = ws.cell(row=r, column=c)
                            cell.fill = fill_subkegiatan
                            cell.font = font_subkegiatan
                            cell.border = border_cell

                        r += 1
        return r

    # Populate Data
    if report_data.get("has_multiple_subs") and report_data.get("sub_unit_groups"):
        for sub_group in report_data["sub_unit_groups"]:
            # Sub Unit Header Row (Soft Blue #BDD7EE)
            ws.row_dimensions[current_row].height = 24
            cell_sub_k = ws.cell(row=current_row, column=1, value=sub_group.get("kode_sub_skpd") or "")
            cell_sub_k.alignment = align_left
            cell_sub_k.font = font_subunit

            cell_sub_n = ws.cell(row=current_row, column=2, value=f"{sub_group.get('nama_sub_skpd', '').upper()}")
            cell_sub_n.alignment = align_left
            cell_sub_n.font = font_subunit

            for c in range(1, 18):
                cell = ws.cell(row=current_row, column=c)
                cell.fill = fill_subunit
                cell.border = border_cell

            current_row += 1
            current_row = render_bidangs(sub_group.get("bidang_list", []), current_row)
    else:
        current_row = render_bidangs(report_data.get("bidang_list", []), current_row)

    # Column Widths
    column_widths = {
        "A": 22,   # Kode (Bidang/Program/Kegiatan/Subkegiatan)
        "B": 42,   # Bidang / Program / Kegiatan / Subkegiatan
        "C": 34,   # Sasaran / Kinerja
        "D": 34,   # Indikator
        "E": 10,   # Satuan
        "F": 12,   # Baseline 2024
        "G": 10,   # 2026 Target
        "H": 18,   # 2026 Pagu
        "I": 10,   # 2027 Target
        "J": 18,   # 2027 Pagu
        "K": 10,   # 2028 Target
        "L": 18,   # 2028 Pagu
        "M": 10,   # 2029 Target
        "N": 18,   # 2029 Pagu
        "O": 10,   # 2030 Target
        "P": 18,   # 2030 Pagu
        "Q": 35,   # Ket (Metadata Indikator)
    }
    for col_letter, width in column_widths.items():
        ws.column_dimensions[col_letter].width = width

    ws.row_dimensions[2].height = 20
    ws.row_dimensions[3].height = 20
    ws.row_dimensions[4].height = 20

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


async def get_iku_report_data(
    session: AsyncSession, id_skpd: int, tipe: str = "murni"
) -> Dict[str, Any]:
    """Fetch Indikator Kinerja Utama (IKU) data for a given OPD."""
    # 1. Fetch OPD
    opd = await session.get(TaOpd, id_skpd)
    if not opd:
        raise ValueError(f"Perangkat Daerah dengan ID {id_skpd} tidak ditemukan")

    kode_skpd = opd.kode_skpd
    use_perubahan = tipe.lower() == "perubahan"

    # 2. Fetch Tujuan
    stmt_tujuan = (
        select(RenstraTujuan)
        .where(RenstraTujuan.kodeskpd == kode_skpd)
        .order_by(RenstraTujuan.no_urut, RenstraTujuan.idtujuan)
    )
    res_tujuan = await session.exec(stmt_tujuan)
    tujuans = res_tujuan.all()

    # Strategy: First collect indicators with iku == '1'
    groups = []
    has_explicit_iku = False

    for t in tujuans:
        # Check Indikator Tujuan with IKU == '1'
        stmt_ind_tujuan = (
            select(RenstraIndikatorTujuan)
            .where(
                RenstraIndikatorTujuan.idtujuan == t.idtujuan,
                RenstraIndikatorTujuan.iku == "1",
            )
            .order_by(
                RenstraIndikatorTujuan.no_urut,
                RenstraIndikatorTujuan.urut,
                RenstraIndikatorTujuan.idtujuan_indikator,
            )
        )
        res_ind_tujuan = await session.exec(stmt_ind_tujuan)
        ind_tujuans = res_ind_tujuan.all()

        if ind_tujuans:
            has_explicit_iku = True
            t_inds = []
            for it in ind_tujuans:
                t0 = it.p_target0 if use_perubahan and it.p_target0 else (it.target0 or "-")
                t1 = it.p_target1 if use_perubahan and it.p_target1 else (it.target1 or "-")
                t2 = it.p_target2 if use_perubahan and it.p_target2 else (it.target2 or "-")
                t3 = it.p_target3 if use_perubahan and it.p_target3 else (it.target3 or "-")
                t4 = it.p_target4 if use_perubahan and it.p_target4 else (it.target4 or "-")
                t5 = it.p_target5 if use_perubahan and it.p_target5 else (it.target5 or "-")

                t_inds.append({
                    "uraian": it.uraitujuan_indikator or "-",
                    "satuan": it.satuan or "-",
                    "target0": format_target_val(t0),
                    "target1": format_target_val(t1),
                    "target2": format_target_val(t2),
                    "target3": format_target_val(t3),
                    "target4": format_target_val(t4),
                    "target5": format_target_val(t5),
                })
            groups.append({
                "tujuan_sasaran": t.uraitujuan or "-",
                "level": "Tujuan",
                "indikator_list": t_inds,
            })

        # Check Sasarans under this Tujuan
        stmt_sasaran = (
            select(RenstraSasaran)
            .where(RenstraSasaran.idtujuan == t.idtujuan)
            .order_by(RenstraSasaran.no, RenstraSasaran.urut, RenstraSasaran.idsasaran)
        )
        res_sasaran = await session.exec(stmt_sasaran)
        sasarans = res_sasaran.all()

        for s in sasarans:
            stmt_ind_sas = (
                select(RenstraIndikatorSasaran)
                .where(
                    RenstraIndikatorSasaran.idsasaran == s.idsasaran,
                    RenstraIndikatorSasaran.iku == "1",
                )
                .order_by(
                    RenstraIndikatorSasaran.no,
                    RenstraIndikatorSasaran.urut,
                    RenstraIndikatorSasaran.idsasaran_indikator,
                )
            )
            res_ind_sas = await session.exec(stmt_ind_sas)
            ind_sasarans = res_ind_sas.all()

            if ind_sasarans:
                has_explicit_iku = True
                s_inds = []
                for isas in ind_sasarans:
                    st0 = isas.p_target0 if use_perubahan and isas.p_target0 else (isas.target0 or "-")
                    st1 = isas.p_target1 if use_perubahan and isas.p_target1 else (isas.target1 or "-")
                    st2 = isas.p_target2 if use_perubahan and isas.p_target2 else (isas.target2 or "-")
                    st3 = isas.p_target3 if use_perubahan and isas.p_target3 else (isas.target3 or "-")
                    st4 = isas.p_target4 if use_perubahan and isas.p_target4 else (isas.target4 or "-")
                    st5 = isas.p_target5 if use_perubahan and isas.p_target5 else (isas.target5 or "-")

                    s_inds.append({
                        "uraian": isas.uraisasaran_indikator or "-",
                        "satuan": isas.satuan or "-",
                        "target0": format_target_val(st0),
                        "target1": format_target_val(st1),
                        "target2": format_target_val(st2),
                        "target3": format_target_val(st3),
                        "target4": format_target_val(st4),
                        "target5": format_target_val(st5),
                    })
                groups.append({
                    "tujuan_sasaran": s.uraisasaran or "-",
                    "level": "Sasaran",
                    "indikator_list": s_inds,
                })

    # If OPD has no explicit IKU flag (iku == '1'), fallback to all Indikator Tujuan
    if not has_explicit_iku:
        for t in tujuans:
            stmt_all_ind_tujuan = (
                select(RenstraIndikatorTujuan)
                .where(RenstraIndikatorTujuan.idtujuan == t.idtujuan)
                .order_by(
                    RenstraIndikatorTujuan.no_urut,
                    RenstraIndikatorTujuan.urut,
                    RenstraIndikatorTujuan.idtujuan_indikator,
                )
            )
            res_all_ind = await session.exec(stmt_all_ind_tujuan)
            all_inds = res_all_ind.all()

            if all_inds:
                t_inds = []
                for it in all_inds:
                    t0 = it.p_target0 if use_perubahan and it.p_target0 else (it.target0 or "-")
                    t1 = it.p_target1 if use_perubahan and it.p_target1 else (it.target1 or "-")
                    t2 = it.p_target2 if use_perubahan and it.p_target2 else (it.target2 or "-")
                    t3 = it.p_target3 if use_perubahan and it.p_target3 else (it.target3 or "-")
                    t4 = it.p_target4 if use_perubahan and it.p_target4 else (it.target4 or "-")
                    t5 = it.p_target5 if use_perubahan and it.p_target5 else (it.target5 or "-")

                    t_inds.append({
                        "uraian": it.uraitujuan_indikator or "-",
                        "satuan": it.satuan or "-",
                        "target0": format_target_val(t0),
                        "target1": format_target_val(t1),
                        "target2": format_target_val(t2),
                        "target3": format_target_val(t3),
                        "target4": format_target_val(t4),
                        "target5": format_target_val(t5),
                    })
                groups.append({
                    "tujuan_sasaran": t.uraitujuan or "-",
                    "level": "Tujuan",
                    "indikator_list": t_inds,
                })

    return {
        "opd": {
            "id_skpd": opd.id_skpd,
            "kode_skpd": opd.kode_skpd,
            "nama_skpd": opd.nama_skpd,
        },
        "tipe": "perubahan" if use_perubahan else "murni",
        "tahun_awal": 2025,
        "tahun_akhir": 2030,
        "has_explicit_iku": has_explicit_iku,
        "groups": groups,
    }


def generate_iku_excel(report_data: Dict[str, Any]) -> io.BytesIO:
    """Generate Excel (.xlsx) file for Indikator Kinerja Utama (IKU)."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "IKU"
    ws.views.sheetView[0].showGridLines = True

    COLOR_PRIMARY_HEADER = "3B6998"   # Dark steel blue
    COLOR_NUM_HEADER     = "5885AF"   # Medium steel blue
    COLOR_NO_COL         = "4A709C"   # Deep blue for No
    COLOR_WHITE          = "FFFFFF"
    COLOR_BORDER         = "94A3B8"

    font_title_bold = Font(name="Calibri", size=11, bold=True)
    font_header = Font(name="Calibri", size=10, bold=True, color=COLOR_WHITE)
    font_num_header = Font(name="Calibri", size=9, bold=True, color=COLOR_WHITE)
    font_no_data = Font(name="Calibri", size=10, bold=True, color=COLOR_WHITE)
    font_data = Font(name="Calibri", size=10)

    fill_primary = PatternFill(start_color=COLOR_PRIMARY_HEADER, end_color=COLOR_PRIMARY_HEADER, fill_type="solid")
    fill_num = PatternFill(start_color=COLOR_NUM_HEADER, end_color=COLOR_NUM_HEADER, fill_type="solid")
    fill_no_col = PatternFill(start_color=COLOR_NO_COL, end_color=COLOR_NO_COL, fill_type="solid")

    thin_border_side = Side(border_style="thin", color=COLOR_BORDER)
    border_cell = Border(
        left=thin_border_side,
        right=thin_border_side,
        top=thin_border_side,
        bottom=thin_border_side,
    )

    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)

    nama_skpd = report_data.get("opd", {}).get("nama_skpd", "Perangkat Daerah")

    # 1. Title Block (Rows 2, 3, 4)
    ws.merge_cells("A2:J2")
    ws["A2"] = "Indikator Kinerja Utama"
    ws["A2"].font = font_title_bold
    ws["A2"].alignment = align_center

    ws.merge_cells("A3:J3")
    ws["A3"] = f"{nama_skpd} Kota Tegal"
    ws["A3"].font = font_title_bold
    ws["A3"].alignment = align_center

    ws.merge_cells("A4:J4")
    ws["A4"] = "Tahun 2025-2030"
    ws["A4"].font = font_title_bold
    ws["A4"].alignment = align_center

    # 2. Table Headers (Rows 6 & 7)
    # Col A: No
    ws.merge_cells("A6:A7")
    ws["A6"] = "No"
    # Col B: Tujuan / Sasaran
    ws.merge_cells("B6:B7")
    ws["B6"] = "Tujuan / Sasaran"
    # Col C: Indikator
    ws.merge_cells("C6:C7")
    ws["C6"] = "Indikator"
    # Col D: Satuan
    ws.merge_cells("D6:D7")
    ws["D6"] = "Satuan"
    # Cols E-J: Target Tahun (merged E6:J6)
    ws.merge_cells("E6:J6")
    ws["E6"] = "Target Tahun"
    ws["E7"] = "2025"
    ws["F7"] = "2026"
    ws["G7"] = "2027"
    ws["H7"] = "2028"
    ws["I7"] = "2029"
    ws["J7"] = "2030"

    # Style Header Rows 6 & 7
    for r in [6, 7]:
        for c in range(1, 11):
            cell = ws.cell(row=r, column=c)
            cell.fill = fill_primary
            cell.font = font_header
            cell.alignment = align_center
            cell.border = border_cell

    # 3. Header Row 8 (Column Numbering: 1 to 10)
    for c in range(1, 11):
        cell = ws.cell(row=8, column=c)
        cell.value = c
        cell.fill = fill_num
        cell.font = font_num_header
        cell.alignment = align_center
        cell.border = border_cell

    # 4. Data Rows
    current_row = 9
    groups = report_data.get("groups", [])
    row_counter = 1

    for g in groups:
        g_start_row = current_row
        tujuan_sasaran_text = g.get("tujuan_sasaran", "-")
        ind_list = g.get("indikator_list", [])

        for ind in ind_list:
            r = current_row
            # Col A: No
            cell_a = ws.cell(row=r, column=1, value=row_counter)
            cell_a.fill = fill_no_col
            cell_a.font = font_no_data
            cell_a.alignment = align_center
            cell_a.border = border_cell

            # Col B: Tujuan / Sasaran
            cell_b = ws.cell(row=r, column=2, value=tujuan_sasaran_text)
            cell_b.font = font_data
            cell_b.alignment = align_left
            cell_b.border = border_cell

            # Col C: Indikator
            cell_c = ws.cell(row=r, column=3, value=ind.get("uraian", "-"))
            cell_c.font = font_data
            cell_c.alignment = align_left
            cell_c.border = border_cell

            # Col D: Satuan
            cell_d = ws.cell(row=r, column=4, value=ind.get("satuan", "-"))
            cell_d.font = font_data
            cell_d.alignment = align_center
            cell_d.border = border_cell

            # Cols E-J: Targets 2025-2030
            targets = [
                ind.get("target0", "-"),
                ind.get("target1", "-"),
                ind.get("target2", "-"),
                ind.get("target3", "-"),
                ind.get("target4", "-"),
                ind.get("target5", "-"),
            ]
            for col_idx, t_val in enumerate(targets, 5):
                cell_t = ws.cell(row=r, column=col_idx, value=t_val)
                cell_t.font = font_data
                cell_t.alignment = align_center
                cell_t.border = border_cell

            row_counter += 1
            current_row += 1

        # Merge Col B if group has multiple indicators
        if len(ind_list) > 1:
            ws.merge_cells(start_row=g_start_row, start_column=2, end_row=current_row - 1, end_column=2)

    # If no data
    if not groups:
        cell_empty = ws.cell(row=9, column=1, value="Tidak ada indikator kinerja utama (IKU) yang terdaftar.")
        ws.merge_cells("A9:J9")
        cell_empty.alignment = align_center
        cell_empty.font = font_data
        for c in range(1, 11):
            ws.cell(row=9, column=c).border = border_cell

    # Column Widths
    column_widths = {
        "A": 6,    # No
        "B": 38,   # Tujuan / Sasaran
        "C": 40,   # Indikator
        "D": 14,   # Satuan
        "E": 13,   # 2025
        "F": 13,   # 2026
        "G": 13,   # 2027
        "H": 13,   # 2028
        "I": 13,   # 2029
        "J": 13,   # 2030
    }
    for col_letter, width in column_widths.items():
        ws.column_dimensions[col_letter].width = width

    ws.row_dimensions[2].height = 20
    ws.row_dimensions[3].height = 20
    ws.row_dimensions[4].height = 20
    ws.row_dimensions[6].height = 24
    ws.row_dimensions[7].height = 24
    ws.row_dimensions[8].height = 18

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output



# =====================================================================
# 4. LAPORAN EVALUASI HASIL RENSTRA (PERMENDRAGRI 86/2017)
# =====================================================================

def parse_num_val(v: Any) -> Optional[float]:
    if v is None:
        return None
    s = str(v).strip().replace(".", "").replace(",", ".")
    try:
        return float(s)
    except Exception:
        return None


def calculate_rasio_percentage(realisasi_val: Any, target_val: Any) -> Optional[float]:
    r = parse_num_val(realisasi_val)
    t = parse_num_val(target_val)
    if r is None or t is None:
        return None
    if t == 0:
        return 100.0 if r == 0 else None
    return round((r / t) * 100.0, 2)


def get_predikat_evaluasi(nilai: Optional[float]) -> str:
    if nilai is None:
        return "-"
    if nilai >= 91.0:
        return "Sangat Tinggi"
    elif nilai >= 76.0:
        return "Tinggi"
    elif nilai >= 66.0:
        return "Sedang"
    elif nilai >= 51.0:
        return "Rendah"
    else:
        return "Sangat Rendah"


async def get_evaluasi_renstra_report_data(
    session: AsyncSession, id_skpd: int, id_sub_skpd: Optional[int] = None, tipe: str = "murni"
) -> Dict[str, Any]:
    """
    Mengambil data terstruktur Laporan Evaluasi Hasil Renstra sesuai format Permendagri 86/2017 (Lampiran E.81).
    Total 38 kolom mencakup Sasaran, Program, Kegiatan beserta Target, Realisasi, Rasio Capaian th 1-5, dan Unit Penanggung Jawab.
    """
    opd = await session.get(TaOpd, id_skpd)
    if not opd:
        raise ValueError("Perangkat Daerah tidak ditemukan")

    target_kode = opd.kode_skpd
    sub_title = None

    subs = (await session.exec(
        select(TaSubPd).where(TaSubPd.id_skpd == id_skpd).order_by(TaSubPd.kode_sub_skpd.asc())
    )).all()
    has_multiple_subs = len(subs) > 1
    sub_map = {s.kode_sub_skpd: s.nama_sub_skpd for s in subs if s.kode_sub_skpd}

    if id_sub_skpd:
        sub = await session.get(TaSubPd, id_sub_skpd)
        if sub and sub.kode_sub_skpd:
            target_kodes = [sub.kode_sub_skpd]
            sub_title = sub.nama_sub_skpd
        else:
            target_kodes = [opd.kode_skpd]
    elif has_multiple_subs:
        target_kodes = [s.kode_sub_skpd for s in subs if s.kode_sub_skpd]
        if opd.kode_skpd not in target_kodes:
            target_kodes.append(opd.kode_skpd)
    else:
        target_kodes = [opd.kode_skpd]

    # 1. Query Sasaran
    sasarans = (await session.exec(
        select(RenstraSasaran)
        .where(RenstraSasaran.kodeskpd.in_(target_kodes))
        .order_by(RenstraSasaran.no.asc(), RenstraSasaran.urut.asc(), RenstraSasaran.idsasaran.asc())
    )).all()

    sasaran_ids = [s.idsasaran for s in sasarans]
    ind_sasaran_rows = (await session.exec(
        select(RenstraIndikatorSasaran)
        .where(RenstraIndikatorSasaran.idsasaran.in_(sasaran_ids))
        .order_by(RenstraIndikatorSasaran.idsasaran.asc(), RenstraIndikatorSasaran.idsasaran_indikator.asc())
    )).all() if sasaran_ids else []
    ind_sasaran_map: Dict[str, List[RenstraIndikatorSasaran]] = {}
    for is_ind in ind_sasaran_rows:
        ind_sasaran_map.setdefault(str(is_ind.idsasaran), []).append(is_ind)

    # 2. Query Programs
    programs = (await session.exec(
        select(RenstraProgram)
        .where(RenstraProgram.kodeskpd.in_(target_kodes))
        .order_by(RenstraProgram.kodeskpd.asc(), RenstraProgram.kodebidang.asc(), RenstraProgram.kodeprogram.asc())
    )).all()

    # Preload indicators and children using composite keys (kodeskpd, kode) to prevent crosstalk between sub units
    ind_prog_rows = (await session.exec(
        select(RenstraIndikatorProgram)
        .where(RenstraIndikatorProgram.kodeskpd.in_(target_kodes))
        .order_by(RenstraIndikatorProgram.no.asc(), RenstraIndikatorProgram.urut.asc(), RenstraIndikatorProgram.id.asc())
    )).all() if target_kodes else []
    ind_prog_map: Dict[tuple, List[RenstraIndikatorProgram]] = {}
    for ip in ind_prog_rows:
        ind_prog_map.setdefault((ip.kodeskpd, ip.kodeprogram), []).append(ip)

    # 3. Query Kegiatans
    keg_rows = (await session.exec(
        select(RenstraKegiatan)
        .where(RenstraKegiatan.kodeskpd.in_(target_kodes))
        .order_by(RenstraKegiatan.no.asc(), RenstraKegiatan.kodekegiatan.asc())
    )).all() if target_kodes else []
    keg_map: Dict[tuple, List[RenstraKegiatan]] = {}
    for k in keg_rows:
        keg_map.setdefault((k.kodeskpd, k.kodeprogram), []).append(k)

    ind_keg_rows = (await session.exec(
        select(RenstraIndikatorKegiatan)
        .where(RenstraIndikatorKegiatan.kodeskpd.in_(target_kodes))
        .order_by(RenstraIndikatorKegiatan.no.asc(), RenstraIndikatorKegiatan.urut.asc(), RenstraIndikatorKegiatan.id.asc())
    )).all() if target_kodes else []
    ind_keg_map: Dict[tuple, List[RenstraIndikatorKegiatan]] = {}
    for ik in ind_keg_rows:
        ind_keg_map.setdefault((ik.kodeskpd, ik.kodekegiatan), []).append(ik)

    # 4. Query Subkegiatans (for pagu aggregations)
    subkeg_rows = (await session.exec(
        select(RenstraSubkegiatan)
        .where(RenstraSubkegiatan.kodeskpd.in_(target_kodes))
        .order_by(RenstraSubkegiatan.no.asc(), RenstraSubkegiatan.kodesubkegiatan.asc())
    )).all() if target_kodes else []
    subkeg_map: Dict[tuple, List[RenstraSubkegiatan]] = {}
    for sk in subkeg_rows:
        subkeg_map.setdefault((sk.kodeskpd, sk.kodekegiatan), []).append(sk)

    # Build Pagu maps for Kegiatan and Program
    keg_pagu_map: Dict[tuple, Dict[str, float]] = {}
    for k in keg_rows:
        pagu_dict = {"1": 0.0, "2": 0.0, "3": 0.0, "4": 0.0, "5": 0.0}
        for sk in subkeg_map.get((k.kodeskpd, k.kodekegiatan), []):
            p1 = float(sk.p_pagu1) if tipe == "perubahan" and sk.p_pagu1 is not None and sk.p_pagu1 > 0 else float(sk.pagu1 or 0)
            p2 = float(sk.p_pagu2) if tipe == "perubahan" and sk.p_pagu2 is not None and sk.p_pagu2 > 0 else float(sk.pagu2 or 0)
            p3 = float(sk.p_pagu3) if tipe == "perubahan" and sk.p_pagu3 is not None and sk.p_pagu3 > 0 else float(sk.pagu3 or 0)
            p4 = float(sk.p_pagu4) if tipe == "perubahan" and sk.p_pagu4 is not None and sk.p_pagu4 > 0 else float(sk.pagu4 or 0)
            p5 = float(sk.p_pagu5) if tipe == "perubahan" and sk.p_pagu5 is not None and sk.p_pagu5 > 0 else float(sk.pagu5 or 0)
            pagu_dict["1"] += p1
            pagu_dict["2"] += p2
            pagu_dict["3"] += p3
            pagu_dict["4"] += p4
            pagu_dict["5"] += p5
        keg_pagu_map[(k.kodeskpd, k.kodekegiatan)] = pagu_dict

    prog_pagu_map: Dict[tuple, Dict[str, float]] = {}
    for p in programs:
        p_pagu = {"1": 0.0, "2": 0.0, "3": 0.0, "4": 0.0, "5": 0.0}
        for k in keg_map.get((p.kodeskpd, p.kodeprogram), []):
            kp = keg_pagu_map.get((k.kodeskpd, k.kodekegiatan), {})
            for y in ["1", "2", "3", "4", "5"]:
                p_pagu[y] += kp.get(y, 0.0)
        prog_pagu_map[(p.kodeskpd, p.kodeprogram)] = p_pagu

    # Track all numeric ratios for summary
    all_k_ratios: List[float] = []
    all_rp_ratios: List[float] = []

    # Helper to construct row item
    def build_eval_row(no_val, sasaran_val, prog_keg_val, indikator_val, b_val, akhir_k, akhir_rp, targets_k, pagu_rp, realisasi_k, realisasi_rp, unit_val):
        tahun_targets = {}
        tahun_realisasi = {}
        tahun_rasio = {}

        for y in ["1", "2", "3", "4", "5"]:
            tk = targets_k.get(y, "-")
            trp = pagu_rp.get(y, 0.0)
            rk = realisasi_k.get(y, "-")
            rrp = realisasi_rp.get(y, "-")

            rasio_k = calculate_rasio_percentage(rk, tk)
            rasio_rp = calculate_rasio_percentage(rrp, trp)

            if rasio_k is not None:
                all_k_ratios.append(rasio_k)
            if rasio_rp is not None:
                all_rp_ratios.append(rasio_rp)

            tahun_targets[y] = {"k": tk, "rp": trp}
            tahun_realisasi[y] = {"k": rk, "rp": rrp}
            tahun_rasio[y] = {"k": rasio_k if rasio_k is not None else "-", "rp": rasio_rp if rasio_rp is not None else "-"}

        return {
            "no": no_val,
            "sasaran": sasaran_val,
            "program_kegiatan": prog_keg_val,
            "indikator": indikator_val,
            "awal": b_val,
            "akhir_k": akhir_k,
            "akhir_rp": akhir_rp,
            "tahun_targets": tahun_targets,
            "tahun_realisasi": tahun_realisasi,
            "tahun_rasio": tahun_rasio,
            "unit_pj": unit_val,
        }

    # Build hierarchical rows
    # A. Sasarans
    sasaran_blocks = []
    s_idx = 1
    unit_default = opd.nama_skpd

    for s in sasarans:
        s_id_str = str(s.idsasaran)
        s_inds = ind_sasaran_map.get(s_id_str, [])
        s_rows = []

        # Sasaran Indicators
        if s_inds:
            for is_ind in s_inds:
                b_val = format_target_val(is_ind.target_awal or is_ind.target0)
                t_k = {
                    "1": format_target_val(is_ind.p_target1 if tipe == "perubahan" and is_ind.p_target1 not in (None, "-", "") else is_ind.target1),
                    "2": format_target_val(is_ind.p_target2 if tipe == "perubahan" and is_ind.p_target2 not in (None, "-", "") else is_ind.target2),
                    "3": format_target_val(is_ind.p_target3 if tipe == "perubahan" and is_ind.p_target3 not in (None, "-", "") else is_ind.target3),
                    "4": format_target_val(is_ind.p_target4 if tipe == "perubahan" and is_ind.p_target4 not in (None, "-", "") else is_ind.target4),
                    "5": format_target_val(is_ind.p_target5 if tipe == "perubahan" and is_ind.p_target5 not in (None, "-", "") else is_ind.target5),
                }
                r_k = {
                    "1": format_target_val(is_ind.realisasi1),
                    "2": format_target_val(is_ind.realisasi2),
                    "3": format_target_val(is_ind.realisasi3),
                    "4": format_target_val(is_ind.realisasi4),
                    "5": format_target_val(is_ind.realisasi5),
                }
                # Sasaran usually doesn't have direct pagu, set to 0.0
                zero_pagu = {"1": 0.0, "2": 0.0, "3": 0.0, "4": 0.0, "5": 0.0}
                dash_real = {"1": "-", "2": "-", "3": "-", "4": "-", "5": "-"}
                row = build_eval_row(
                    no_val=str(s_idx),
                    sasaran_val=s.uraisasaran or "-",
                    prog_keg_val="-",
                    indikator_val=is_ind.uraisasaran_indikator or "-",
                    b_val=b_val,
                    akhir_k=t_k["5"],
                    akhir_rp=0.0,
                    targets_k=t_k,
                    pagu_rp=zero_pagu,
                    realisasi_k=r_k,
                    realisasi_rp=dash_real,
                    unit_val=unit_default,
                )
                row["level"] = "sasaran"
                s_rows.append(row)
        else:
            zero_pagu = {"1": 0.0, "2": 0.0, "3": 0.0, "4": 0.0, "5": 0.0}
            dash_real = {"1": "-", "2": "-", "3": "-", "4": "-", "5": "-"}
            row = build_eval_row(
                no_val=str(s_idx),
                sasaran_val=s.uraisasaran or "-",
                prog_keg_val="-",
                indikator_val="-",
                b_val="-",
                akhir_k="-",
                akhir_rp=0.0,
                targets_k=dash_real,
                pagu_rp=zero_pagu,
                realisasi_k=dash_real,
                realisasi_rp=dash_real,
                unit_val=unit_default,
            )
            row["level"] = "sasaran"
            s_rows.append(row)

        s_idx += 1
        sasaran_blocks.append({
            "sasaran": s,
            "rows": s_rows,
        })

    # B. Programs and Kegiatans
    def build_program_and_children_rows(prog_list: List[RenstraProgram], unit_override: Optional[str] = None) -> List[Dict[str, Any]]:
        rows = []
        for p in prog_list:
            p_inds = ind_prog_map.get((p.kodeskpd, p.kodeprogram), [])
            p_pagu = prog_pagu_map.get((p.kodeskpd, p.kodeprogram), {"1": 0.0, "2": 0.0, "3": 0.0, "4": 0.0, "5": 0.0})
            total_p_pagu_akhir = sum(p_pagu.values())
            unit_p = unit_override or p.uraibidang or unit_default

            if p_inds:
                for ip in p_inds:
                    b_val = format_target_val(ip.target_awal or ip.target0)
                    t_k = {
                        "1": format_target_val(ip.p_target1 if tipe == "perubahan" and ip.p_target1 not in (None, "-", "") else ip.target1),
                        "2": format_target_val(ip.p_target2 if tipe == "perubahan" and ip.p_target2 not in (None, "-", "") else ip.target2),
                        "3": format_target_val(ip.p_target3 if tipe == "perubahan" and ip.p_target3 not in (None, "-", "") else ip.target3),
                        "4": format_target_val(ip.p_target4 if tipe == "perubahan" and ip.p_target4 not in (None, "-", "") else ip.target4),
                        "5": format_target_val(ip.p_target5 if tipe == "perubahan" and ip.p_target5 not in (None, "-", "") else ip.target5),
                    }
                    r_k = {
                        "1": format_target_val(ip.realisasi1),
                        "2": format_target_val(ip.realisasi2),
                        "3": format_target_val(ip.realisasi3),
                        "4": format_target_val(ip.realisasi4),
                        "5": format_target_val(ip.realisasi5),
                    }
                    dash_real_rp = {"1": "-", "2": "-", "3": "-", "4": "-", "5": "-"}
                    row = build_eval_row(
                        no_val=p.kodeprogram or "-",
                        sasaran_val="-",
                        prog_keg_val=p.uraiprogram or "-",
                        indikator_val=ip.uraiindikator or "-",
                        b_val=b_val,
                        akhir_k=t_k["5"],
                        akhir_rp=total_p_pagu_akhir,
                        targets_k=t_k,
                        pagu_rp=p_pagu,
                        realisasi_k=r_k,
                        realisasi_rp=dash_real_rp,
                        unit_val=unit_p,
                    )
                    row["level"] = "program"
                    rows.append(row)
            else:
                dash_real = {"1": "-", "2": "-", "3": "-", "4": "-", "5": "-"}
                row = build_eval_row(
                    no_val=p.kodeprogram or "-",
                    sasaran_val="-",
                    prog_keg_val=p.uraiprogram or "-",
                    indikator_val="-",
                    b_val="-",
                    akhir_k="-",
                    akhir_rp=total_p_pagu_akhir,
                    targets_k=dash_real,
                    pagu_rp=p_pagu,
                    realisasi_k=dash_real,
                    realisasi_rp=dash_real,
                    unit_val=unit_p,
                )
                row["level"] = "program"
                rows.append(row)

            # C. Kegiatans under this program
            for k in keg_map.get((p.kodeskpd, p.kodeprogram), []):
                k_inds = ind_keg_map.get((k.kodeskpd, k.kodekegiatan), [])
                k_pagu = keg_pagu_map.get((k.kodeskpd, k.kodekegiatan), {"1": 0.0, "2": 0.0, "3": 0.0, "4": 0.0, "5": 0.0})
                total_k_pagu_akhir = sum(k_pagu.values())

                if k_inds:
                    for ik in k_inds:
                        b_val = format_target_val(ik.target_awal or ik.target0)
                        t_k = {
                            "1": format_target_val(ik.p_target1 if tipe == "perubahan" and ik.p_target1 not in (None, "-", "") else ik.target1),
                            "2": format_target_val(ik.p_target2 if tipe == "perubahan" and ik.p_target2 not in (None, "-", "") else ik.target2),
                            "3": format_target_val(ik.p_target3 if tipe == "perubahan" and ik.p_target3 not in (None, "-", "") else ik.target3),
                            "4": format_target_val(ik.p_target4 if tipe == "perubahan" and ik.p_target4 not in (None, "-", "") else ik.target4),
                            "5": format_target_val(ik.p_target5 if tipe == "perubahan" and ik.p_target5 not in (None, "-", "") else ik.target5),
                        }
                        r_k = {
                            "1": format_target_val(ik.realisasi1),
                            "2": format_target_val(ik.realisasi2),
                            "3": format_target_val(ik.realisasi3),
                            "4": format_target_val(ik.realisasi4),
                            "5": format_target_val(ik.realisasi5),
                        }
                        dash_real_rp = {"1": "-", "2": "-", "3": "-", "4": "-", "5": "-"}
                        row = build_eval_row(
                            no_val=k.kodekegiatan or "-",
                            sasaran_val="-",
                            prog_keg_val=k.uraikegiatan or "-",
                            indikator_val=ik.uraiindikator or "-",
                            b_val=b_val,
                            akhir_k=t_k["5"],
                            akhir_rp=total_k_pagu_akhir,
                            targets_k=t_k,
                            pagu_rp=k_pagu,
                            realisasi_k=r_k,
                            realisasi_rp=dash_real_rp,
                            unit_val=unit_p,
                        )
                        row["level"] = "kegiatan"
                        rows.append(row)
                else:
                    dash_real = {"1": "-", "2": "-", "3": "-", "4": "-", "5": "-"}
                    row = build_eval_row(
                        no_val=k.kodekegiatan or "-",
                        sasaran_val="-",
                        prog_keg_val=k.uraikegiatan or "-",
                        indikator_val="-",
                        b_val="-",
                        akhir_k="-",
                        akhir_rp=total_k_pagu_akhir,
                        targets_k=dash_real,
                        pagu_rp=k_pagu,
                        realisasi_k=dash_real,
                        realisasi_rp=dash_real,
                        unit_val=unit_p,
                    )
                    row["level"] = "kegiatan"
                    rows.append(row)

                # D. Subkegiatans under this kegiatan
                for sk in subkeg_map.get((k.kodeskpd, k.kodekegiatan), []):
                    sk_b_val = format_target_val(sk.volume_awal or sk.volume_0)
                    sk_t_k = {
                        "1": format_target_val(sk.p_volume_1 if tipe == "perubahan" and sk.p_volume_1 not in (None, "-", "") else sk.volume_1),
                        "2": format_target_val(sk.p_volume_2 if tipe == "perubahan" and sk.p_volume_2 not in (None, "-", "") else sk.volume_2),
                        "3": format_target_val(sk.p_volume_3 if tipe == "perubahan" and sk.p_volume_3 not in (None, "-", "") else sk.volume_3),
                        "4": format_target_val(sk.p_volume_4 if tipe == "perubahan" and sk.p_volume_4 not in (None, "-", "") else sk.volume_4),
                        "5": format_target_val(sk.p_volume_5 if tipe == "perubahan" and sk.p_volume_5 not in (None, "-", "") else sk.volume_5),
                    }
                    sk_r_k = {
                        "1": format_target_val(sk.realisasi1),
                        "2": format_target_val(sk.realisasi2),
                        "3": format_target_val(sk.realisasi3),
                        "4": format_target_val(sk.realisasi4),
                        "5": format_target_val(sk.realisasi5),
                    }
                    sk_pagu = {
                        "1": float(sk.p_pagu1) if tipe == "perubahan" and sk.p_pagu1 is not None and sk.p_pagu1 > 0 else float(sk.pagu1 or 0),
                        "2": float(sk.p_pagu2) if tipe == "perubahan" and sk.p_pagu2 is not None and sk.p_pagu2 > 0 else float(sk.pagu2 or 0),
                        "3": float(sk.p_pagu3) if tipe == "perubahan" and sk.p_pagu3 is not None and sk.p_pagu3 > 0 else float(sk.pagu3 or 0),
                        "4": float(sk.p_pagu4) if tipe == "perubahan" and sk.p_pagu4 is not None and sk.p_pagu4 > 0 else float(sk.pagu4 or 0),
                        "5": float(sk.p_pagu5) if tipe == "perubahan" and sk.p_pagu5 is not None and sk.p_pagu5 > 0 else float(sk.pagu5 or 0),
                    }
                    total_sk_pagu_akhir = sum(sk_pagu.values())
                    dash_real_rp = {"1": "-", "2": "-", "3": "-", "4": "-", "5": "-"}

                    sk_row = build_eval_row(
                        no_val=sk.kodesubkegiatan or "-",
                        sasaran_val="-",
                        prog_keg_val=sk.uraisubkegiatan or "-",
                        indikator_val=sk.uraisubkegiatan_indikator or "-",
                        b_val=sk_b_val,
                        akhir_k=sk_t_k["5"],
                        akhir_rp=total_sk_pagu_akhir,
                        targets_k=sk_t_k,
                        pagu_rp=sk_pagu,
                        realisasi_k=sk_r_k,
                        realisasi_rp=dash_real_rp,
                        unit_val=unit_p,
                    )
                    sk_row["level"] = "subkegiatan"
                    rows.append(sk_row)
        return rows

    program_rows = []
    if has_multiple_subs and not id_sub_skpd:
        # Group programs by sub unit
        progs_by_sub: Dict[str, List[RenstraProgram]] = {}
        for p in programs:
            progs_by_sub.setdefault(p.kodeskpd, []).append(p)

        for s in subs:
            s_progs = progs_by_sub.get(s.kode_sub_skpd, [])
            if s_progs:
                # Calculate sub unit total pagu
                s_pagu = {"1": 0.0, "2": 0.0, "3": 0.0, "4": 0.0, "5": 0.0}
                for sp in s_progs:
                    spp = prog_pagu_map.get((sp.kodeskpd, sp.kodeprogram), {})
                    for y in ["1", "2", "3", "4", "5"]:
                        s_pagu[y] += spp.get(y, 0.0)
                sub_total_pagu_akhir = sum(s_pagu.values())

                dash_real = {"1": "-", "2": "-", "3": "-", "4": "-", "5": "-"}
                sub_header_row = build_eval_row(
                    no_val=s.kode_sub_skpd,
                    sasaran_val="-",
                    prog_keg_val=f"{s.nama_sub_skpd.upper()}",
                    indikator_val="-",
                    b_val="-",
                    akhir_k="-",
                    akhir_rp=sub_total_pagu_akhir,
                    targets_k=dash_real,
                    pagu_rp=s_pagu,
                    realisasi_k=dash_real,
                    realisasi_rp=dash_real,
                    unit_val=s.nama_sub_skpd,
                )
                sub_header_row["level"] = "sub_unit"
                program_rows.append(sub_header_row)

                # Add this sub unit's programs and children
                program_rows.extend(build_program_and_children_rows(s_progs, unit_override=s.nama_sub_skpd))
    else:
        program_rows = build_program_and_children_rows(programs)

    # Combine all evaluation rows in standard sequence: Sasaran rows, followed by Program & Kegiatan rows
    all_rows = []
    for sb in sasaran_blocks:
        all_rows.extend(sb["rows"])
    all_rows.extend(program_rows)

    # Calculate overall average ratio and performance predicate
    avg_k_ratio = round(sum(all_k_ratios) / len(all_k_ratios), 2) if all_k_ratios else None
    avg_rp_ratio = round(sum(all_rp_ratios) / len(all_rp_ratios), 2) if all_rp_ratios else None
    combined_ratios = all_k_ratios + all_rp_ratios
    grand_avg_ratio = round(sum(combined_ratios) / len(combined_ratios), 2) if combined_ratios else None
    predikat = get_predikat_evaluasi(grand_avg_ratio or avg_k_ratio)

    return {
        "opd": {
            "id_skpd": opd.id_skpd,
            "kode_skpd": opd.kode_skpd,
            "nama_skpd": opd.nama_skpd,
            "sub_title": sub_title,
        },
        "tipe": tipe,
        "has_multiple_subs": has_multiple_subs and not id_sub_skpd,
        "rows": all_rows,
        "summary": {
            "total_sasaran": len(sasarans),
            "total_program": len(programs),
            "total_kegiatan": len(keg_rows),
            "total_subkegiatan": len(subkeg_rows),
            "rata_rata_k": avg_k_ratio,
            "rata_rata_rp": avg_rp_ratio,
            "rata_rata_capaian": grand_avg_ratio or avg_k_ratio,
            "predikat_kinerja": predikat,
            "faktor_pendorong": "-",
            "faktor_penghambat": "-",
            "usulan_renja": "-",
            "usulan_renstra": "-",
        },
    }


def generate_evaluasi_renstra_excel(report_data: Dict[str, Any]) -> io.BytesIO:
    """
    Generate Excel (.xlsx) file matching the exact standard layout of Formulir Evaluasi Renstra Permendagri 86/2017 (38 Columns).
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Evaluasi Hasil Renstra"
    ws.views.sheetView[0].showGridLines = True

    COLOR_HEADER_BG = "B4C6E7"    # Steel Blue / Soft Lavender
    COLOR_GUIDE_BG  = "D9E1F2"    # Light Ice Blue
    COLOR_SUBUNIT   = "BDD7EE"    # Soft Header Blue for Sub Unit
    COLOR_SASARAN   = "FFF2CC"    # Soft Light Yellow for Sasaran
    COLOR_PROGRAM   = "FCE4D6"    # Soft Peach for Program
    COLOR_KEGIATAN  = "E2EFDA"    # Soft Pastel Green for Kegiatan
    COLOR_WHITE     = "FFFFFF"
    COLOR_BORDER    = "94A3B8"
    COLOR_BLACK     = "000000"

    font_title_bold = Font(name="Calibri", size=11, bold=True)
    font_header_bold = Font(name="Calibri", size=9.5, bold=True, color=COLOR_BLACK)
    font_guide = Font(name="Calibri", size=8.5, bold=True, color=COLOR_BLACK)
    font_subunit = Font(name="Calibri", size=9.5, bold=True, color=COLOR_BLACK)
    font_row_bold = Font(name="Calibri", size=9.5, bold=True, color=COLOR_BLACK)
    font_row_regular = Font(name="Calibri", size=9, bold=False, color=COLOR_BLACK)

    fill_header = PatternFill(start_color=COLOR_HEADER_BG, end_color=COLOR_HEADER_BG, fill_type="solid")
    fill_guide = PatternFill(start_color=COLOR_GUIDE_BG, end_color=COLOR_GUIDE_BG, fill_type="solid")
    fill_subunit = PatternFill(start_color=COLOR_SUBUNIT, end_color=COLOR_SUBUNIT, fill_type="solid")
    fill_sasaran = PatternFill(start_color=COLOR_SASARAN, end_color=COLOR_SASARAN, fill_type="solid")
    fill_program = PatternFill(start_color=COLOR_PROGRAM, end_color=COLOR_PROGRAM, fill_type="solid")
    fill_kegiatan = PatternFill(start_color=COLOR_KEGIATAN, end_color=COLOR_KEGIATAN, fill_type="solid")

    thin_border_side = Side(border_style="thin", color=COLOR_BORDER)
    border_cell = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)

    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
    align_right = Alignment(horizontal="right", vertical="center")

    opd_info = report_data.get("opd", {})
    nama_skpd = opd_info.get("nama_skpd", "Perangkat Daerah")
    sub_title = opd_info.get("sub_title")
    title_unit = f"{nama_skpd} - {sub_title}" if sub_title else nama_skpd

    # Title block
    ws.merge_cells("A1:AL1")
    ws["A1"] = "EVALUASI HASIL RENCANA STRATEGIS PERANGKAT DAERAH (RENSTRA)"
    ws["A1"].font = Font(name="Calibri", size=12, bold=True)
    ws["A1"].alignment = align_center

    ws.merge_cells("A2:AL2")
    ws["A2"] = title_unit.upper()
    ws["A2"].font = font_title_bold
    ws["A2"].alignment = align_center

    ws.merge_cells("A3:AL3")
    ws["A3"] = "KOTA TEGAL"
    ws["A3"].font = font_title_bold
    ws["A3"].alignment = align_center

    # Row 5 to 9: Headers matching user CSV specification
    # Header Row 1 (Row 5 in Excel):
    # A5:D6 merged for No, Sasaran, Program/Kegiatan, Indikator Kinerja
    ws.merge_cells("A5:A7")
    ws["A5"] = "No"
    ws.merge_cells("B5:B7")
    ws["B5"] = "Sasaran"
    ws.merge_cells("C5:C7")
    ws["C5"] = "Program/Kegiatan/\nSub Kegiatan"
    ws.merge_cells("D5:D7")
    ws["D5"] = "Indikator Kinerja"

    # E5:E7: Data Capaian Pada Awal Tahun Perencanaan
    ws.merge_cells("E5:E7")
    ws["E5"] = "Data Capaian Pada Awal Tahun\nPerencanaan"

    # F5:G6: Target Capaian pada Akhir Tahun Perencanaan
    ws.merge_cells("F5:G6")
    ws["F5"] = "Target Capaian pada Akhir Tahun\nPerencanaan"

    # H5:Q5: Target Renstra Perangkat Daerah kabupaten/kota Tahun ke-
    ws.merge_cells("H5:Q5")
    ws["H5"] = "Target Renstra Perangkat Daerah kabupaten/kota Tahun ke-"

    # R5:AA5: Realisasi Capaian Tahun ke-
    ws.merge_cells("R5:AA5")
    ws["R5"] = "Realisasi Capaian Tahun ke-"

    # AB5:AK5: Rasio Capaian pada Tahun ke-
    ws.merge_cells("AB5:AK5")
    ws["AB5"] = "Rasio Capaian pada Tahun ke-"

    # AL5:AL7: Unit Penang- gung Jawab
    ws.merge_cells("AL5:AL7")
    ws["AL5"] = "Unit Penang-\ngung Jawab"

    # Header Row 2 (Row 6 in Excel): Years 1 to 5
    # Target Years (H6..Q6)
    ws.merge_cells("H6:I6")
    ws["H6"] = "1"
    ws.merge_cells("J6:K6")
    ws["J6"] = "2"
    ws.merge_cells("L6:M6")
    ws["L6"] = "3"
    ws.merge_cells("N6:O6")
    ws["N6"] = "4"
    ws.merge_cells("P6:Q6")
    ws["P6"] = "5"

    # Realisasi Years (R6..AA6)
    ws.merge_cells("R6:S6")
    ws["R6"] = "1"
    ws.merge_cells("T6:U6")
    ws["T6"] = "2"
    ws.merge_cells("V6:W6")
    ws["V6"] = "3"
    ws.merge_cells("X6:Y6")
    ws["X6"] = "4"
    ws.merge_cells("Z6:AA6")
    ws["Z6"] = "5"

    # Rasio Years (AB6..AK6)
    ws.merge_cells("AB6:AC6")
    ws["AB6"] = "1"
    ws.merge_cells("AD6:AE6")
    ws["AD6"] = "2"
    ws.merge_cells("AF6:AG6")
    ws["AF6"] = "3"
    ws.merge_cells("AH6:AI6")
    ws["AH6"] = "4"
    ws.merge_cells("AJ6:AK6")
    ws["AJ6"] = "5"

    # Header Row 3 (Row 7 in Excel): K & Rp
    pairs = [
        ("F7", "G7"),
        ("H7", "I7"), ("J7", "K7"), ("L7", "M7"), ("N7", "O7"), ("P7", "Q7"),
        ("R7", "S7"), ("T7", "U7"), ("V7", "W7"), ("X7", "Y7"), ("Z7", "AA7"),
        ("AB7", "AC7"), ("AD7", "AE7"), ("AF7", "AG7"), ("AH7", "AI7"), ("AJ7", "AK7")
    ]
    for k_cell, rp_cell in pairs:
        ws[k_cell] = "K"
        ws[rp_cell] = "Rp"

    # Header Row 4 (Row 8 in Excel): Column Numbering Guide (-1 .. -22)
    guide_vals = [
        ("A8", "(1)"), ("B8", "(2)"), ("C8", "(3)"), ("D8", "(4)"), ("E8", "(5)"),
        ("F8:G8", "(6)"),
        ("H8:I8", "(7)"), ("J8:K8", "(8)"), ("L8:M8", "(9)"), ("N8:O8", "(10)"), ("P8:Q8", "(11)"),
        ("R8:S8", "(12)"), ("T8:U8", "(13)"), ("V8:W8", "(14)"), ("X8:Y8", "(15)"), ("Z8:AA8", "(16)"),
        ("AB8:AC8", "(17)"), ("AD8:AE8", "(18)"), ("AF8:AG8", "(19)"), ("AH8:AI8", "(20)"), ("AJ8:AK8", "(21)"),
        ("AL8", "(22)")
    ]
    for ref, g_txt in guide_vals:
        if ":" in ref:
            ws.merge_cells(ref)
            first_c = ref.split(":")[0]
            ws[first_c] = g_txt
        else:
            ws[ref] = g_txt

    # Format header styles
    for r in range(5, 8):
        ws.row_dimensions[r].height = 22
        for col in range(1, 39):
            cell = ws.cell(row=r, column=col)
            cell.fill = fill_header
            cell.font = font_header_bold
            cell.alignment = align_center
            cell.border = border_cell

    ws.row_dimensions[8].height = 18
    for col in range(1, 39):
        cell = ws.cell(row=8, column=col)
        cell.fill = fill_guide
        cell.font = font_guide
        cell.alignment = align_center
        cell.border = border_cell

    current_row = 9

    # Populate Data Rows
    for row_data in report_data.get("rows", []):
        level = row_data.get("level", "kegiatan")
        ws.row_dimensions[current_row].height = 24 if level == "sub_unit" else 22

        if level == "sub_unit":
            fill_lvl = fill_subunit
            font_lvl = font_subunit
        elif level == "sasaran":
            fill_lvl = fill_sasaran
            font_lvl = font_row_bold
        elif level == "program":
            fill_lvl = fill_program
            font_lvl = font_row_bold
        elif level == "kegiatan":
            fill_lvl = fill_kegiatan
            font_lvl = Font(name="Calibri", size=9, bold=True, color=COLOR_BLACK)
        else:
            fill_lvl = None
            font_lvl = font_row_regular

        ws.cell(row=current_row, column=1, value=row_data.get("no", "")).alignment = align_left
        ws.cell(row=current_row, column=2, value=row_data.get("sasaran", "-")).alignment = align_left
        ws.cell(row=current_row, column=3, value=row_data.get("program_kegiatan", "-")).alignment = align_left
        ws.cell(row=current_row, column=4, value=row_data.get("indikator", "-")).alignment = align_left
        ws.cell(row=current_row, column=5, value=row_data.get("awal", "-")).alignment = align_center

        # Col 6 & 7: Target Akhir Renstra
        ws.cell(row=current_row, column=6, value=row_data.get("akhir_k", "-")).alignment = align_center
        c_ak_rp = ws.cell(row=current_row, column=7, value=row_data.get("akhir_rp", 0.0))
        c_ak_rp.number_format = "#,##0"
        c_ak_rp.alignment = align_right

        # Col 8 to 17: Target Th 1..5
        t_targets = row_data.get("tahun_targets", {})
        for idx, y in enumerate(["1", "2", "3", "4", "5"]):
            k_col = 8 + (idx * 2)
            rp_col = k_col + 1
            ws.cell(row=current_row, column=k_col, value=t_targets.get(y, {}).get("k", "-")).alignment = align_center
            c_p = ws.cell(row=current_row, column=rp_col, value=t_targets.get(y, {}).get("rp", 0.0))
            c_p.number_format = "#,##0"
            c_p.alignment = align_right

        # Col 18 to 27: Realisasi Th 1..5
        t_real = row_data.get("tahun_realisasi", {})
        for idx, y in enumerate(["1", "2", "3", "4", "5"]):
            k_col = 18 + (idx * 2)
            rp_col = k_col + 1
            ws.cell(row=current_row, column=k_col, value=t_real.get(y, {}).get("k", "-")).alignment = align_center
            c_rp = ws.cell(row=current_row, column=rp_col, value=t_real.get(y, {}).get("rp", "-"))
            if isinstance(c_rp.value, (int, float)):
                c_rp.number_format = "#,##0"
                c_rp.alignment = align_right
            else:
                c_rp.alignment = align_center

        # Col 28 to 37: Rasio Th 1..5
        t_rasio = row_data.get("tahun_rasio", {})
        for idx, y in enumerate(["1", "2", "3", "4", "5"]):
            k_col = 28 + (idx * 2)
            rp_col = k_col + 1
            ws.cell(row=current_row, column=k_col, value=t_rasio.get(y, {}).get("k", "-")).alignment = align_center
            ws.cell(row=current_row, column=rp_col, value=t_rasio.get(y, {}).get("rp", "-")).alignment = align_center

        # Col 38: Unit Penanggung Jawab
        ws.cell(row=current_row, column=38, value=row_data.get("unit_pj", "-")).alignment = align_left

        for c in range(1, 39):
            cell = ws.cell(row=current_row, column=c)
            cell.font = font_lvl
            cell.border = border_cell
            if fill_lvl:
                cell.fill = fill_lvl

        current_row += 1

    # Footer Section matching user CSV
    summary = report_data.get("summary", {})

    footer_items = [
        ("Rata-rata capaian kinerja (%)", f"{summary.get('rata_rata_capaian', '-')}%" if summary.get('rata_rata_capaian') is not None else "-"),
        ("Predikat kinerja", summary.get("predikat_kinerja", "-")),
        ("Faktor pendorong pencapaian kinerja:", summary.get("faktor_pendorong", "-")),
        ("Faktor penghambat:", summary.get("faktor_penghambat", "-")),
        ("Usulan tindak lanjut pada Renja Perangkat Daerah kabupaten/kota berikutnya:", summary.get("usulan_renja", "-")),
        ("Usulan tindak lanjut pada Renstra Perangkat Daerah kabupaten/kota berikutnya:", summary.get("usulan_renstra", "-")),
    ]

    for label, val in footer_items:
        ws.row_dimensions[current_row].height = 20
        ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=4)
        cell_lbl = ws.cell(row=current_row, column=1, value=label)
        cell_lbl.font = font_row_bold
        cell_lbl.alignment = align_left

        ws.merge_cells(start_row=current_row, start_column=5, end_row=current_row, end_column=38)
        cell_v = ws.cell(row=current_row, column=5, value=val)
        cell_v.font = font_row_regular
        cell_v.alignment = align_left

        for c in range(1, 39):
            ws.cell(row=current_row, column=c).border = border_cell

        current_row += 1

    # Auto set column widths for 38 columns
    col_widths = {
        1: 18, 2: 32, 3: 35, 4: 35, 5: 12, 6: 10, 7: 18,
        8: 10, 9: 18, 10: 10, 11: 18, 12: 10, 13: 18, 14: 10, 15: 18, 16: 10, 17: 18,
        18: 10, 19: 18, 20: 10, 21: 18, 22: 10, 23: 18, 24: 10, 25: 18, 26: 10, 27: 18,
        28: 10, 29: 10, 30: 10, 31: 10, 32: 10, 33: 10, 34: 10, 35: 10, 36: 10, 37: 10,
        38: 28
    }
    for col_idx, width in col_widths.items():
        col_letter = openpyxl.utils.get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = width

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output
