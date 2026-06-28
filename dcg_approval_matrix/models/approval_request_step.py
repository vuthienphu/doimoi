# -*- coding: utf-8 -*-
from odoo import fields, models


STEP_STATE_SELECTION = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('cancelled', 'Cancelled'),
]


class DcgApprovalRequestStep(models.Model):
    """Snapshot runtime của các step trong 1 approval request.

    Khi submit, engine snapshot matrix lines áp dụng thành các step.
    Request hoạt động dựa trên step này — không phụ thuộc matrix nữa.
    """
    _name = 'dcg.approval.request.step'
    _description = 'Approval Request Step'
    _order = 'request_id, sequence, id'

    request_id = fields.Many2one(
        'dcg.approval.request',
        string='Request',
        required=True,
        ondelete='cascade',
        index=True,
    )
    sequence = fields.Integer(string='Step No.', required=True, default=10)
    matrix_line_id = fields.Many2one(
        'dcg.approval.matrix.line',
        string='Matrix Line',
        ondelete='set null',
    )
    name = fields.Char(string='Step Name', translate=True)

    # Snapshot
    approver_type = fields.Selection(
        selection=[
            ('specific_user', 'Specific User'),
            ('group', 'Group'),
            ('employee_manager', 'Employee Manager'),
        ],
        string='Approver Type',
    )
    approver_user_ids = fields.Many2many(
        'res.users',
        'dcg_approval_request_step_user_rel',
        'step_id',
        'user_id',
        string='Candidate Approvers',
    )
    min_amount = fields.Float(string='Min Amount')
    max_amount = fields.Float(string='Max Amount')

    # Result
    state = fields.Selection(
        selection=STEP_STATE_SELECTION,
        string='Status',
        required=True,
        default='pending',
    )
    approved_by = fields.Many2one('res.users', string='Approved By')
    approved_date = fields.Datetime(string='Approved Date')
    rejected_by = fields.Many2one('res.users', string='Rejected By')
    rejected_date = fields.Datetime(string='Rejected Date')
    note = fields.Text(string='Note')
