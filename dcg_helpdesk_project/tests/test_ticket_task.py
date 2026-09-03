from odoo.tests import tagged
from .common import HelpdeskProjectSyncCommon


@tagged('post_install', '-at_install')
class TestTicketTaskWorkflow(HelpdeskProjectSyncCommon):

    def test_07_create_task_button_visible_condition(self):
        """Test 7: Ticket with partner_id AND project_id allows task creation."""
        ticket = self.env['helpdesk.ticket'].create({
            'name': 'Ticket 1',
            'team_id': self.helpdesk_team.id,
            'partner_id': self.partner_company_a.id,
            'project_id': self.project_a.id,
        })
        wizard_action = ticket.action_create_task_wizard()
        self.assertEqual(wizard_action.get('res_model'), 'helpdesk.ticket.create.task.wizard')

    def test_08_create_task_button_hidden_no_partner(self):
        """Test 8: Ticket without partner_id returns warning on create task."""
        ticket = self.env['helpdesk.ticket'].create({
            'name': 'Ticket No Partner',
            'team_id': self.helpdesk_team.id,
            'project_id': self.project_a.id,
        })
        action = ticket.action_create_task_wizard()
        self.assertEqual(action.get('type'), 'ir.actions.client')
        self.assertEqual(action.get('tag'), 'display_notification')

    def test_09_create_task_button_hidden_no_project(self):
        """Test 9: Ticket without project_id returns warning on create task."""
        ticket = self.env['helpdesk.ticket'].create({
            'name': 'Ticket No Project',
            'team_id': self.helpdesk_team.id,
            'partner_id': self.partner_company_a.id,
        })
        action = ticket.action_create_task_wizard()
        self.assertEqual(action.get('type'), 'ir.actions.client')
        self.assertEqual(action.get('tag'), 'display_notification')

    def test_10_project_domain_filter(self):
        """Test 10: Project field domain filters projects matching ticket partner_id."""
        ticket = self.env['helpdesk.ticket'].create({
            'name': 'Domain Test Ticket',
            'partner_id': self.partner_company_a.id,
        })
        projects_for_a = self.env['project.project'].search([('partner_id', '=', ticket.partner_id.id)])
        self.assertIn(self.project_a, projects_for_a)
        self.assertNotIn(self.project_b, projects_for_a)

    def test_11_wizard_create_task_success(self):
        """Test 11: Task creation wizard creates project.task successfully."""
        ticket = self.env['helpdesk.ticket'].create({
            'name': 'Wizard Ticket',
            'team_id': self.helpdesk_team.id,
            'partner_id': self.partner_company_a.id,
            'project_id': self.project_a.id,
            'description': 'Ticket Description Text',
        })
        wizard = self.env['helpdesk.ticket.create.task.wizard'].with_context(default_ticket_id=ticket.id).create({
            'ticket_id': ticket.id,
            'project_id': self.project_a.id,
            'task_name': 'New Task Name',
            'description': 'Task Description Text',
        })
        wizard.action_create_task()

        task = self.env['project.task'].search([('helpdesk_ticket_id', '=', ticket.id)], limit=1)
        self.assertTrue(task.exists())
        self.assertEqual(task.name, 'New Task Name')

    def test_12_task_linked_to_ticket(self):
        """Test 12: Created task has correct helpdesk_ticket_id reference."""
        ticket = self.env['helpdesk.ticket'].create({
            'name': 'Linked Ticket',
            'team_id': self.helpdesk_team.id,
        })
        task = self.env['project.task'].create({
            'name': 'Linked Task',
            'project_id': self.project_a.id,
            'helpdesk_ticket_id': ticket.id,
        })
        self.assertEqual(task.helpdesk_ticket_id, ticket)

    def test_13_smart_button_task_count(self):
        """Test 13: Ticket task_count reflects number of linked tasks."""
        ticket = self.env['helpdesk.ticket'].create({
            'name': 'Multi Task Ticket',
            'team_id': self.helpdesk_team.id,
        })
        self.assertEqual(ticket.task_count, 0)

        self.env['project.task'].create({
            'name': 'Sub Task 1',
            'project_id': self.project_a.id,
            'helpdesk_ticket_id': ticket.id,
        })
        self.env['project.task'].create({
            'name': 'Sub Task 2',
            'project_id': self.project_a.id,
            'helpdesk_ticket_id': ticket.id,
        })

        ticket.invalidate_recordset(['task_count'])
        self.assertEqual(ticket.task_count, 2)

    def test_14_smart_button_opens_task_list(self):
        """Test 14: Smart button action_open_ticket_tasks returns list view act_window."""
        ticket = self.env['helpdesk.ticket'].create({
            'name': 'Action Ticket',
            'team_id': self.helpdesk_team.id,
        })
        task = self.env['project.task'].create({
            'name': 'Task Single',
            'project_id': self.project_a.id,
            'helpdesk_ticket_id': ticket.id,
        })
        action = ticket.action_open_ticket_tasks()
        self.assertEqual(action.get('res_model'), 'project.task')
        self.assertEqual(action.get('view_mode'), 'list,form')
        self.assertEqual(action.get('domain'), [('id', 'in', [task.id])])

    def test_15_ticket_remains_in_progress(self):
        """Test 15: Ticket with 2 tasks remains in progress if 1 task is Done and 1 is In Progress."""
        ticket = self.env['helpdesk.ticket'].create({
            'name': 'Progress Ticket',
            'team_id': self.helpdesk_team.id,
            'stage_id': self.stage_in_progress.id,
        })
        task1 = self.env['project.task'].create({
            'name': 'Task 1',
            'project_id': self.project_a.id,
            'helpdesk_ticket_id': ticket.id,
            'stage_id': self.task_stage_done.id,
        })
        task2 = self.env['project.task'].create({
            'name': 'Task 2',
            'project_id': self.project_a.id,
            'helpdesk_ticket_id': ticket.id,
            'stage_id': self.task_stage_todo.id,
        })

        self.assertNotEqual(ticket.stage_id, self.stage_done, "Ticket should not be done while task2 is todo")

    def test_16_ticket_auto_done_when_all_tasks_done(self):
        """Test 16: Ticket automatically moves to Done stage when ALL linked tasks are Done."""
        ticket = self.env['helpdesk.ticket'].create({
            'name': 'Auto Done Ticket',
            'team_id': self.helpdesk_team.id,
            'stage_id': self.stage_in_progress.id,
        })
        task1 = self.env['project.task'].create({
            'name': 'Task 1',
            'project_id': self.project_a.id,
            'helpdesk_ticket_id': ticket.id,
            'stage_id': self.task_stage_todo.id,
        })
        task2 = self.env['project.task'].create({
            'name': 'Task 2',
            'project_id': self.project_a.id,
            'helpdesk_ticket_id': ticket.id,
            'stage_id': self.task_stage_todo.id,
        })

        # Complete task1
        task1.write({'stage_id': self.task_stage_done.id})
        self.assertNotEqual(ticket.stage_id, self.stage_done)

        # Complete task2
        task2.write({'stage_id': self.task_stage_done.id})
        self.assertEqual(ticket.stage_id, self.stage_done, "Ticket should automatically transition to Done stage")

    def test_17_unrelated_task_no_impact(self):
        """Test 17: Completing an unrelated task has no effect on tickets."""
        ticket = self.env['helpdesk.ticket'].create({
            'name': 'Unrelated Ticket',
            'team_id': self.helpdesk_team.id,
            'stage_id': self.stage_in_progress.id,
        })
        unrelated_task = self.env['project.task'].create({
            'name': 'Independent Task',
            'project_id': self.project_a.id,
            'stage_id': self.task_stage_todo.id,
        })
        unrelated_task.write({'stage_id': self.task_stage_done.id})
        self.assertEqual(ticket.stage_id, self.stage_in_progress)
