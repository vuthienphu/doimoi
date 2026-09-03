/** @odoo-module **/

import { Component, onWillStart, onMounted, onWillUnmount, useState, useRef, useEffect } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { loadBundle } from "@web/core/assets";
import { _t } from "@web/core/l10n/translation";

const MODEL = "inom.offboarding.request";
// Thống kê theo ngày nghỉ việc thực tế (Date, không lệch múi giờ).
const DATE_FIELD = "last_day";
const TYPE_VOL = "voluntarily";
const TYPE_LAY = "layoff";
const COLOR_VOL = "#6f4a63";
const COLOR_LAY = "#dcc7d5";

// Plugin vẽ số bên trong mỗi bar.
const valueLabelPlugin = {
    id: "ofbValueLabels",
    afterDatasetsDraw(chart) {
        const { ctx } = chart;
        ctx.save();
        ctx.font = "600 12px sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        chart.data.datasets.forEach((dataset, di) => {
            const meta = chart.getDatasetMeta(di);
            if (meta.hidden) {
                return;
            }
            meta.data.forEach((bar, i) => {
                const value = dataset.data[i];
                if (!value) {
                    return;
                }
                // Số đặt ở GIỮA mỗi bar, theo đúng x của bar đó nên không đè nhau.
                // Bar tối -> chữ trắng; bar sáng -> chữ đậm.
                ctx.fillStyle = di === 0 ? "#ffffff" : "#4a2f42";
                ctx.fillText(String(value), bar.x, (bar.y + bar.base) / 2);
            });
        });
        ctx.restore();
    },
};

export class OffboardingDashboard extends Component {
    static template = "inom_employee_offboarding.OffboardingDashboard";

    setup() {
        this.orm = useService("orm");
        const currentYear = new Date().getFullYear();
        // Năm: từ 2026 đến năm hiện tại.
        const years = [];
        for (let y = 2026; y <= currentYear; y++) {
            years.push(y);
        }
        if (!years.length) {
            years.push(currentYear);
        }

        this.state = useState({
            filters: {
                department_ids: [], // rỗng = Tất cả
                mode: "year", // year | quarter | month
                year: currentYear,
                quarter: false,
                month: false,
            },
            deptOpen: false,
            departments: [],
            years,
            months: Array.from({ length: 12 }, (_, i) => i + 1),
            quarters: [1, 2, 3, 4],
            loading: true,
            kpi: { total: 0, turnover: 0, tenure: 0 },
            trendTitle: "",
            trendData: [],
            trendEmpty: false,
            reasonData: [],
            levelData: [],
            deptRows: [],
            _version: 0,
        });

        this.trendCanvas = useRef("trendCanvas");
        this._charts = {};

        onWillStart(async () => {
            await loadBundle("web.chartjs_lib");
            await this._loadDepartments();
            await this._load();
        });

        // Đóng dropdown phòng ban khi click ra ngoài.
        this._onDocClick = () => {
            if (this.state.deptOpen) {
                this.state.deptOpen = false;
            }
        };
        onMounted(() => document.addEventListener("click", this._onDocClick));
        onWillUnmount(() => document.removeEventListener("click", this._onDocClick));

        useEffect(
            () => {
                this._renderCharts();
                return () => this._destroyCharts();
            },
            () => [this.state._version]
        );
    }

    // -----------------------------------------------------------------
    // Helpers ngày tháng
    // -----------------------------------------------------------------
    _pad(n) {
        return String(n).padStart(2, "0");
    }
    _ym(year, month) {
        return `${year}-${this._pad(month)}-01`;
    }
    _ymd(year, month, day) {
        return `${year}-${this._pad(month)}-${this._pad(day)}`;
    }
    _dayAfter(year, month, day) {
        const dt = new Date(year, month - 1, day + 1);
        return `${dt.getFullYear()}-${this._pad(dt.getMonth() + 1)}-${this._pad(dt.getDate())}`;
    }
    _monthEnd(year, month) {
        // Đầu tháng kế tiếp (exclusive).
        return month === 12 ? this._ym(year + 1, 1) : this._ym(year, month + 1);
    }

    /** Chia tháng thành các tuần (Thứ 2 - CN), kẹp trong phạm vi tháng. */
    _weekBuckets(year, month) {
        const buckets = [];
        const daysInMonth = new Date(year, month, 0).getDate();
        let d = 1;
        while (d <= daysInMonth) {
            const dow = (new Date(year, month - 1, d).getDay() + 6) % 7; // Mon=0..Sun=6
            const endDay = Math.min(d + (6 - dow), daysInMonth);
            buckets.push({ startDay: d, endDay });
            d = endDay + 1;
        }
        return buckets;
    }

    // -----------------------------------------------------------------
    // Nạp dữ liệu
    // -----------------------------------------------------------------
    async _loadDepartments() {
        this.state.departments = await this.orm.searchRead(
            "hr.department", [], ["id", "name"], { order: "name" }
        );
    }

    _granularity() {
        const f = this.state.filters;
        if (f.mode === "month" && f.month) {
            return "month";
        }
        if (f.mode === "quarter" && f.quarter) {
            return "quarter";
        }
        return "year";
    }

    /** Danh sách bucket + tiêu đề cho chart xu hướng, tùy filter. */
    _trendBuckets() {
        const f = this.state.filters;
        const year = f.year;
        const gran = this._granularity();

        if (gran === "month") {
            return {
                title: _t("Số nghỉ việc theo tháng"),
                buckets: this._weekBuckets(year, f.month).map((w) => ({
                    label: `Tuần ${w.startDay}-${w.endDay}/${f.month}`,
                    start: this._ymd(year, f.month, w.startDay),
                    end: this._dayAfter(year, f.month, w.endDay),
                })),
            };
        }
        if (gran === "quarter") {
            const startMonth = (f.quarter - 1) * 3 + 1;
            return {
                title: _t("Số nghỉ việc theo quý"),
                buckets: [0, 1, 2].map((i) => {
                    const m = startMonth + i;
                    return {
                        label: `Tháng ${m}`,
                        start: this._ym(year, m),
                        end: this._monthEnd(year, m),
                    };
                }),
            };
        }
        // year
        return {
            title: _t("Số nghỉ việc theo năm"),
            buckets: this.state.quarters.map((q) => {
                const sm = (q - 1) * 3 + 1;
                const em = sm + 3;
                return {
                    label: `Quý ${q}`,
                    start: this._ym(year, sm),
                    end: em > 12 ? this._ym(year + 1, em - 12) : this._ym(year, em),
                };
            }),
        };
    }

    _deptFilterDomain() {
        const ids = this.state.filters.department_ids;
        return ids.length ? [["department_id", "in", ids]] : [];
    }

    /** Ngày đầu/cuối kỳ (inclusive) theo filter, cho tính turnover. */
    _period() {
        const f = this.state.filters;
        if (f.month) {
            const lastDay = new Date(f.year, f.month, 0).getDate();
            return { start: this._ym(f.year, f.month), end: this._ymd(f.year, f.month, lastDay) };
        }
        if (f.quarter) {
            const sm = (f.quarter - 1) * 3 + 1;
            const em = sm + 2; // tháng cuối của quý
            const lastDay = new Date(f.year, em, 0).getDate();
            return { start: this._ym(f.year, sm), end: this._ymd(f.year, em, lastDay) };
        }
        return { start: this._ym(f.year, 1), end: this._ymd(f.year, 12, 31) };
    }

    /** Domain đầy đủ (phòng ban + năm + quý + tháng) cho KPI/lý do/bảng. */
    _fullDomain() {
        const f = this.state.filters;
        const d = [...this._deptFilterDomain()];
        if (!f.year) {
            return d;
        }
        if (f.month) {
            d.push([DATE_FIELD, ">=", this._ym(f.year, f.month)]);
            d.push([DATE_FIELD, "<", this._monthEnd(f.year, f.month)]);
        } else if (f.quarter) {
            const sm = (f.quarter - 1) * 3 + 1;
            const em = sm + 3;
            d.push([DATE_FIELD, ">=", this._ym(f.year, sm)]);
            d.push([DATE_FIELD, "<", em > 12 ? this._ym(f.year + 1, em - 12) : this._ym(f.year, em)]);
        } else {
            d.push([DATE_FIELD, ">=", this._ym(f.year, 1)]);
            d.push([DATE_FIELD, "<", this._ym(f.year + 1, 1)]);
        }
        return d;
    }

    async _countByType(domain) {
        const [vol, lay] = await Promise.all([
            this.orm.searchCount(MODEL, [...domain, ["offboarding_type", "=", TYPE_VOL]]),
            this.orm.searchCount(MODEL, [...domain, ["offboarding_type", "=", TYPE_LAY]]),
        ]);
        return { vol, lay };
    }

    async _load() {
        this.state.loading = true;
        const depDom = this._deptFilterDomain();
        const fullDom = this._fullDomain();

        // Chart xu hướng (drill-down theo filter).
        const { title, buckets } = this._trendBuckets();
        const trendProm = Promise.all(
            buckets.map(async (b) => {
                const domain = [...depDom, [DATE_FIELD, ">=", b.start], [DATE_FIELD, "<", b.end]];
                return { label: b.label, ...(await this._countByType(domain)) };
            })
        );

        const totalProm = this.orm.searchCount(MODEL, fullDom);
        const reasonProm = this.orm.formattedReadGroup(MODEL, fullDom, ["reason_id"], ["__count"]);
        const levelProm = this.orm.formattedReadGroup(MODEL, fullDom, ["level_id"], ["__count"]);
        // Thâm niên TB + turnover + bảng phòng ban tính ở server (sudo) vì cần
        // đọc dữ liệu hợp đồng/nhân viên mà user thường không có quyền.
        const { start, end } = this._period();
        const deptIds = this.state.filters.department_ids;
        const tenureProm = this.orm.call(MODEL, "get_dashboard_avg_tenure", [fullDom]);
        const turnoverProm = this.orm.call(MODEL, "get_dashboard_turnover", [deptIds, start, end]);
        const deptProm = this.orm.call(MODEL, "get_dashboard_department_rows", [fullDom, start, end]);

        const [trendData, total, reasonGroups, levelGroups, tenure, turnover, deptRows] =
            await Promise.all([
                trendProm, totalProm, reasonProm, levelProm, tenureProm, turnoverProm, deptProm,
            ]);

        this.state.trendTitle = title;
        this.state.trendData = trendData;
        this.state.trendEmpty = trendData.every((r) => !r.vol && !r.lay);
        // turnover & tenure: số (float) hoặc false.
        this.state.kpi = { total, turnover, tenure };

        const reasonTotal = reasonGroups.reduce((s, g) => s + g.__count, 0) || 1;
        this.state.reasonData = reasonGroups
            .map((g) => ({
                name: g.reason_id ? g.reason_id[1] : _t("Không xác định"),
                count: g.__count,
                pct: Math.round((g.__count / reasonTotal) * 100),
            }))
            .sort((a, b) => b.count - a.count);

        const levelTotal = levelGroups.reduce((s, g) => s + g.__count, 0) || 1;
        this.state.levelData = levelGroups
            .map((g) => ({
                label: g.level_id ? g.level_id[1] : _t("Không xác định"),
                count: g.__count,
                pct: Math.round((g.__count / levelTotal) * 100),
            }))
            .sort((a, b) => b.count - a.count);

        this.state.deptRows = deptRows.map((r) => ({
            name: r.name,
            headcount: r.headcount,
            leavers: r.leavers,
            turnover: r.turnover, // % (float) hoặc false
            tenure: r.tenure, // số năm (float) hoặc false
            topReasons: r.top_reasons,
        }));

        this.state.loading = false;
        this.state._version++;
    }

    // -----------------------------------------------------------------
    // Chart.js
    // -----------------------------------------------------------------
    _destroyCharts() {
        for (const key of Object.keys(this._charts)) {
            this._charts[key].destroy();
            delete this._charts[key];
        }
    }

    _renderCharts() {
        this._destroyCharts();
        if (!window.Chart || !this.trendCanvas.el) {
            return;
        }
        const rows = this.state.trendData;
        this._charts.trend = new window.Chart(this.trendCanvas.el, {
            type: "bar",
            data: {
                labels: rows.map((r) => r.label),
                datasets: [
                    { label: _t("Nhân viên tự nguyện nghỉ"), data: rows.map((r) => r.vol), backgroundColor: COLOR_VOL, borderRadius: 4 },
                    { label: _t("Công ty cho nghỉ"), data: rows.map((r) => r.lay), backgroundColor: COLOR_LAY, borderColor: "#b98fa8", borderWidth: 1, borderRadius: 4 },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: "top", align: "start" } },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: {
                            // Dòng dưới nhãn: tổng 2 bar của mỗi nhóm.
                            callback: (value, index) => {
                                const row = rows[index];
                                const label = row ? row.label : "";
                                const total = row ? row.vol + row.lay : 0;
                                return [label, `Tổng: ${total}`];
                            },
                        },
                    },
                    y: { beginAtZero: true, ticks: { precision: 0 } },
                },
            },
            plugins: [valueLabelPlugin],
        });
    }

    // -----------------------------------------------------------------
    // Filter
    // -----------------------------------------------------------------
    // Định dạng số năm thâm niên: 3.8 -> "3,8" (dấu phẩy). "" nếu không có.
    fmtYears(value) {
        if (typeof value !== "number") {
            return "";
        }
        return value.toFixed(1).replace(".", ",");
    }

    // Headcount trung bình: số nguyên nếu tròn, ngược lại 1 chữ số thập phân.
    fmtHeadcount(value) {
        if (typeof value !== "number") {
            return value;
        }
        return Number.isInteger(value)
            ? String(value)
            : value.toFixed(1).replace(".", ",");
    }

    // -----------------------------------------------------------------
    // Filter phòng ban (chọn nhiều)
    // -----------------------------------------------------------------
    toggleDeptDropdown() {
        this.state.deptOpen = !this.state.deptOpen;
    }

    /** Tên các phòng ban đang chọn (theo thứ tự danh sách). */
    selectedDeptNames() {
        const ids = this.state.filters.department_ids;
        return this.state.departments
            .filter((d) => ids.includes(d.id))
            .map((d) => d.name);
    }

    /** Đổi chế độ thời gian: year | quarter | month. Reset filter con không dùng. */
    onModeChange(mode) {
        const f = this.state.filters;
        if (f.mode === mode) {
            return;
        }
        f.mode = mode;
        if (mode !== "quarter") {
            f.quarter = false;
        }
        if (mode !== "month") {
            f.month = false;
        }
        this._load();
    }

    onDeptAll() {
        this.state.filters.department_ids = [];
        this._load();
    }

    onDeptToggle(depId) {
        const ids = this.state.filters.department_ids;
        const idx = ids.indexOf(depId);
        if (idx >= 0) {
            ids.splice(idx, 1);
        } else {
            ids.push(depId);
        }
        this._load();
    }

    onFilterChange(key, ev) {
        const raw = ev.target.value;
        const value = raw === "" ? false : Number(raw);
        this.state.filters[key] = value;
        // Quý và tháng loại trừ nhau: chọn cái này thì xóa cái kia.
        if (key === "month" && value) {
            this.state.filters.quarter = false;
        } else if (key === "quarter" && value) {
            this.state.filters.month = false;
        }
        this._load();
    }

    exportExcel() {
        const f = this.state.filters;
        const domain = this._fullDomain();
        const params = new URLSearchParams({
            domain: JSON.stringify(domain),
            mode: f.mode,
            year: f.year || "",
            quarter: f.quarter || "",
            month: f.month || "",
        });
        window.location.href = `/offboarding/export/xlsx?${params.toString()}`;
    }
}

registry.category("actions").add("offboarding_dashboard", OffboardingDashboard);
