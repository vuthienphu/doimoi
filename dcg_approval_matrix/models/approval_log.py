# -*- coding: utf-8 -*-
from odoo import fields, models


ACTION_SELECTION = [
    ('submit', 'Submit'),
    ('approve', 'Approve'),
    ('reject', 'Reject'),
    ('cancel', 'Cancel'),
]


class DcgApprovalLog(models.Model):
    """Audit trail của approval request."""
    _name = 'dcg.approval.log'
    _description = 'Approval Log'
    _order = 'id'

    request_id = fields.Many2one(
        'dcg.approval.request',
        string='Request',
        required=True,
        ondelete='cascade',
        index=True,
    )
    sequence = fields.Integer(string='Order')
    step_no = fields.Integer(string='Step No.')
    matrix_line_id = fields.Many2one(
        'dcg.approval.matrix.line',
        string='Matrix Line',
        ondelete='set null',
    )
    request_step_id = fields.Many2one(
        'dcg.approval.request.step',
        string='Request Step',
        ondelete='set null',
    )
    approver_id = fields.Many2one('res.users', string='Performed By')
    action = fields.Selection(
        selection=ACTION_SELECTION,
        string='Action',
        required=True,
    )
    action_date = fields.Datetime(
        string='Action Date',
        required=True,
        default=fields.Datetime.now,
    )
    from_state = fields.Char(string='From State')
    to_state = fields.Char(string='To State')
    note = fields.Text(string='Note / Reason')
