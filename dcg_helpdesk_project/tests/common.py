from odoo.tests.common import TransactionCase


class HelpdeskProjectSyncCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner_company_a = cls.env['res.partner'].create({
            'name': 'Company A',
            'is_company': True,
        })
        cls.partner_company_b = cls.env['res.partner'].create({
            'name': 'Company B',
            'is_company': True,
        })

        cls.project_a = cls.env['project.project'].create({
            'name': 'Project A',
            'partner_id': cls.partner_company_a.id,
        })
        cls.project_b = cls.env['project.project'].create({
            'name': 'Project B',
            'partner_id': cls.partner_company_b.id,
        })

        cls.helpdesk_team = cls.env['helpdesk.team'].create({
            'name': 'Support Team',
        })

        cls.stage_new = cls.env['helpdesk.stage'].create({
            'name': 'New',
            'sequence': 1,
            'team_ids': [(4, cls.helpdesk_team.id)],
            'fold': False,
        })
        cls.stage_in_progress = cls.env['helpdesk.stage'].create({
            'name': 'In Progress',
            'sequence': 2,
            'team_ids': [(4, cls.helpdesk_team.id)],
            'fold': False,
        })
        cls.stage_done = cls.env['helpdesk.stage'].create({
            'name': 'Done',
            'sequence': 3,
            'team_ids': [(4, cls.helpdesk_team.id)],
            'fold': True,
        })

        cls.task_stage_todo = cls.env['project.task.type'].create({
            'name': 'To Do',
            'sequence': 1,
            'fold': False,
        })
        cls.task_stage_done = cls.env['project.task.type'].create({
            'name': 'Done',
            'sequence': 2,
            'fold': True,
        })
