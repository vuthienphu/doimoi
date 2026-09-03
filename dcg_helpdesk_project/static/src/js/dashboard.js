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
            dateFrom: firstDay.toISOString().split('T')[0],
            dateTo: today.toISOString().split('T')[0],
            data: {
                total: 0,
                with_task: 0,
                without_task: 0,
                in_progress: 0,
                done: 0,
                by_source: { web: 0, zalo: 0, internal: 0, other: 0 },
                by_stage: {},
                recent_tickets: [],
            },
            loading: false,
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        this.state.loading = true;
        try {
            const res = await rpc("/dcg_helpdesk_project/dashboard_data", {
                date_from: this.state.dateFrom,
                date_to: this.state.dateTo,
            });
            if (res) {
                this.state.data = res;
            }
        } catch (error) {
            console.error("Failed to load dashboard data", error);
        } finally {
            this.state.loading = false;
        }
    }

    async onFilterSubmit(ev) {
        ev.preventDefault();
        await this.loadData();
    }

    openTicketList(domain, title) {
        const fullDomain = [];
        if (this.state.dateFrom) {
            fullDomain.push(['create_date', '>=', `${this.state.dateFrom} 00:00:00`]);
        }
        if (this.state.dateTo) {
            fullDomain.push(['create_date', '<=', `${this.state.dateTo} 23:59:59`]);
        }
        if (domain) {
            fullDomain.push(...domain);
        }

        this.action.doAction({
            name: title || "Helpdesk Tickets",
            type: "ir.actions.act_window",
            res_model: "helpdesk.ticket",
            view_mode: "list,form",
            views: [[false, "list"], [false, "form"]],
            domain: fullDomain,
        });
    }

    openTicketForm(ticketId) {
        this.action.doAction({
            name: "Ticket Details",
            type: "ir.actions.act_window",
            res_model: "helpdesk.ticket",
            res_id: ticketId,
            view_mode: "form",
            views: [[false, "form"]],
        });
    }
}

registry.category("actions").add("helpdesk_customer_request_dashboard", CustomerRequestDashboard);
