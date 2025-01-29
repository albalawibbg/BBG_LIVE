# -*- coding: utf-8 -*-
import time
from odoo import models, api, fields
from odoo.exceptions import UserError, ValidationError


class loan_payments(models.Model):
    _name = 'loan.payments'

    name = fields.Char(string="Name", required=True, help='Payment name')
    debit_account_id = fields.Many2one('account.account', string="Debit Account", required=True,
                                       help='Debit account for journal entry')
    credit_account_id = fields.Many2one('account.account', string="Credit Account", required=True,
                                        help='Credit account for journal entry')
    journal_id = fields.Many2one('account.journal', string="Journal", required=True, help='Journal for journal entry')


class HrLoanAcc(models.Model):
    _inherit = 'hr.loan'

    employee_account_id = fields.Many2one('account.account', string="Credit Account")
    treasury_account_id = fields.Many2one('account.account', string="Debit Account")
    journal_id = fields.Many2one('account.journal', string="Journal")
    pay_method = fields.Many2one('loan.payments', string='Loan Type', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval_1', 'Submitted'),
        ('waiting_approval_2', 'Waiting Approval'),
        ('approve1', 'First Approval'),
        ('approve', 'Approved'),
        ('reschedule', 'Reschedule'),
        ('refuse', 'Refused'),
        ('cancel', 'Canceled'),
    ], string="State", default='draft', track_visibility='onchange', copy=False, )

    def action_approve(self):
        """This create account move for request.
            """
        # loan_approve = self.env['ir.config_parameter'].sudo().get_param('account.loan_approve')
        contract_obj = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)])
        if not contract_obj:
            raise UserError('You must Define a contract for employee')
        if not self.loan_lines:
            raise UserError('You must compute installment before Approved')

        # if loan_approve:
        # self.write({'state': 'waiting_approval_2'})
        # else:
        if not self.pay_method.debit_account_id or not self.pay_method.credit_account_id or not self.pay_method.journal_id:
            raise UserError("You must enter Payment Method Credit account & Debit account and journal to approve ")
        if not self.loan_lines:
            raise UserError('You must compute Loan Request before Approved')
        timenow = time.strftime('%Y-%m-%d')
        for loan in self:
            lines_amount = sum(loan.loan_lines.mapped('amount'))
            if loan.loan_amount != lines_amount:
                raise ValidationError('Loan Amount must be equal to Total Amount')
            for tab in loan.loan_lines:
                if tab.amount < 0.0:
                    raise ValidationError('One of the Installment Amount is in Negative Value')
            amount = loan.loan_amount
            loan_name = loan.employee_id.name
            reference = loan.name
            journal_id = loan.pay_method.journal_id.id
            debit_account_id = loan.pay_method.debit_account_id.id
            credit_account_id = loan.pay_method.credit_account_id.id
            debit_vals = {
                'name': loan_name,
                'account_id': debit_account_id,
                'journal_id': journal_id,
                'partner_id': loan.employee_id.address_id.id,
                'date': timenow,
                'debit': amount > 0.0 and amount or 0.0,
                'credit': amount < 0.0 and -amount or 0.0,
                'loan_id': loan.id,
            }
            credit_vals = {
                'name': loan_name,
                'account_id': credit_account_id,
                'journal_id': journal_id,
                'partner_id': loan.employee_id.address_id.id,
                'date': timenow,
                'debit': amount < 0.0 and -amount or 0.0,
                'credit': amount > 0.0 and amount or 0.0,
                'loan_id': loan.id,
            }
            vals = {
                'narration': loan_name,
                'ref': reference,
                'journal_id': journal_id,
                'date': timenow,
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
            }
            move = self.env['account.move'].create(vals)
            move.action_post()
        self.write({'state': 'approve'})
        return True

    def action_reschedule(self):
        for record in self:
            record.write({'state': 'reschedule'})

    def action_reschedule_done(self):
        for record in self:
            lines_amount = sum(record.loan_lines.mapped('amount'))
            for tab in record.loan_lines:
                current_date = fields.Date.today()
                # print('TTTTTTTTTTTTTTTTTTTTTT',current_date)
                if tab.amount < 0.0:
                    raise ValidationError('One of the Installment Amount is in Minus Value')
                if tab.paid == False:
                    if current_date > tab.date:
                        raise ValidationError('One of the Installment Date is before current date')
            if record.loan_amount != lines_amount:
                raise ValidationError('Loan Amount must be equal to Total Amount')
            record.write({'state': 'approve'})

    def action_double_approve(self):
        """This create account move for request in case of double approval.
            """
        if not self.pay_method.debit_account_id or not self.pay_method.credit_account_id or not self.pay_method.journal_id:
            raise UserError("You must enter Payment Method Credit account & Debit account and journal to approve ")
        if not self.loan_lines:
            raise UserError('You must compute Loan Request before Approved')
        timenow = time.strftime('%Y-%m-%d')
        for loan in self:
            lines_amount = sum(loan.loan_lines.mapped('amount'))
            if loan.loan_amount != lines_amount:
                raise ValidationError('Loan Amount must be equal to Total Amount')
            for tab in loan.loan_lines:
                if tab.amount < 0.0:
                    raise ValidationError('One of the Installment Amount is in Minus Value')
            amount = loan.loan_amount
            loan_name = loan.employee_id.name
            reference = loan.name
            journal_id = loan.pay_method.journal_id.id
            debit_account_id = loan.pay_method.debit_account_id.id
            credit_account_id = loan.pay_method.credit_account_id.id
            debit_vals = {
                'name': loan_name,
                'account_id': debit_account_id,
                'journal_id': journal_id,
                'partner_id': loan.employee_id.address_id.id,
                'date': timenow,
                'debit': amount > 0.0 and amount or 0.0,
                'credit': amount < 0.0 and -amount or 0.0,
                'loan_id': loan.id,
            }
            credit_vals = {
                'name': loan_name,
                'account_id': credit_account_id,
                'journal_id': journal_id,
                'partner_id': loan.employee_id.address_id.id,
                'date': timenow,
                'debit': amount < 0.0 and -amount or 0.0,
                'credit': amount > 0.0 and amount or 0.0,
                'loan_id': loan.id,
            }
            vals = {
                'narration': loan_name,
                'ref': reference,
                'journal_id': journal_id,
                'date': timenow,
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
            }
            move = self.env['account.move'].create(vals)
            move.action_post()
        self.write({'state': 'approve'})
        return True


class HrLoanLineAcc(models.Model):
    _inherit = "hr.loan.line"

    pay_type = fields.Selection([('deductsalary', 'Salary Deduct'), ('paycash', 'Cash Pay')], default='deductsalary',
                                string="Type", readonly=True)

    def action_paid_amount(self):
        """This create the account move line for payment of each installment.
            """
        timenow = time.strftime('%Y-%m-%d')
        for line in self:
            if line.loan_id.state != 'approve':
                raise UserError("Loan Request must be approved")
            amount = line.amount
            loan_name = line.employee_id.name
            reference = line.loan_id.name
            journal_id = line.loan_id.pay_method.journal_id.id
            debit_account_id = line.loan_id.pay_method.credit_account_id.id
            credit_account_id = line.loan_id.pay_method.debit_account_id.id

            debit_vals = {
                'name': loan_name,
                'account_id': debit_account_id,
                'journal_id': journal_id,
                'partner_id': line.employee_id.address_id.id,
                'date': timenow,
                'debit': amount > 0.0 and amount or 0.0,
                'credit': amount < 0.0 and -amount or 0.0,
            }
            credit_vals = {
                'name': loan_name,
                'account_id': credit_account_id,
                'journal_id': journal_id,
                'partner_id': line.employee_id.address_id.id,
                'date': timenow,
                'debit': amount < 0.0 and -amount or 0.0,
                'credit': amount > 0.0 and amount or 0.0,
            }
            vals = {
                'narration': loan_name,
                'ref': reference,
                'journal_id': journal_id,
                'date': timenow,
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
            }
            move = self.env['account.move'].create(vals)
            move.action_post()
        return True


class HrPayslipAcc(models.Model):
    _inherit = 'hr.payslip'

    '''def action_payslip_done(self):
        for line in self.input_line_ids:
            self.compute_sheet()
            if line.loan_line_ids:
                line.loan_line_ids.action_paid_amount()
        return super(HrPayslipAcc, self).action_payslip_done()'''

    '''def action_payslip_done(self):
        print("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF")
        #self.compute_sheet()
        for line in self.input_line_ids:
            #self.compute_sheet()
            if line.loan_line_ids:
                line.loan_line_ids.action_paid_amount()
        res = super(HrPayslipAcc, self).action_payslip_done()
        for line in self.input_line_ids:
            if line.loan_line_ids:
                line.loan_line_ids.write({'paid': True})
                loan_id = list(set(line.loan_line_ids.mapped('loan_id')))
                if loan_id:
                    loan_id[0]._compute_loan_amount()
        return res'''
