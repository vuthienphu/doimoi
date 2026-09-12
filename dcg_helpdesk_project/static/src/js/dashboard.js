/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

export class CustomerRequestDashboard extends Component {
    static template = "dcg_helpdesk_project.CustomerRequestDashboardTemplate";

    setup() {
        this.action = useService("action");

        const today = new Date();
        const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);

        this.state = useState({
            filters: {
                datePreset: "this_month",
                dateFrom: firstDay.toISOString().split("T")[0],
                dateTo: today.toISOString().split("T")[0],
                partnerId: "",
                projectId: "",
                teamId: "",
                userId: "",
                requestSource: "",
                stageId: "",
            },
            filterOptions: {
                partners: [],
                projects: [],
                teams: [],
                users: [],
                stages: [],
                request_sources: [],
            },
            data: {
                kpi: {
                    total: 0,
                    new: 0,
                    processing: 0,
                    waiting: 0,
                    urgent: 0,
                    without_task: 0,
                },
                by_stage: [],
                by_source: [],
                by_priority: [],
                by_user: [],
                task_stats: {
                    total_tasks: 0,
                    tickets_with_task: 0,
                    tickets_without_task: 0,
                    completed_tasks: 0,
                },
                attention_tickets: [],
            },
            loading: true,
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        this.state.loading = true;
        try {
            const params = {
                date_preset: this.state.filters.datePreset,
                date_from: this.state.filters.dateFrom,
                date_to: this.state.filters.dateTo,
                partner_id: this.state.filters.partnerId ? parseInt(this.state.filters.partnerId) : false,
                project_id: this.state.filters.projectId ? parseInt(this.state.filters.projectId) : false,
                team_id: this.state.filters.teamId ? parseInt(this.state.filters.teamId) : false,
                user_id: this.state.filters.userId === 'unassigned' ? 'unassigned' : (this.state.filters.userId ? parseInt(this.state.filters.userId) : false),
                request_source: this.state.filters.requestSource || false,
                stage_id: this.state.filters.stageId ? parseInt(this.state.filters.stageId) : false,
            };

            const res = await rpc("/helpdesk/dashboard/data", params);
            if (res) {
                if (res.filter_options) {
                    this.state.filterOptions = res.filter_options;
                }
                this.state.data = res;
            }
        } catch (error) {
            console.error("Failed to load helpdesk dashboard data", error);
        } finally {
            this.state.loading = false;
        }
    }

    onPresetChange(ev) {
        const val = ev.target.value;
        this.state.filters.datePreset = val;
        const today = new Date();

        if (val === "today") {
            const isoStr = today.toISOString().split("T")[0];
            this.state.filters.dateFrom = isoStr;
            this.state.filters.dateTo = isoStr;
        } else if (val === "7days") {
            const past7 = new Date(today);
            past7.setDate(today.getDate() - 6);
            this.state.filters.dateFrom = past7.toISOString().split("T")[0];
            this.state.filters.dateTo = today.toISOString().split("T")[0];
        } else if (val === "30days") {
            const past30 = new Date(today);
            past30.setDate(today.getDate() - 29);
            this.state.filters.dateFrom = past30.toISOString().split("T")[0];
            this.state.filters.dateTo = today.toISOString().split("T")[0];
        } else if (val === "this_month") {
            const first = new Date(today.getFullYear(), today.getMonth(), 1);
            const last = new Date(today.getFullYear(), today.getMonth() + 1, 0);
            this.state.filters.dateFrom = first.toISOString().split("T")[0];
            this.state.filters.dateTo = last.toISOString().split("T")[0];
        } else if (val === "last_month") {
            const first = new Date(today.getFullYear(), today.getMonth() - 1, 1);
            const last = new Date(today.getFullYear(), today.getMonth(), 0);
            this.state.filters.dateFrom = first.toISOString().split("T")[0];
            this.state.filters.dateTo = last.toISOString().split("T")[0];
        } else if (val === "this_quarter") {
            const currentQuarter = Math.floor(today.getMonth() / 3);
            const first = new Date(today.getFullYear(), currentQuarter * 3, 1);
            const last = new Date(today.getFullYear(), (currentQuarter + 1) * 3, 0);
            this.state.filters.dateFrom = first.toISOString().split("T")[0];
            this.state.filters.dateTo = last.toISOString().split("T")[0];
        } else if (val === "this_year") {
            const first = new Date(today.getFullYear(), 0, 1);
            const last = new Date(today.getFullYear(), 11, 31);
            this.state.filters.dateFrom = first.toISOString().split("T")[0];
            this.state.filters.dateTo = last.toISOString().split("T")[0];
        }

        this.loadData();
    }

    async onFilterChange() {
        await this.loadData();
    }

    async onFilterReset() {
        const today = new Date();
        const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
        this.state.filters = {
            datePreset: "this_month",
            dateFrom: firstDay.toISOString().split("T")[0],
            dateTo: today.toISOString().split("T")[0],
            partnerId: "",
            projectId: "",
            teamId: "",
            userId: "",
            requestSource: "",
            stageId: "",
        };
        await this.loadData();
    }

    buildCurrentDomain() {
        const domain = [];
        if (this.state.filters.dateFrom) {
            domain.push(["create_date", ">=", `${this.state.filters.dateFrom} 00:00:00`]);
        }
        if (this.state.filters.dateTo) {
            domain.push(["create_date", "<=", `${this.state.filters.dateTo} 23:59:59`]);
        }
        if (this.state.filters.partnerId) {
            domain.push(["partner_id", "=", parseInt(this.state.filters.partnerId)]);
        }
        if (this.state.filters.projectId) {
            domain.push(["project_id", "=", parseInt(this.state.filters.projectId)]);
        }
        if (this.state.filters.teamId) {
            domain.push(["team_id", "=", parseInt(this.state.filters.teamId)]);
        }
        if (this.state.filters.userId) {
            if (this.state.filters.userId === "unassigned") {
                domain.push(["user_id", "=", false]);
            } else {
                domain.push(["user_id", "=", parseInt(this.state.filters.userId)]);
            }
        }
        if (this.state.filters.requestSource) {
            domain.push(["request_source", "=", this.state.filters.requestSource]);
        }
        if (this.state.filters.stageId) {
            domain.push(["stage_id", "=", parseInt(this.state.filters.stageId)]);
        }
        return domain;
    }

    openTicketList(extraDomain = [], title = "Danh sách Ticket") {
        const fullDomain = [...this.buildCurrentDomain(), ...extraDomain];
        this.action.doAction({
            name: title,
            type: "ir.actions.act_window",
            res_model: "helpdesk.ticket",
            view_mode: "list,kanban,form",
            views: [
                [false, "list"],
                [false, "kanban"],
                [false, "form"],
            ],
            domain: fullDomain,
        });
    }

    openTicketForm(ticketId) {
        this.action.doAction({
            name: "Chi tiết Ticket",
            type: "ir.actions.act_window",
            res_model: "helpdesk.ticket",
            res_id: ticketId,
            view_mode: "form",
            views: [[false, "form"]],
        });
    }
}

registry.category("actions").add("helpdesk_customer_request_dashboard", CustomerRequestDashboard);

