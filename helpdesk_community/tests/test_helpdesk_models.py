from odoo.tests import common, tagged
from odoo import fields


@tagged('-at_install', 'post_install')
class TestHelpdeskModels(common.TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Stage = cls.env['helpdesk.stage']
        cls.Team = cls.env['helpdesk.team']
        cls.Category = cls.env['helpdesk.category']
        cls.Ticket = cls.env['helpdesk.ticket']

        # Create default stages
        cls.stage_new = cls.Stage.create({
            'name': 'New', 'sequence': 10, 'is_start': True})
        cls.stage_ip = cls.Stage.create({
            'name': 'In Progress', 'sequence': 20})
        cls.stage_done = cls.Stage.create({
            'name': 'Closed', 'sequence': 30, 'is_done': True, 'fold': True})

        # Create team
        cls.team = cls.Team.create({
            'name': 'Support',
            'member_ids': [(6, 0, [cls.env.user.id])],
        })

        # Create category
        cls.category = cls.Category.create({
            'name': 'Bug Report',
            'team_id': cls.team.id,
            'color': 1,
        })

    def test_01_create_ticket(self):
        ticket = self.Ticket.create({
            'name': 'Test ticket subject',
        })
        self.assertTrue(ticket.ticket_number)
        self.assertTrue(ticket.ticket_number.startswith('HD'))
        self.assertTrue(ticket.stage_id.is_start)
        self.assertTrue(ticket.stage_change_date)

    def test_02_ticket_workflow(self):
        ticket = self.Ticket.create({
            'name': 'Workflow test',
        })
        ticket.write({'stage_id': self.stage_ip.id})
        self.assertEqual(ticket.stage_id, self.stage_ip)
        self.assertFalse(ticket.close_date)

        ticket.write({'stage_id': self.stage_done.id})
        self.assertTrue(ticket.close_date)
        self.assertTrue(ticket.stage_change_date)

    def test_03_ticket_priority(self):
        ticket = self.Ticket.create({
            'name': 'Priority test',
            'priority': 'urgent',
        })
        self.assertEqual(ticket.priority, 'urgent')

    def test_04_ticket_assign(self):
        ticket = self.Ticket.create({
            'name': 'Assign test',
            'team_id': self.team.id,
            'user_id': self.env.user.id,
        })
        self.assertEqual(ticket.team_id, self.team)
        self.assertEqual(ticket.user_id, self.env.user)

    def test_05_ticket_category(self):
        ticket = self.Ticket.create({
            'name': 'Category test',
            'category_id': self.category.id,
        })
        self.assertEqual(ticket.category_id, self.category)

    def test_06_start_stage_default(self):
        ticket = self.Ticket.create({
            'name': 'Default stage test',
        })
        self.assertTrue(ticket.stage_id.is_start)

    def test_07_stage_creation(self):
        stage = self.Stage.create({
            'name': 'Test Stage',
            'sequence': 50,
            'is_start': False,
            'is_done': True,
        })
        self.assertEqual(stage.name, 'Test Stage')
        self.assertTrue(stage.is_done)

    def test_08_team_creation(self):
        team = self.Team.create({
            'name': 'Test Team',
            'assignment_policy': 'round_robin',
        })
        self.assertEqual(team.assignment_policy, 'round_robin')

    def test_09_category_creation(self):
        category = self.Category.create({
            'name': 'Test Category',
            'team_id': self.team.id,
            'sequence': 5,
        })
        self.assertEqual(category.sequence, 5)

    def test_10_ticket_archive(self):
        ticket = self.Ticket.create({
            'name': 'Archive test',
        })
        self.assertTrue(ticket.active)
        ticket.action_archive()
        self.assertFalse(ticket.active)

    def test_11_ticket_unlink(self):
        ticket = self.Ticket.create({
            'name': 'Delete test',
        })
        tid = ticket.id
        ticket.unlink()
        self.assertFalse(self.Ticket.search([('id', '=', tid)]))

    def test_12_read_group_stage_ids(self):
        # Call the callback directly using the golden (18.0/19.0) 2-arg
        # signature. The Compatibility Layer (R-ORM-002) appends `order`
        # when backporting to <= 17.0, so it also rewrites this call.
        stages = self.Ticket._read_group_stage_ids(self.Stage, [])
        self.assertIn(self.stage_new, stages)
        self.assertIn(self.stage_ip, stages)

    def test_13_group_expand_orm_path(self):
        # Regression for R-ORM-002 golden bug: exercise group_expand through
        # the real ORM grouping path so a wrong callback signature raises here
        # on ANY series (read_group is portable across 14-19). Empty stages
        # must still appear because group_expand returns every stage.
        self.Ticket.create({
            'name': 'Group expand regression',
            'stage_id': self.stage_new.id,
        })
        groups = self.Ticket.read_group([], [], ['stage_id'])
        grouped_ids = [g['stage_id'][0] for g in groups if g.get('stage_id')]
        self.assertIn(self.stage_ip.id, grouped_ids)
        self.assertIn(self.stage_done.id, grouped_ids)

    def test_14_security_groups_resolve(self):
        # Regression for F-001: view/menu groups= must reference resolvable
        # fully-qualified xml ids, otherwise button/menu visibility is dropped.
        for xmlid in (
            'helpdesk_community.group_helpdesk_user',
            'helpdesk_community.group_helpdesk_team_leader',
            'helpdesk_community.group_helpdesk_manager',
        ):
            self.assertTrue(
                self.env.ref(xmlid, raise_if_not_found=False),
                'Missing security group %s' % xmlid,
            )
