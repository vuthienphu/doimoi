# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class DcgContract(models.Model):
    _inherit = 'dcg.contract'

    project_count = fields.Integer(compute='_compute_project_count')
    primary_project_id = fields.Many2one(
        'dcg.project.delivery', string='Primary Project', copy=False,
    )
    project_created = fields.Boolean(string='Project Created', copy=False)

    def _compute_project_count(self):
        Project = self.env['dcg.project.delivery']
        for rec in self:
            rec.project_count = Project.search_count(
                [('contract_id', '=', rec.id)]
            ) if rec.id else 0

    def action_create_project(self):
        """Tạo dcg.project.delivery từ contract, map contract lines → project scope."""
        self.ensure_one()
        if self.state not in ('approved', 'active', 'in_progress'):
            raise UserError(_(
                "Contract must be approved, active, or in progress to create a project."
            ))

        vals = {
            'name': self.name,
            'contract_id': self.id,
            'partner_id': self.partner_id.id,
            'lead_id': self.lead_id.id if self.lead_id else False,
            'quotation_id': self.quotation_id.id if self.quotation_id else False,
            'estimate_id': self.estimate_id.id if self.estimate_id else False,
            'currency_id': self.currency_id.id,
            'company_id': self.company_id.id,
            'project_manager_id': self.project_manager_id.id if self.project_manager_id else False,
            'delivery_owner_id': self.delivery_owner_id.id if self.delivery_owner_id else False,
            'presales_owner_id': self.presales_owner_id.id if self.presales_owner_id else False,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'contract_amount_total': self.amount_total,
            'expected_cost': self.expected_cost,
            'expected_margin': self.expected_margin,
            'scope_summary': self.scope_summary,
            'handover_note': self.handover_note,
        }
        project = self.env['dcg.project.delivery'].create(vals)

        # Map contract lines → project scope
        Scope = self.env['dcg.project.scope']
        for cline in self.line_ids:
            Scope.create({
                'project_id': project.id,
                'contract_line_id': cline.id,
                'estimate_line_id': cline.estimate_line_id.id if cline.estimate_line_id else False,
                'lead_scope_id': cline.scope_id.id if cline.scope_id else False,
                'name': cline.name,
                'service_catalog_id': cline.service_catalog_id.id if cline.service_catalog_id else False,
                'ba_hours': cline.ba_hours,
                'dev_hours': cline.dev_hours,
                'test_hours': cline.test_hours,
                'pm_hours': cline.pm_hours,
                'support_hours': cline.support_hours,
                'planned_start_date': cline.planned_start_date,
                'planned_end_date': cline.planned_end_date,
            })

        self.write({
            'project_created': True,
            'primary_project_id': project.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'dcg.project.delivery',
            'res_id': project.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_projects(self):
        self.ensure_one()
        projects = self.env['dcg.project.delivery'].search(
            [('contract_id', '=', self.id)]
        )
        if len(projects) == 1:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'dcg.project.delivery',
                'res_id': projects.id,
                'view_mode': 'form',
                'target': 'current',
            }
        return {
            'type': 'ir.actions.act_window',
            'name': _('Delivery Projects'),
            'res_model': 'dcg.project.delivery',
            'view_mode': 'list,form',
            'domain': [('contract_id', '=', self.id)],
        }
