# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


APPROVAL_TYPE_SELECTION = [
    ('deal_approval', 'Deal Approval'),
    ('trip_approval', 'Business Trip Approval'),
    ('contract_approval', 'Contract Approval'),
    ('appendix_approval', 'Contract Appendix Approval'),
    ('change_request_approval', 'Project Change Request Approval'),
    ('timesheet_approval', 'Timesheet Approval'),
    ('asset_request_approval', 'Asset Request Approval'),
]


class DcgApprovalMatrix(models.Model):
    """Template ma trận duyệt cho một loại nghiệp vụ."""
    _name = 'dcg.approval.matrix'
    _description = 'Approval Matrix'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, approval_type, name'

    # ---- Identification ----
    name = fields.Char(
        string='Matrix Name',
        required=True,
        tracking=True,
        translate=True,
    )
    code = fields.Char(string='Code', index=True, tracking=True)
    sequence = fields.Integer(
        string='Priority',
        default=10,
        help='Lower value means higher priority when multiple matrices match.',
    )
    active = fields.Boolean(default=True, tracking=True)

    # ---- Scope ----
    approval_type = fields.Selection(
        selection=APPROVAL_TYPE_SELECTION,
        string='Approval Type',
        required=True,
        tracking=True,
        index=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        tracking=True,
        help='Leave empty to apply to all companies.',
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        tracking=True,
        help='Leave empty to apply to all departments.',
    )
    amount_from = fields.Float(
        string='Amount From',
        help='Optional header amount range. Leave empty for no lower bound.',
    )
    amount_to = fields.Float(
        string='Amount To',
        help='Optional header amount range. Leave empty for no upper bound.',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
    )

    # ---- Description ----
    description = fields.Text(string='Description', translate=True)
    note = fields.Text(string='Internal Note', translate=True)

    # ---- Lines ----
    line_ids = fields.One2many(
        'dcg.approval.matrix.line',
        'matrix_id',
        string='Approval Steps',
        copy=True,
    )
    line_count = fields.Integer(
        string='Step Count',
        compute='_compute_line_count',
    )

    _sql_constraints = [
        (
            'code_uniq',
            'unique(code)',
            'Approval Matrix code must be unique.',
        ),
    ]

    # ---- Compute ----
    @api.depends('line_ids')
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.line_ids)

    # ---- Constraints ----
    @api.constrains('amount_from', 'amount_to')
    def _check_amount_range(self):
        for rec in self:
            if rec.amount_from and rec.amount_to and rec.amount_from > rec.amount_to:
                raise ValidationError(_(
                    "Matrix '%s': Amount From must be less than or equal to Amount To."
                ) % rec.display_name)

    @api.constrains('active', 'line_ids')
    def _check_active_has_lines(self):
        for rec in self:
            if rec.active and not rec.line_ids.filtered('active'):
                raise ValidationError(_(
                    "Matrix '%s' is active but has no active step. Please add at least one active step."
                ) % rec.display_name)

    # ---- Engine helpers (called by mixin) ----
    @api.model
    def _find_best_matrix(self, approval_type, company, department, amount):
        """Tìm matrix phù hợp nhất theo độ ưu tiên:

        - level 1: company khớp + department khớp
        - level 2: company khớp + department rỗng
        - level 3: company rỗng + department khớp
        - level 4: company rỗng + department rỗng

        Trong cùng level: sequence tăng dần, rồi id tăng dần.
        Nếu cùng level có nhiều matrix khớp → raise ValidationError.
        """
        domain = [
            ('active', '=', True),
            ('approval_type', '=', approval_type),
        ]
        matrices = self.search(domain, order='sequence, id')
        if not matrices:
            return self.browse()

        # Filter by amount range (header)
        def amount_ok(m):
            if m.amount_from and amount < m.amount_from:
                return False
            if m.amount_to and amount > m.amount_to:
                return False
            return True

        matrices = matrices.filtered(amount_ok)

        # Filter by company
        company_id = company.id if company else False
        matrices = matrices.filtered(
            lambda m: (not m.company_id) or (m.company_id.id == company_id)
        )
        # Filter by department
        department_id = department.id if department else False
        matrices = matrices.filtered(
            lambda m: (not m.department_id) or (m.department_id.id == department_id)
        )

        if not matrices:
            return self.browse()

        # Rank
        def rank(m):
            if m.company_id and m.department_id:
                return 1
            if m.company_id and not m.department_id:
                return 2
            if not m.company_id and m.department_id:
                return 3
            return 4

        ranked = sorted(matrices, key=lambda m: (rank(m), m.sequence, m.id))
        best_rank = rank(ranked[0])
        best_seq = ranked[0].sequence
        best = [m for m in ranked if rank(m) == best_rank and m.sequence == best_seq]

        if len(best) > 1:
            raise ValidationError(_(
                "Multiple approval matrices match this document (type=%(t)s). "
                "Please review matrix configuration: %(names)s"
            ) % {
                't': approval_type,
                'names': ', '.join(m.display_name for m in best),
            })
        return ranked[0]

    def action_view_lines(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Approval Steps'),
            'res_model': 'dcg.approval.matrix.line',
            'view_mode': 'list,form',
            'domain': [('matrix_id', '=', self.id)],
            'context': {'default_matrix_id': self.id},
        }
