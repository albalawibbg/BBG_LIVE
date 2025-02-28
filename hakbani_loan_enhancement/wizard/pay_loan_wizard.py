# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
from datetime import date, timedelta
from odoo.exceptions import ValidationError, UserError


class PayLoanWizard(models.TransientModel):
    _name = "pay.loan.wizard"
    _description = "Pay Loan Wizard"

    date = fields.Date("Date", default=date.today())
    ref = fields.Char("Description")
    journal_id = fields.Many2one("account.journal", string="Journal", required=True)

    def create_loan_payment_entry(self):
        loan_rec_id = self.env.context.get('active_ids', [])
        loan_rec = self.env['hr.loan'].search([('id', '=', loan_rec_id)])
        for loan in loan_rec:
            amount = loan.balance_amount
            if amount <= 0:
                raise UserError('Your remaining amount is zero.')
            loan_name = loan.employee_id.name
            reference = loan.name
            journal_id = self.journal_id.id
            debit_account_id = loan.pay_method.credit_account_id.id
            credit_account_id = self.journal_id.default_account_id.id
            debit_vals = {
                'name': loan_name,
                'account_id': debit_account_id,
                'journal_id': journal_id,
                'partner_id': loan.employee_id.address_home_id.id,
                'date': self.date,
                'debit': amount > 0.0 and amount or 0.0,
                'credit': amount < 0.0 and -amount or 0.0,
            }
            credit_vals = {
                'name': loan_name,
                'account_id': credit_account_id,
                'journal_id': journal_id,
                'partner_id': loan.employee_id.address_home_id.id,
                'date': self.date,
                'debit': amount < 0.0 and -amount or 0.0,
                'credit': amount > 0.0 and amount or 0.0,
            }
            vals = {
                'narration': loan_name,
                'ref': reference,
                'journal_id': journal_id,
                'date': self.date,
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
            }
            move = self.env['account.move'].create(vals)
            move.action_post()
            for line in loan.loan_lines:
                line.update({'paid': True})
