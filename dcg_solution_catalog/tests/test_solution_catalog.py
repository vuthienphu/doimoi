from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestSolutionCatalog(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.solution_cat = cls.env['solution.solution'].create({
            'name': 'HRM Solution',
            'code': 'HRM',
        })
        cls.config_hr = cls.env['solution.configuration'].create({
            'name': 'HR Configuration',
            'code': 'CFG_HR',
        })

        cls.module_employee = cls.env['solution.module'].create({
            'name': 'Hồ sơ nhân viên',
            'code': 'hr_employee',
            'solution_id': cls.solution_cat.id,
            'configuration_id': cls.config_hr.id,
            'version': '19',
            'state': 'ready',
        })

        cls.tmpl_1 = cls.env['solution.module.task.template'].create({
            'module_id': cls.module_employee.id,
            'name': 'Task Mẫu 1 - Khảo sát',
            'planned_hours': 4.0,
        })
        cls.tmpl_2 = cls.env['solution.module.task.template'].create({
            'module_id': cls.module_employee.id,
            'name': 'Task Mẫu 2 - Triển khai',
            'planned_hours': 8.0,
        })

    def test_01_solution_module_and_task_templates(self):
        """Test 1: Module total_planned_hours computes sum of task templates."""
        self.assertEqual(self.module_employee.total_planned_hours, 12.0)

    def test_02_task_default_solution_inherit(self):
        """Test 2: Task created under project defaults solution_ids to project's solution_ids."""
        project = self.env['project.project'].create({
            'name': 'Dự án Test 1',
            'solution_ids': [(6, 0, [self.module_employee.id])],
        })
        task = self.env['project.task'].create({
            'name': 'Task Test',
            'project_id': project.id,
        })
        self.assertIn(self.module_employee, task.solution_ids)

    def test_03_project_solution_removed_warning_wizard(self):
        """Test 3: Removing a solution used by existing tasks returns warning wizard action."""
        module_payroll = self.env['solution.module'].create({
            'name': 'Bảng lương',
            'code': 'hr_payroll',
            'state': 'ready',
        })
        project = self.env['project.project'].create({
            'name': 'Dự án Test Warning',
            'solution_ids': [(6, 0, [self.module_employee.id, module_payroll.id])],
        })
        task = self.env['project.task'].create({
            'name': 'Task dùng Bảng lương',
            'project_id': project.id,
            'solution_ids': [(6, 0, [module_payroll.id])],
        })

        # Try removing module_payroll from project
        action = project.write({
            'solution_ids': [(6, 0, [self.module_employee.id])],
        })
        self.assertIsInstance(action, dict)
        self.assertEqual(action.get('res_model'), 'project.solution.change.warning.wizard')

    def test_04_crm_won_auto_generate_project_and_tasks(self):
        """Test 4: Winning CRM lead creates Project and generates tasks according to solution task templates."""
        lead = self.env['crm.lead'].create({
            'name': 'Cơ hội Triển khai HR ABC',
            'type': 'opportunity',
            'probability': 100,
            'solution_ids': [(6, 0, [self.module_employee.id])],
        })
        lead._dcg_create_project_for_won_opportunities()

        project = lead.project_id
        self.assertTrue(project.exists())
        self.assertIn(self.module_employee, project.solution_ids)

        # Check generated tasks
        generated_tasks = self.env['project.task'].search([('project_id', '=', project.id)])
        task_names = generated_tasks.mapped('name')
        self.assertIn('Task Mẫu 1 - Khảo sát', task_names)
        self.assertIn('Task Mẫu 2 - Triển khai', task_names)
