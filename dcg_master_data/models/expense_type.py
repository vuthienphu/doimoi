# -*- coding: utf-8 -*-
from odoo import fields, models


class DcgExpenseType(models.Model):
    _name = 'dcg.expense.type'
    _description = 'Expense Type'
    _order = 'sequence, code, name'

    name = fields.Char(
        string='Expense Type',
        required=True,
        translate=True,
    )
    code = fields.Char(
        string='Code',
        index=True,
    )
    expense_group = fields.Selection(
        selection=[
            ('travel', 'Travel'),
            ('accommodation', 'Accommodation'),
            ('meal', 'Meal'),
            ('transport', 'Transport'),
            ('customer_care', 'Customer Care'),
            ('license', 'License'),
            ('subcontractor', 'Subcontractor'),
            ('office', 'Office'),
            ('other', 'Other'),
        ],
        string='Expense Group',
        default='other',
    )
    is_billable = fields.Boolean(
        string='Billable',
        default=False,
        help='Indicates whether this expense type can be re-billed to the customer.',
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    note = fields.Text(string='Internal Note', translate=True)

    _sql_constraints = [
        (
            'code_uniq',
            'unique(code)',
            'Expense Type code must be unique.',
        ),
    ]
