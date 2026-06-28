/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { KpiCard } from "./widgets/kpi_card";

// ============================================================
// Base Dashboard — all dashboards inherit this
// ============================================================
class BaseDashboard extends Component {
    static components = { KpiCard };
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({ data: null, loading: true });
        onWillStart(() => this.loadData());
    }
    async loadData() {
        this.state.loading = true;
        try { this.state.data = await this._fetch(); }
        catch(e) { console.error("Dashboard error:", e); this.state.data = {}; }
        this.state.loading = false;
    }
    async _fetch() { return {}; }
    async refresh() { await this.loadData(); }
    fmtNum(v) {
        if (typeof v !== "number") return v || "0";
        if (Math.abs(v) >= 1e9) return (v/1e9).toFixed(1)+"B";
        if (Math.abs(v) >= 1e6) return (v/1e6).toFixed(1)+"M";
        if (Math.abs(v) >= 1e3) return (v/1e3).toFixed(0)+"K";
        return v.toLocaleString();
    }
    openRec(model, id) {
        this.action.doAction({ type:"ir.actions.act_window", res_model:model, res_id:id, views:[[false,"form"]], target:"current" });
    }
    drill(model, domain) {
        this.action.doAction({ type:"ir.actions.act_window", res_model:model, views:[[false,"list"],[false,"form"]], domain, target:"current" });
    }
    nav(tag) { this.action.doAction({ type:"ir.actions.client", tag }); }
    quickAction(model) {
        this.action.doAction({ type:"ir.actions.act_window", res_model:model, views:[[false,"form"]], target:"current" });
    }
}

// ============================================================
// Home
// ============================================================
export class HomeDashboard extends BaseDashboard {
    static template = "dcg_dashboard_kpi.HomeDashboard";
    setup() {
        super.setup();
        this.state.exec = null;
        this.state.notif = null;
    }
    async loadData() {
        this.state.loading = true;
        try {
            this.state.exec = await this.orm.call("dcg.dashboard.service","get_executive_data",[]);
            this.state.notif = await this.orm.call("dcg.dashboard.service","get_notifications",[]);
        } catch(e) { console.error(e); }
        this.state.loading = false;
    }
}

// ============================================================
// Executive
// ============================================================
export class ExecutiveDashboard extends BaseDashboard {
    static template = "dcg_dashboard_kpi.ExecutiveDashboard";
    async _fetch() { return this.orm.call("dcg.dashboard.service","get_executive_data",[]); }
}

// ============================================================
// Sales
// ============================================================
export class SalesDashboard extends BaseDashboard {
    static template = "dcg_dashboard_kpi.SalesDashboard";
    async _fetch() { return this.orm.call("dcg.dashboard.service","get_sales_data",[]); }
}

// ============================================================
// Project
// ============================================================
export class ProjectDashboard extends BaseDashboard {
    static template = "dcg_dashboard_kpi.ProjectDashboard";
    async _fetch() { return this.orm.call("dcg.dashboard.service","get_project_data",[]); }
}

// ============================================================
// Resource
// ============================================================
export class ResourceDashboard extends BaseDashboard {
    static template = "dcg_dashboard_kpi.ResourceDashboard";
    async _fetch() { return this.orm.call("dcg.dashboard.service","get_resource_data",[]); }
}

// ============================================================
// Finance
// ============================================================
export class FinanceDashboard extends BaseDashboard {
    static template = "dcg_dashboard_kpi.FinanceDashboard";
    async _fetch() { return this.orm.call("dcg.dashboard.service","get_finance_data",[]); }
}

// ============================================================
// Support
// ============================================================
export class SupportDashboard extends BaseDashboard {
    static template = "dcg_dashboard_kpi.SupportDashboard";
    async _fetch() { return this.orm.call("dcg.dashboard.service","get_support_data",[]); }
}

// ============================================================
// Asset
// ============================================================
export class AssetDashboard extends BaseDashboard {
    static template = "dcg_dashboard_kpi.AssetDashboard";
    async _fetch() { return this.orm.call("dcg.dashboard.service","get_asset_data",[]); }
}

// ============================================================
// Project Tasks (New)
// ============================================================
export class ProjectTaskDashboard extends BaseDashboard {
    static template = "dcg_dashboard_kpi.ProjectTaskDashboard";

    setup() {
        super.setup();
        this.state.projectId = null;
        this.state.projectFilter = "all";
        this.state.taskTypeFilter = "all";
        this.state.taskStatusFilter = "all";
    }

    async _fetch() {
        return this.orm.call("dcg.dashboard.service", "get_project_task_data", [], {
            project_id: this.state.projectId
        });
    }

    async selectProject(projectId) {
        this.state.projectId = projectId ? parseInt(projectId) : null;
        this.state.taskTypeFilter = "all";
        this.state.taskStatusFilter = "all";
        await this.loadData();
    }

    async selectProjectFromRow(projectId) {
        this.state.projectId = projectId;
        this.state.projectFilter = projectId.toString();
        await this.loadData();
    }

    async resetProject() {
        this.state.projectId = null;
        this.state.projectFilter = "all";
        await this.loadData();
    }

    setTaskTypeFilter(type) {
        this.state.taskTypeFilter = type;
    }

    setTaskStatusFilter(status) {
        this.state.taskStatusFilter = status;
    }

    getFilteredTasks() {
        if (!this.state.data || !this.state.data.tasks) return [];
        let tasks = this.state.data.tasks;
        if (this.state.taskTypeFilter !== "all") {
            tasks = tasks.filter(t => t.task_type === this.state.taskTypeFilter);
        }
        if (this.state.taskStatusFilter !== "all") {
            if (this.state.taskStatusFilter === "todo") {
                tasks = tasks.filter(t => t.is_start);
            } else if (this.state.taskStatusFilter === "in_progress") {
                tasks = tasks.filter(t => t.is_in_progress);
            } else if (this.state.taskStatusFilter === "in_review") {
                tasks = tasks.filter(t => t.is_review);
            } else if (this.state.taskStatusFilter === "done") {
                tasks = tasks.filter(t => t.is_done);
            }
        }
        return tasks;
    }
}

// ============================================================
// Register all with action registry
// ============================================================
const actions = registry.category("actions");
actions.add("dcg_dashboard_home", HomeDashboard);
actions.add("dcg_dashboard_executive", ExecutiveDashboard);
actions.add("dcg_dashboard_sales", SalesDashboard);
actions.add("dcg_dashboard_project", ProjectDashboard);
actions.add("dcg_dashboard_project_task", ProjectTaskDashboard);
actions.add("dcg_dashboard_resource", ResourceDashboard);
actions.add("dcg_dashboard_finance", FinanceDashboard);
actions.add("dcg_dashboard_support", SupportDashboard);
actions.add("dcg_dashboard_asset", AssetDashboard);
