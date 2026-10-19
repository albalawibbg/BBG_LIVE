# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging

from datetime import datetime
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    @api.onchange('holiday_status_id')
    def _onchange_user_employees(self):
        res = {}
        if self.user_has_groups('hr_holidays.group_hr_holidays_user') is False:
            user_employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
            employee_ids = user_employee.child_ids.ids + [user_employee.id]
            res['domain'] = {'employee_id': [('id', 'in', employee_ids)]}
        return res

    # def _end_of_year_accrual(self):
    #     # to override in payroll
    #     first_day_this_year = fields.Date.today() + relativedelta(month=1, day=1)
    #     for allocation in self:
    #         current_level = allocation._get_current_accrual_plan_level_id(first_day_this_year)[0]
    #         nextcall = current_level._get_next_date(first_day_this_year)
    #         if current_level and current_level.action_with_unused_accruals == 'lost':
    #             # Allocations are lost but number_of_days should not be lower than leaves_taken
    #             allocation.write({'number_of_days': allocation.leaves_taken, 'lastcall': first_day_this_year, 'nextcall': nextcall})


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    remaining_leaves = fields.Float(
        # compute="_compute_leaves",
        string="Remaining leaves",
        readonly=True,
        store=True
    )

    @api.onchange('holiday_status_id', 'employee_id')
    def _compute_leaves(self):
        data_days = {}
        employee_id = self.employee_id.id

        if employee_id:
            data_days = (
                self.holiday_status_id.get_employees_days(employee_id)[employee_id[0]] if isinstance(employee_id,
                                                                                                     list) else
                self.holiday_status_id.get_employees_days([employee_id])[employee_id])

        for leave in self:
            result = data_days.get(leave.holiday_status_id.id, {})
            leave.remaining_leaves = result.get('remaining_leaves', 0)
            # import pdb
            # pdb.set_trace()

    @api.onchange('holiday_status_id')
    def _onchange_user_employees(self):
        res = {}
        if self.user_has_groups('hr_holidays.group_hr_holidays_user') is False:
            user_employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
            employee_ids = user_employee.child_ids.ids + [user_employee.id]
            res['domain'] = {'employee_id': [('id', 'in', employee_ids)]}
        return res
