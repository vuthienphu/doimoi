/** @odoo-module **/
import { Component } from "@odoo/owl";

export class KpiCard extends Component {
    static template = "dcg_dashboard_kpi.KpiCard";
    static props = {
        label: String,
        value: { type: [Number, String], optional: true },
        prefix: { type: String, optional: true },
        suffix: { type: String, optional: true },
        sub: { type: String, optional: true },
        color: { type: String, optional: true },
        onClick: { type: Function, optional: true },
    };

    formatValue(val) {
        if (typeof val !== "number") return val || "0";
        if (Math.abs(val) >= 1e9) return (val / 1e9).toFixed(1) + "B";
        if (Math.abs(val) >= 1e6) return (val / 1e6).toFixed(1) + "M";
        if (Math.abs(val) >= 1e3) return (val / 1e3).toFixed(1) + "K";
        return val.toLocaleString();
    }
}

export class DashboardTable extends Component {
    static template = "dcg_dashboard_kpi.DashboardTable";
    static props = {
        title: String,
        columns: Array,
        rows: Array,
        onRowClick: { type: Function, optional: true },
    };
}
