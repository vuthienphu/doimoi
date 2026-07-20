/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

export class DcgProjectDashboard extends Component {
    static template = "dcg_project_dashboard.ProjectDashboard";

    setup() {
        this.periods = [
            ["today", "Hôm nay"],
            ["yesterday", "Hôm qua"],
            ["7_days", "7 ngày"],
            ["30_days", "30 ngày"],
            ["this_week", "Tuần này"],
            ["this_month", "Tháng này"],
            ["this_quarter", "Quý này"],
            ["this_year", "Năm nay"],
        ];
        this.statsBasis = [
            ["project_create", "Ngày tạo Project"],
            ["task_create", "Ngày tạo Task"],
            ["deadline", "Deadline"],
            ["completed", "Ngày hoàn thành"],
            ["live", "Ngày đưa Live"],
        ];
        this.standardStageNames = [
            "Cần làm",
            "Đang làm",
            "Chuyển test",
            "Hoàn thành",
            "Đã đưa lên Live",
        ];
        this.state = useState({
            loading: true,
            filters: {
                period: "30_days",
                stats_basis: "task_create",
                date_from: "",
                date_to: "",
                project_ids: [],
                partner_ids: [],
                pm_ids: [],
                user_ids: [],
                stage_ids: [],
            },
            options: { projects: [], partners: [], users: [], stages: [] },
            filterSearch: {
                project_ids: "",
                partner_ids: "",
                pm_ids: "",
                user_ids: "",
                stage_ids: "",
            },
            openFilter: "",
            summary: {},
            stage: [],
            trend: [],
            workload: [],
            progress: [],
            overdue: [],
            testing: [],
            notLive: [],
            upcoming: [],
            sort: {
                progress: { field: "deadline", dir: "asc" },
                workload: { field: "total", dir: "desc" },
            },
        });
        onWillStart(() => this.loadDashboard());
    }

    async loadDashboard() {
        this.state.loading = true;
        const filters = JSON.parse(JSON.stringify(this.state.filters));
        const [options, summary, stage, trend, workload, progress, overdue, testing, notLive, upcoming] =
            await Promise.all([
                rpc("/dashboard/options", filters),
                rpc("/dashboard/summary", filters),
                rpc("/dashboard/task_stage", filters),
                rpc("/dashboard/task_trend", filters),
                rpc("/dashboard/workload", filters),
                rpc("/dashboard/project_progress", filters),
                rpc("/dashboard/overdue", filters),
                rpc("/dashboard/testing", filters),
                rpc("/dashboard/not_live", filters),
                rpc("/dashboard/upcoming", filters),
            ]);
        Object.assign(this.state, {
            options: {
                ...options,
                stages: this.standardStages(options.stages),
            },
            summary,
            stage: this.standardStages(stage),
            trend,
            workload,
            progress: this.normalizeProgress(progress),
            overdue,
            testing,
            notLive,
            upcoming,
            loading: false,
        });
    }

    onFilterChange(ev) {
        this.state.filters[ev.target.name] = ev.target.value;
        if (ev.target.name === "period") {
            this.state.filters.date_from = "";
            this.state.filters.date_to = "";
        }
        this.loadDashboard();
    }

    onDateChange(ev) {
        this.state.filters[ev.target.name] = ev.target.value;
        this.loadDashboard();
    }

    onMultiChange(ev) {
        this.state.filters[ev.target.name] = Array.from(ev.target.selectedOptions).map((option) =>
            Number(option.value)
        );
        this.loadDashboard();
    }

    onTagSelect(ev) {
        const name = ev.target.name;
        const id = Number(ev.target.value);
        if (id && !this.state.filters[name].includes(id)) {
            this.state.filters[name] = [...this.state.filters[name], id];
            this.loadDashboard();
        }
        ev.target.value = "";
    }

    onTagSearch(name, ev) {
        this.state.openFilter = name;
        this.state.filterSearch[name] = ev.target.value;
    }

    toggleTag(name, id) {
        this.state.openFilter = name;
        const selected = new Set(this.state.filters[name] || []);
        if (selected.has(id)) {
            selected.delete(id);
        } else {
            selected.add(id);
        }
        this.state.filters[name] = [...selected];
        this.loadDashboard();
    }

    toggleFilter(name) {
        this.state.openFilter = this.state.openFilter === name ? "" : name;
    }

    removeTag(name, id) {
        this.state.filters[name] = this.state.filters[name].filter((item) => item !== id);
        this.loadDashboard();
    }

    clearTagFilter(name) {
        this.state.filters[name] = [];
        this.loadDashboard();
    }

    selectedItems(name, items) {
        const selected = new Set(this.state.filters[name] || []);
        return (items || []).filter((item) => selected.has(item.id));
    }

    availableItems(name, items) {
        const selected = new Set(this.state.filters[name] || []);
        return (items || []).filter((item) => !selected.has(item.id));
    }

    filteredTagItems(name, items) {
        const query = (this.state.filterSearch[name] || "").trim().toLowerCase();
        if (!query) {
            return items || [];
        }
        return (items || []).filter((item) => (item.name || "").toLowerCase().includes(query));
    }

    filterSummary(name, items) {
        const selected = this.selectedItems(name, items);
        if (!selected.length) {
            return "Tất cả";
        }
        if (selected.length === 1) {
            return selected[0].name;
        }
        return `${selected.length} đã chọn`;
    }

    firstInitial(value) {
        const name = (value || "").trim();
        return name ? name[0].toUpperCase() : "?";
    }

    firstName(value) {
        return (value || "").split(",")[0].trim();
    }

    progressTone(value) {
        const percent = Number(value) || 0;
        if (percent >= 80) {
            return "danger";
        }
        if (percent >= 60) {
            return "warning";
        }
        return "normal";
    }

    riskBadgeClass(variant, days) {
        if (variant === "overdue" || Number(days) > 0) {
            return "danger";
        }
        if (variant === "upcoming") {
            return "warning";
        }
        return "neutral";
    }

    setSort(scope, field) {
        const current = this.state.sort[scope] || {};
        this.state.sort[scope] = {
            field,
            dir: current.field === field && current.dir === "asc" ? "desc" : "asc",
        };
    }

    sortIcon(scope, field) {
        const current = this.state.sort[scope] || {};
        if (current.field !== field) {
            return "fa fa-sort";
        }
        return current.dir === "asc" ? "fa fa-sort-asc" : "fa fa-sort-desc";
    }

    sortedProgress() {
        return this.sortedRows(this.state.progress, "progress");
    }

    sortedWorkload() {
        return this.sortedRows(this.state.workload, "workload");
    }

    sortedRows(rows, scope) {
        const sort = this.state.sort[scope] || {};
        const direction = sort.dir === "desc" ? -1 : 1;
        return [...(rows || [])].sort((left, right) => {
            const a = this.sortValue(left, sort.field);
            const b = this.sortValue(right, sort.field);
            if (a < b) {
                return -1 * direction;
            }
            if (a > b) {
                return 1 * direction;
            }
            return 0;
        });
    }

    sortValue(row, field) {
        if (!field) {
            return "";
        }
        if (field === "done_ratio") {
            return Number(row.done_tasks || 0) / Math.max(Number(row.total_tasks || 0), 1);
        }
        if (field === "deadline") {
            return row.deadline || "9999-12-31";
        }
        const value = row[field];
        if (typeof value === "number") {
            return value;
        }
        return String(value || "").toLowerCase();
    }

    stageColor(index) {
        return ["#3b82f6", "#f59e0b", "#8b5cf6", "#10b981", "#06b6d4", "#94a3b8"][index % 6];
    }

    stageTone(index) {
        return ["blue", "amber", "violet", "green", "cyan", "slate"][index % 6];
    }

    standardStages(items) {
        const byName = new Map((items || []).map((item) => [item.name, item]));
        return this.standardStageNames.map((name) => ({
            id: byName.get(name)?.id || name,
            name,
            count: byName.get(name)?.count || 0,
            percent: byName.get(name)?.percent || 0,
        }));
    }

    normalizeProgress(projects) {
        return (projects || []).map((project) => ({
            ...project,
            stage_counts: this.standardStages(project.stage_counts),
        }));
    }

    donutSegments() {
        let offset = 25;
        return this.state.stage.map((item, index) => {
            const percent = item.percent || 0;
            const segment = {
                id: item.id || item.name,
                color: this.stageColor(index),
                dasharray: `${percent} ${100 - percent}`,
                dashoffset: -offset,
            };
            offset += percent;
            return segment;
        });
    }

    maxTrendValue() {
        const values = this.state.trend.flatMap((item) => [item.created, item.done, item.overdue]);
        return Math.max(...values, 1);
    }

    barHeight(value) {
        return `${Math.max(4, (value / this.maxTrendValue()) * 100)}%`;
    }

    trendPoints(field) {
        const max = this.maxTrendValue();
        const count = Math.max(this.state.trend.length - 1, 1);
        return this.state.trend.map((item, index) => {
            const x = 32 + (index / count) * 536;
            const y = 188 - ((item[field] || 0) / max) * 148;
            return `${x.toFixed(1)},${y.toFixed(1)}`;
        }).join(" ");
    }

    trendLastLabel() {
        const item = this.state.trend[this.state.trend.length - 1];
        return item ? item.date : "";
    }
}

registry.category("actions").add("dcg_project_dashboard.project_dashboard", DcgProjectDashboard);
