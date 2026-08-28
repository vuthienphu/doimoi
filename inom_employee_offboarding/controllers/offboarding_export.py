# -*- coding: utf-8 -*-
import json
import io
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.label import DataLabelList
from odoo import http
from odoo.http import request, content_disposition

# Tông màu bám theo file mẫu bao_cao.xlsx
COLOR_PRIMARY = '5C3A4E'   # tím đậm: header, tiêu đề
COLOR_SOFT = 'F4EEF2'      # nền nhạt: KPI, dòng tổng
FONT_NAME = 'Arial'


def _font(**kwargs):
    """Font mặc định Arial cho toàn bộ báo cáo."""
    kwargs.setdefault('name', FONT_NAME)
    return Font(**kwargs)


class OffboardingExportController(http.Controller):

    @http.route('/offboarding/export/xlsx', type='http', auth='user', methods=['GET'])
    def export_xlsx(self, **kwargs):
        domain_raw = kwargs.get('domain', '[]')
        mode = kwargs.get('mode', 'year')
        year = kwargs.get('year', '')
        quarter = kwargs.get('quarter', '')
        month = kwargs.get('month', '')

        try:
            domain = json.loads(domain_raw)
        except Exception:
            domain = []

        rows = request.env['inom.offboarding.request'].get_dashboard_export_data(domain)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Dữ liệu nghỉ việc'

        # ---- Tiêu đề ----
        ws.merge_cells('A1:K1')
        title_cell = ws['A1']
        title_cell.value = 'DANH SÁCH NHÂN SỰ NGHỈ VIỆC'
        title_cell.font = _font(bold=True, size=14)
        title_cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        ws.row_dimensions[1].height = 28

        # ---- Thông tin filter ----
        filter_label = _build_filter_label(mode, year, quarter, month)
        ws.merge_cells('A2:K2')
        filter_cell = ws['A2']
        filter_cell.value = filter_label
        filter_cell.font = _font()
        filter_cell.alignment = Alignment(horizontal='center', wrap_text=True)

        # ---- Xác định tên cột cuối (J, K) theo chế độ filter ----
        col_j_header, col_k_header = _time_column_headers(mode, quarter)

        # ---- Header hàng 4 ----
        HEADERS = [
            'Email', 'Họ tên', 'Phòng ban', 'Level',
            'Loại nghỉ', 'Lý do nghỉ',
            'Ngày vào làm', 'Ngày nghỉ việc',
            'Thâm niên (năm)', col_j_header, col_k_header,
        ]
        header_fill = PatternFill('solid', fgColor='4A2F42')
        thin = Side(style='thin', color='CCCCCC')
        border = Border(left=thin, right=thin, top=thin, bottom=thin)

        for col_idx, header in enumerate(HEADERS, start=1):
            cell = ws.cell(row=4, column=col_idx, value=header)
            cell.font = _font(bold=True, color='FFFFFF', size=10)
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell.border = border
        ws.row_dimensions[4].height = 32

        # ---- Dữ liệu ----
        alt_fill = PatternFill('solid', fgColor='F9F0F6')
        for row_idx, rec in enumerate(rows, start=5):
            data = [
                rec['work_email'],
                rec['employee_name'],
                rec['department'],
                rec['level'],
                rec['offboarding_type'],
                rec['reason'],
                rec['start_date'],
                rec['last_day'],
                rec['tenure_years'],
                _time_col_j_value(rec, mode),
                _time_col_k_value(rec, mode, quarter),
            ]
            fill = alt_fill if row_idx % 2 == 0 else None
            for col_idx, value in enumerate(data, start=1):
                cell = ws.cell(row=row_idx, column=col_idx, value=value)
                cell.font = _font(size=10)
                cell.alignment = Alignment(vertical='center', wrap_text=True)
                cell.border = border
                if fill:
                    cell.fill = fill

        # ---- Độ rộng cột ----
        col_widths = [36, 24, 22, 14, 26, 26, 16, 16, 16, 14, 10]
        for i, w in enumerate(col_widths, start=1):
            ws.column_dimensions[get_column_letter(i)].width = w

        # ---- Sheet Báo cáo + Danh mục ----
        report_data = request.env['inom.offboarding.request'].get_report_export_data(
            domain, mode, year, quarter, month)
        categories = request.env['inom.offboarding.request'].get_report_categories()
        _build_report_sheet(wb, report_data, year)
        _build_category_sheet(wb, categories)

        # ---- Xuất file ----
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        filename = 'bao_cao_nghi_viec.xlsx'
        return request.make_response(
            buf.read(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', content_disposition(filename)),
            ]
        )


def _build_filter_label(mode, year, quarter, month):
    MONTH_NAMES = ['', 'Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5', 'Tháng 6',
                   'Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10', 'Tháng 11', 'Tháng 12']
    parts = []
    if year:
        parts.append('Năm %s' % year)
    if mode == 'quarter' and quarter:
        parts.append('Quý %s' % quarter)
    if mode == 'month' and month:
        try:
            parts.append(MONTH_NAMES[int(month)])
        except (IndexError, ValueError):
            parts.append('Tháng %s' % month)
    return ' | '.join(parts) if parts else ''


def _time_column_headers(mode, quarter):
    """Trả về (tên cột J, tên cột K) tùy filter."""
    if mode == 'year':
        # Khi lọc Năm: J = Quý, K = Năm
        return 'Quý', 'Năm'
    if mode == 'quarter':
        if quarter:
            # Khi lọc Quý cụ thể: J = Tháng, K = Quý
            return 'Tháng', 'Quý'
        # Khi Quý = "Tất cả": J = Quý, K = Năm
        return 'Quý', 'Năm'
    # mode == 'month'
    if True:  # month filter (kể cả "Tất cả")
        # J = Tháng, K = Năm  (hoặc Quý nếu có cả month)
        return 'Tháng', 'Năm'


def _time_col_j_value(rec, mode):
    """Giá trị cột J theo mode."""
    if mode == 'year':
        return rec['quarter']
    if mode == 'quarter':
        # lấy tháng từ last_day
        return _month_from_date_str(rec['last_day'])
    # month
    return _month_from_date_str(rec['last_day'])


def _time_col_k_value(rec, mode, quarter):
    """Giá trị cột K theo mode."""
    if mode == 'year':
        return rec['year']
    if mode == 'quarter':
        if quarter:
            return rec['quarter']
        return rec['year']
    # month
    return rec['year']


def _month_from_date_str(date_str):
    """Lấy tháng từ chuỗi dd/mm/yyyy."""
    if not date_str:
        return ''
    try:
        return int(date_str.split('/')[1])
    except Exception:
        return ''


# ======================================================================
# Sheet "Báo cáo"
# ======================================================================
def _hdr_cell(ws, coord, value):
    """Ô header nền tím, chữ trắng, canh giữa."""
    c = ws[coord]
    c.value = value
    c.font = _font(bold=True, color='FFFFFF', size=10)
    c.fill = PatternFill('solid', fgColor=COLOR_PRIMARY)
    c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    return c


def _build_report_sheet(wb, data, year):
    ws = wb.create_sheet('Báo cáo')
    kpi = data['kpi']
    trend = data['trend']

    # Độ rộng cột theo mẫu
    for col, w in {'A': 3, 'B': 26, 'C': 26, 'D': 20, 'E': 12,
                   'F': 17, 'G': 12, 'H': 14, 'I': 12, 'J': 3}.items():
        ws.column_dimensions[col].width = w

    # ---- Tiêu đề ----
    ws.merge_cells('B2:I2')
    t = ws['B2']
    t.value = 'BÁO CÁO XU HƯỚNG NGHỈ VIỆC'
    t.font = _font(bold=True, size=18, color=COLOR_PRIMARY)
    t.alignment = Alignment(wrap_text=True)

    ws['B4'].value = 'Năm báo cáo:'
    ws['B4'].font = _font(bold=True, size=10, color=COLOR_PRIMARY)
    ws['B4'].alignment = Alignment(wrap_text=True)
    ws['C4'].value = '→'
    ws['C4'].alignment = Alignment(wrap_text=True)
    yc = ws['D4']
    yc.value = int(year) if year else ''
    yc.font = _font(bold=True, color='0000FF')
    yc.fill = PatternFill('solid', fgColor='FFF9E6')
    yc.alignment = Alignment(horizontal='center', wrap_text=True)

    ws.merge_cells('E4:F4')
    ws['E4'].value = 'Số nhân sự bình quân:'
    ws['E4'].font = _font(bold=True, size=10, color=COLOR_PRIMARY)
    ws['E4'].alignment = Alignment(wrap_text=True)
    hc = ws['H4']
    hc.value = kpi.get('avg_headcount', 0)
    hc.font = _font(bold=True, color='0000FF')
    hc.fill = PatternFill('solid', fgColor='FFF9E6')
    hc.number_format = '0.0'
    hc.alignment = Alignment(horizontal='center', wrap_text=True)
    ws['I4'].value = '(dùng để tính % turnover)'
    ws['I4'].font = _font(size=8, color='888888', italic=True)
    ws['I4'].alignment = Alignment(wrap_text=True)

    # ---- 3 KPI ----
    _build_kpi(ws, 'B', 'Tổng nhân viên nghỉ việc', kpi['total'], '0', 'người')
    _build_kpi(ws, 'D', 'Tỷ lệ turnover trung bình', kpi['turnover'] / 100.0, '0.0%', 'số nghỉ / NS bình quân')
    _build_kpi(ws, 'F', 'Thâm niên TB khi nghỉ', kpi['tenure'], '0.0', 'năm')

    # ---- Bảng trend + 2 bảng lý do/level ----
    trend_ref = _build_trend_table(ws, trend)
    reason_ref = _build_count_table(ws, 'B', 20, 'Số nghỉ việc theo Lý do',
                                    'Lý do', data['reasons'], 'name')
    level_ref = _build_count_table(ws, 'F', 20, 'Số nghỉ việc theo Level',
                                   'Level', data['levels'], 'label', label_colspan=2)

    # ---- Chart ----
    _add_report_charts(ws, trend, trend_ref, reason_ref, level_ref)


def _build_kpi(ws, col_left, label, value, num_fmt, sub):
    """1 ô KPI: nhãn (hàng 6), giá trị lớn (hàng 7-8), chú thích (hàng 9).
    col_left = 'B'/'D'/'F', ghép 2 cột (B:C, D:E, F:G)."""
    col_right = chr(ord(col_left) + 1)
    ws.merge_cells('%s6:%s6' % (col_left, col_right))
    _hdr_cell(ws, '%s6' % col_left, label).font = _font(bold=True, size=9, color='FFFFFF')

    ws.merge_cells('%s7:%s8' % (col_left, col_right))
    v = ws['%s7' % col_left]
    v.value = value
    v.font = _font(bold=True, size=20, color=COLOR_PRIMARY)
    v.fill = PatternFill('solid', fgColor=COLOR_SOFT)
    v.number_format = num_fmt
    v.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

    ws.merge_cells('%s9:%s9' % (col_left, col_right))
    s = ws['%s9' % col_left]
    s.value = sub
    s.font = _font(size=8, color='888888')
    s.alignment = Alignment(horizontal='center', wrap_text=True)


def _build_trend_table(ws, trend):
    """Bảng số nghỉ theo kỳ, bắt đầu B11. Trả về dict range cho chart."""
    ws['B11'].value = trend['title']
    ws['B11'].font = _font(bold=True, size=12, color=COLOR_PRIMARY)
    ws['B11'].alignment = Alignment(wrap_text=True)

    # Header hàng 12
    for coord, val in [('B12', 'Kỳ'), ('C12', 'Nhân viên tự nguyện nghỉ'),
                       ('D12', 'Công ty cho nghỉ'), ('E12', 'Tổng')]:
        _hdr_cell(ws, coord, val)

    rows = trend['rows']
    start = 13
    for i, r in enumerate(rows):
        row = start + i
        lbl = ws.cell(row=row, column=2, value=r['label'])
        lbl.font = _font(size=10)
        lbl.alignment = Alignment(wrap_text=True)
        for col, key in [(3, 'vol'), (4, 'lay')]:
            c = ws.cell(row=row, column=col, value=r[key])
            c.font = _font(size=10)
            c.alignment = Alignment(horizontal='center', wrap_text=True)
        tot = ws.cell(row=row, column=5, value=r['vol'] + r['lay'])
        tot.font = _font(size=10)
        tot.alignment = Alignment(horizontal='center', wrap_text=True)

    # Dòng tổng
    total_row = start + len(rows)
    soft = PatternFill('solid', fgColor=COLOR_SOFT)
    total_lbl = ws.cell(row=total_row, column=2, value='Tổng')
    total_lbl.alignment = Alignment(wrap_text=True)
    for col in range(2, 6):
        c = ws.cell(row=total_row, column=col)
        if col >= 3:
            c.value = sum(r['vol'] if col == 3 else r['lay'] if col == 4
                          else r['vol'] + r['lay'] for r in rows)
            c.alignment = Alignment(horizontal='center', wrap_text=True)
        c.font = _font(bold=True, size=10)
        c.fill = soft

    return {'header_row': 12, 'first': start, 'last': start + len(rows) - 1}


def _build_count_table(ws, col_left, top_row, title, label_head, items, key, label_colspan=1):
    """Bảng đếm (Lý do/Level): cột nhãn / số lượng / tỷ lệ.
    col_left = 'B' hoặc 'F'. label_colspan > 1 thì merge ô nhãn.
    Trả về dict range cho chart."""
    c0 = ord(col_left) - ord('A') + 1   # index cột nhãn (1-based)
    c1 = c0 + label_colspan              # cột số lượng
    c2 = c1 + 1                          # cột tỷ lệ

    def _merge_label(row):
        if label_colspan > 1:
            ws.merge_cells(start_row=row, start_column=c0,
                           end_row=row, end_column=c0 + label_colspan - 1)

    _merge_label(top_row)
    title_cell = ws.cell(row=top_row, column=c0, value=title)
    title_cell.font = _font(bold=True, size=12, color=COLOR_PRIMARY)
    title_cell.alignment = Alignment(wrap_text=True)
    hdr_row = top_row + 1
    _merge_label(hdr_row)
    _hdr_cell(ws, '%s%s' % (get_column_letter(c0), hdr_row), label_head)
    _hdr_cell(ws, '%s%s' % (get_column_letter(c1), hdr_row), 'Số lượng')
    _hdr_cell(ws, '%s%s' % (get_column_letter(c2), hdr_row), 'Tỷ lệ')

    total = sum(it['count'] for it in items) or 0
    first = hdr_row + 1
    for i, it in enumerate(items):
        row = first + i
        _merge_label(row)
        lbl = ws.cell(row=row, column=c0, value=it[key])
        lbl.font = _font(size=9)
        lbl.alignment = Alignment(wrap_text=True)
        cc = ws.cell(row=row, column=c1, value=it['count'])
        cc.font = _font(size=10)
        cc.alignment = Alignment(horizontal='center', wrap_text=True)
        pct = ws.cell(row=row, column=c2, value=(it['count'] / total) if total else 0)
        pct.font = _font(size=10)
        pct.number_format = '0%'
        pct.alignment = Alignment(horizontal='center', wrap_text=True)

    last = first + len(items) - 1 if items else hdr_row
    # Dòng tổng
    total_row = last + 1
    soft = PatternFill('solid', fgColor=COLOR_SOFT)
    _merge_label(total_row)
    tl = ws.cell(row=total_row, column=c0, value='Tổng')
    tl.font = _font(bold=True, size=10)
    tl.alignment = Alignment(wrap_text=True)
    ws.cell(row=total_row, column=c0).fill = soft
    tc = ws.cell(row=total_row, column=c1, value=total)
    tc.font = _font(bold=True, size=10)
    tc.fill = soft
    tc.alignment = Alignment(horizontal='center', wrap_text=True)
    pc = ws.cell(row=total_row, column=c2, value=1 if total else 0)
    pc.font = _font(bold=True, size=10)
    pc.fill = soft
    pc.number_format = '0%'
    pc.alignment = Alignment(horizontal='center', wrap_text=True)

    return {'label_col': c0, 'count_col': c1, 'header_row': hdr_row,
            'first': first, 'last': last}


def _labels():
    dl = DataLabelList()
    dl.showVal = True
    dl.showSerName = False
    dl.showCatName = False
    dl.showLegendKey = False
    dl.showPercent = False
    return dl


def _add_report_charts(ws, trend, trend_ref, reason_ref, level_ref):
    # ---- Chart 1: trend (cột chồng) ----
    c1 = BarChart()
    c1.type = 'col'
    c1.grouping = 'stacked'
    c1.overlap = 100
    c1.gapWidth = 150
    c1.title = trend['title']
    c1.height = 9
    c1.width = 22
    # C12:D<last>: 2 series (vol, lay), header ở hàng 12
    data = Reference(ws, min_col=3, max_col=4,
                     min_row=trend_ref['header_row'], max_row=trend_ref['last'])
    cats = Reference(ws, min_col=2, min_row=trend_ref['first'], max_row=trend_ref['last'])
    c1.add_data(data, titles_from_data=True)
    c1.set_categories(cats)
    c1.dataLabels = _labels()
    ws.add_chart(c1, 'A31')

    # ---- Chart 2: lý do (thanh ngang) ----
    c2 = BarChart()
    c2.type = 'bar'
    c2.grouping = 'clustered'
    c2.gapWidth = 150
    c2.title = 'Nghỉ việc theo Lý do'
    c2.legend = None
    c2.height = 8
    c2.width = 22
    data = Reference(ws, min_col=reason_ref['count_col'],
                     min_row=reason_ref['header_row'], max_row=reason_ref['last'])
    cats = Reference(ws, min_col=reason_ref['label_col'],
                     min_row=reason_ref['first'], max_row=reason_ref['last'])
    c2.add_data(data, titles_from_data=True)
    c2.set_categories(cats)
    c2.dataLabels = _labels()
    ws.add_chart(c2, 'B52')

    # ---- Chart 3: level (thanh ngang) ----
    c3 = BarChart()
    c3.type = 'bar'
    c3.grouping = 'clustered'
    c3.gapWidth = 150
    c3.title = 'Nghỉ việc theo Level'
    c3.legend = None
    c3.height = 8
    c3.width = 22
    data = Reference(ws, min_col=level_ref['count_col'],
                     min_row=level_ref['header_row'], max_row=level_ref['last'])
    cats = Reference(ws, min_col=level_ref['label_col'],
                     min_row=level_ref['first'], max_row=level_ref['last'])
    c3.add_data(data, titles_from_data=True)
    c3.set_categories(cats)
    c3.dataLabels = _labels()
    ws.add_chart(c3, 'B70')


# ======================================================================
# Sheet "Danh mục"
# ======================================================================
def _build_category_sheet(wb, categories):
    ws = wb.create_sheet('Danh mục')
    for col, w in {'A': 18, 'B': 14, 'C': 26, 'D': 55}.items():
        ws.column_dimensions[col].width = w

    headers = ['Phòng ban', 'Level', 'Loại nghỉ', 'Lý do nghỉ']
    for i, h in enumerate(headers, start=1):
        _hdr_cell(ws, '%s1' % get_column_letter(i), h)

    columns = [
        categories.get('departments', []),
        categories.get('levels', []),
        categories.get('offboarding_types', []),
        categories.get('reasons', []),
    ]
    for col_idx, values in enumerate(columns, start=1):
        for row_idx, val in enumerate(values, start=2):
            c = ws.cell(row=row_idx, column=col_idx, value=val)
            c.font = _font(size=10)
            c.alignment = Alignment(wrap_text=True)
