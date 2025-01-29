# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

from datetime import datetime
from dateutil import relativedelta

_logger = logging.getLogger(__name__)


class HrWorkEntryRegeneration(models.TransientModel):
    _inherit = 'hr.work.entry.regeneration.wizard'
    # employee_id = fields.Many2one(
    #     required=False,
    # )
    multiple_employees = fields.Boolean('Regenerate for multiple employees')
    # employee_ids = fields.Many2many(
    #     'hr.employee',
    #     string="Employees",
    # )

    # def regenerate_we_multiple(self):
    #     for wiz in self:
    #         for employee in wiz.employee_ids:
    #             wiz._regenerate_we_multiple(employee)
    #         action = self.env["ir.actions.actions"]._for_xml_id('hr_work_entry.hr_work_entry_action')
    #         return action

    # def _regenerate_we_multiple(self, employee):
    #     self.ensure_one()
    #     date_from = self.date_from
    #     date_to = self.date_to
    #     work_entries = self.env['hr.work.entry'].search([
    #         ('employee_id', '=', employee.id),
    #         ('date_stop', '>=', date_from),
    #         ('date_start', '<=', date_to),
    #         ('state', '!=', 'validated')])
    #
    #     work_entries.write({'active': False})
    #     employee.generate_work_entries(date_from, date_to, True)

    # @api.onchange('multiple_employees')
    # def _onchange_multiple_employees(self):
    #     for wiz in self:
    #         if wiz.multiple_employees:
    #             wiz.employee_id = False
