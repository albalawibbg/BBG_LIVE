from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _, Command
from odoo.exceptions import ValidationError


class ArtecHrMonthlyAccrual(models.Model):
    _name = 'hr.monthly.accrual'
    _description = 'HR Monthly accrual'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Name",
    )
    department_ids = fields.Many2many(
        'hr.department',
        string='Departments',
    )
    date_from = fields.Date(
        'Date from',
        required=True,
    )
    date_to = fields.Date(
        'Date to',
    )
    duration = fields.Float(
        'Duration (DAYS/month)',
    )
    total_duration = fields.Float(
        'Total duration (Days)',
        compute='_compute_total_duration'
    )
    months = fields.Float(
        'Nbr of Months',
        compute='_compute_months'

    )
    time_limit = fields.Boolean(
        'Limited by period'
    )
    employee_ids = fields.Many2many(
        'hr.employee',
        string="Employee",
        # domain=[('department_id', '=', department_ids)]
    )
    leave_type_id = fields.Many2one(
        'hr.leave.type',
        string="Leave Type",
    )
    allocation_id = fields.Many2one(
        'hr.leave.allocation',
        'Allocation'
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ],
        string="State",
        default='draft',
        tracking=True,
        copy=False,
    )

    @api.depends('date_to', 'date_from')
    def _compute_months(self):
        for rec in self:
            delta_months = 0
            if rec.date_from and rec.date_to:
                delta = relativedelta(rec.date_to, rec.date_from)
                delta_months = delta.months + (delta.years * 12)
                if delta.days >= 30:
                    delta_months += 1
            rec.months = delta_months

    @api.depends('duration', 'date_to', 'date_from')
    def _compute_total_duration(self):
        for rec in self:
            total_duration = 0
            if rec.date_from and rec.date_to:
                total_duration = rec.months * rec.duration
            rec.total_duration = total_duration

    def update_employees_by_department(self):
        self.employee_ids = False
        for dep in self.department_ids:
            employees = self.env['hr.employee'].search([('department_id', '=', dep.id)])
            for employee in employees:
                self.employee_ids += employee

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirm'

    def action_done(self):
        for rec in self:
            if not rec.allocation_id:
                rec._create_employees_accrual()
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def _create_employees_accrual(self):
        if not self.employee_ids:
            raise ValidationError(_("Select at least One employee and proceed !"))
        vals = {
            'employee_ids': self.employee_ids.ids,
            'name': self.name,
            'date_from': self.date_from,
            'date_to': self.date_to if not self.time_limit else False,
            'holiday_status_id': self.leave_type_id.id,
            'allocation_type': 'regular',
            'number_of_days': self.total_duration,
            'holiday_type': 'employee',
            "multi_employee": True,
        }

        self.allocation_id = self.env['hr.leave.allocation'].create(vals)
        self.allocation_id.action_confirm()
        self.allocation_id.action_validate()
