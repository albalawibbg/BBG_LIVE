# -*-coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError


class HrLoan(models.Model):
    _inherit = "hr.loan"

    def reset_to_draft(self):
        for line in self.loan_lines:
            if line.paid:
                raise UserError(_('You cannot make reset paid entries.'))
        rec = self.env['account.move'].search([('ref', '=', self.name)])
        if rec:
            rec.button_draft()
            rec.button_cancel()
        self.update({'state': 'draft'})

