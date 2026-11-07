import io
import re
from typing import Any, Dict, List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from app.models.opd import TaOpd
from app.models.renstra import (
    RenstraIndikatorSasaran,
    RenstraIndikatorTujuan,
    RenstraSasaran,
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

