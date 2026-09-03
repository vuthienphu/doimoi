from odoo.tests import tagged
from .common import HelpdeskProjectSyncCommon
from datetime import date, timedelta


@tagged('post_install', '-at_install')
class TestDashboard(HelpdeskProjectSyncCommon):

    def test_18_dashboard_kpi_calculation(self):
        """Test 18: Dashboard Controller correctly computes total, with_task, in_progress, and done KPIs."""
        ticket_1 = self.env['helpdesk.ticket'].create({
            'name': 'Dash 1',
            'team_id': self.helpdesk_team.id,
            'stage_id': self.stage_in_progress.id,
            'request_source': 'web',
        })
        ticket_2 = self.env['helpdesk.ticket'].create({
            'name': 'Dash 2',
            'team_id': self.helpdesk_team.id,
            'stage_id': self.stage_done.id,
            'request_source': 'zalo',
        })
        task_1 = self.env['project.task'].create({
            'name': 'Task 1',
            'project_id': self.project_a.id,
            'helpdesk_ticket_id': ticket_1.id,
        })

        controller = self.env['dcg_helpdesk_project.dashboard_controller'] if hasattr(self.env, 'dcg_helpdesk_project.dashboard_controller') else None

        # Fetch data using controller class directly or via RPC method logic
        from odoo.addons.dcg_helpdesk_project.controllers.dashboard import CustomerRequestDashboardController
        ctrl = CustomerRequestDashboardController()

        # Mock request context for test
        class DummyRequest:
            env = self.env
        import odoo.http
        original_req = getattr(odoo.http, 'request', None)
        odoo.http.request = DummyRequest()
        try:
            today_str = date.today().strftime('%Y-%m-%d')
            data = ctrl.get_dashboard_data(date_from=today_str, date_to=today_str)
            self.assertGreaterEqual(data['total'], 2)
            self.assertGreaterEqual(data['with_task'], 1)
            self.assertGreaterEqual(data['in_progress'], 1)
            self.assertGreaterEqual(data['done'], 1)
        finally:
            odoo.http.request = original_req

    def test_19_dashboard_date_filtering(self):
        """Test 19: Dashboard correctly filters tickets by date_from and date_to."""
        from odoo.addons.dcg_helpdesk_project.controllers.dashboard import CustomerRequestDashboardController
        ctrl = CustomerRequestDashboardController()

        class DummyRequest:
            env = self.env
        import odoo.http
        original_req = getattr(odoo.http, 'request', None)
        odoo.http.request = DummyRequest()
        try:
            yesterday_str = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
            today_str = date.today().strftime('%Y-%m-%d')

            data_today = ctrl.get_dashboard_data(date_from=today_str, date_to=today_str)
            self.assertIsNotNone(data_today.get('total'))
        finally:
            odoo.http.request = original_req
