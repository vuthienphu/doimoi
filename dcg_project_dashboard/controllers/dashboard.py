# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

from ..services.project_dashboard_service import ProjectDashboardService


class ProjectDashboardController(http.Controller):

    def _service(self):
        return ProjectDashboardService(request.env)

    @http.route('/dashboard/options', type='jsonrpc', auth='user')
    def dashboard_options(self, **filters):
        return self._service().get_options(filters)

    @http.route('/dashboard/summary', type='jsonrpc', auth='user')
    def dashboard_summary(self, **filters):
        return self._service().get_summary(filters)

    @http.route('/dashboard/project', type='jsonrpc', auth='user')
    def dashboard_project(self, **filters):
        return self._service().get_projects(filters)

    @http.route('/dashboard/task_stage', type='jsonrpc', auth='user')
    def dashboard_task_stage(self, **filters):
        return self._service().get_task_stage(filters)

    @http.route('/dashboard/task_trend', type='jsonrpc', auth='user')
    def dashboard_task_trend(self, **filters):
        return self._service().get_task_trend(filters)

    @http.route('/dashboard/workload', type='jsonrpc', auth='user')
    def dashboard_workload(self, **filters):
        return self._service().get_workload(filters)

    @http.route('/dashboard/project_progress', type='jsonrpc', auth='user')
    def dashboard_project_progress(self, **filters):
        return self._service().get_project_progress(filters)

    @http.route('/dashboard/overdue', type='jsonrpc', auth='user')
    def dashboard_overdue(self, **filters):
        return self._service().get_overdue(filters)

    @http.route('/dashboard/testing', type='jsonrpc', auth='user')
    def dashboard_testing(self, **filters):
        return self._service().get_testing(filters)

    @http.route('/dashboard/not_live', type='jsonrpc', auth='user')
    def dashboard_not_live(self, **filters):
        return self._service().get_not_live(filters)

    @http.route('/dashboard/upcoming', type='jsonrpc', auth='user')
    def dashboard_upcoming(self, **filters):
        return self._service().get_upcoming(filters)
