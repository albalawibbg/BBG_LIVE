# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
# from odoo.exceptions import Warning
from datetime import date, datetime

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    outstanding_fields = fields.Float(string="Outstanding Amount",  compute='_compute_outstanding_fields')

    def _compute_outstanding_fields(self):
        for me in self:
            #pay_term_lines = me.move_id.line_ids\
                #.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))

            domain = [
                #('account_id', 'in', pay_term_lines.account_id.ids),
                ('move_id.state', '=', 'posted'),
                ('partner_id', '=', me.partner_id.id),
                ('reconciled', '=', False),
                '|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0),
            ]
            outstanding_fields = 0.0
            for line in self.env['account.move.line'].search(domain):
                outstanding_fields += line.amount_residual
            self.outstanding_fields = outstanding_fields




















