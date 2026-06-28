# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


APPROVER_TYPE_SELECTION = [
    ('specific_user', 'Specific User'),
    ('group', 'Group'),
    ('employee_manager', 'Employee Manager'),
]


MANAGER_LEVEL_SELECTION = [
    ('1', 'Direct Manager'),
    ('2', 'Manager Level 2'),
]


class DcgApprovalMatrixLine(models.Model):
    """Một step duyệt trong matrix."""
    _name = 'dcg.approval.matrix.line'
    _description = 'Approval Matrix Line'
    _order = 'sequence, id'

    matrix_id = fields.Many2one(
        'dcg.approval.matrix',
        string='Matrix',
        required=True,
        ondelete='cascade',
        index=True,
    )
    sequence = fields.Integer(string='Step', required=True, default=10)
    name = fields.Char(string='Step Name', translate=True)
    active = fields.Boolean(default=True)

    # Approver definition
    approver_type = fields.Selection(
        selection=APPROVER_TYPE_SELECTION,
        string='Approver Type',
        required=True,
        default='specific_user',
    )
    user_id = fields.Many2one(
        'res.users',
        string='Specific User',
        domain="[('share', '=', False)]",
        help='Used when Approver Type is Specific User.',
    )
    group_id = fields.Many2one(
        'res.groups',
        string='Group',
        help='Used when Approver Type is Group. Any active internal user in the group can approve.',
    )
    manager_level = fields.Selection(
        selection=MANAGER_LEVEL_SELECTION,
        string='Manager Level',
        default='1',
        help='Used when Approver Type is Employee Manager. Phase 1 only supports level 1.',
    )

    # Filter
    min_amount = fields.Float(
        string='Min Amount',
        help='Apply this step only if the request amount is greater than or equal to this value.',
    )
    max_amount = fields.Float(
        string='Max Amount',
        help='Apply this step only if the request amount is less than or equal to this value.',
    )
    condition_json = fields.Text(
        string='Condition (JSON)',
        help='Reserved for future advanced rules. Currently informational only.',
    )
    stop_if_rejected = fields.Boolean(
        string='Stop If Rejected',
        default=True,
        help='If checked, rejecting this step stops the whole approval. (Phase 1 always true.)',
    )

    # Related / display
    matrix_approval_type = fields.Selection(
        related='matrix_id.approval_type',
        store=True,
        string='Approval Type',
    )
    matrix_company_id = fields.Many2one(
        related='matrix_id.company_id',
        store=True,
        string='Company',
    )

    @api.constrains('min_amount', 'max_amount')
    def _check_amount_bounds(self):
        for rec in self:
            if rec.min_amount and rec.max_amount and rec.min_amount > rec.max_amount:
                raise ValidationError(_(
                    "Step '%s': Min Amount must be less than or equal to Max Amount."
                ) % (rec.name or rec.sequence))

    @api.constrains('approver_type', 'user_id', 'group_id', 'manager_level')
    def _check_approver_config(self):
        for rec in self:
            if rec.approver_type == 'specific_user' and not rec.user_id:
                raise ValidationError(_(
                    "Step '%s': Specific User must be set when Approver Type is 'Specific User'."
                ) % (rec.name or rec.sequence))
            if rec.approver_type == 'group' and not rec.group_id:
                raise ValidationError(_(
                    "Step '%s': Group must be set when Approver Type is 'Group'."
                ) % (rec.name or rec.sequence))
            if rec.approver_type == 'employee_manager' and rec.manager_level not in ('1', '2'):
                raise ValidationError(_(
                    "Step '%s': Manager Level is required for Employee Manager."
                ) % (rec.name or rec.sequence))

    # ---- Engine helpers ----
    def is_applicable_for_amount(self, amount):
        """Step có được áp dụng với amount này không?"""
        self.ensure_one()
        if self.min_amount and amount < self.min_amount:
            return False
        if self.max_amount and amount > self.max_amount:
            return False
        return True

    def resolve_approver_users(self, requester_employee=None):
        """Trả về recordset res.users là candidate approver cho line này.

        Raise ValidationError nếu không resolve được.
        """
        self.ensure_one()
        Users = self.env['res.users']

        if self.approver_type == 'specific_user':
            if not self.user_id:
                raise ValidationError(_(
                    "Step '%s' is misconfigured: Specific User is empty."
                ) % (self.name or self.sequence))
            if not self.user_id.active:
                raise ValidationError(_(
                    "Step '%(s)s': configured user '%(u)s' is inactive."
                ) % {'s': self.name or self.sequence, 'u': self.user_id.display_name})
            return self.user_id

        if self.approver_type == 'group':
            if not self.group_id:
                raise ValidationError(_(
                    "Step '%s' is misconfigured: Group is empty."
                ) % (self.name or self.sequence))
            users = self.group_id.users.filtered(
                lambda u: u.active and not u.share
            )
            if not users:
                raise ValidationError(_(
                    "Step '%(s)s': group '%(g)s' has no active internal user."
                ) % {'s': self.name or self.sequence, 'g': self.group_id.display_name})
            return users

        if self.approver_type == 'employee_manager':
            if self.manager_level != '1':
                raise ValidationError(_(
                    "Step '%s': only Manager Level 1 is supported in this version."
                ) % (self.name or self.sequence))
            if not requester_employee:
                raise ValidationError(_(
                    "Step '%s' requires an Employee Manager but the requester has no employee record."
                ) % (self.name or self.sequence))
            parent = requester_employee.parent_id
            if not parent:
                raise ValidationError(_(
                    "Step '%(s)s': employee '%(e)s' has no direct manager configured."
                ) % {'s': self.name or self.sequence, 'e': requester_employee.display_name})
            if not parent.user_id or not parent.user_id.active:
                raise ValidationError(_(
                    "Step '%(s)s': manager '%(m)s' has no active user account."
                ) % {'s': self.name or self.sequence, 'm': parent.display_name})
            return parent.user_id

        return Users.browse()
