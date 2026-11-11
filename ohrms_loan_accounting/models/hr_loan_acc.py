# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.tools import float_compare
from odoo.exceptions import UserError, ValidationError


class LoanPayments(models.Model):
    _name = 'loan.payments'
    _description = 'Loan Payment Method'

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
    ], string="State", default='draft', tracking=True, copy=False, )

    def _check_employee_contract(self, date):
        """Odoo 19 stores employee contracts as dated hr.version records."""
        self.ensure_one()
        if not self.employee_id or not self.employee_id._is_in_contract(date):
            raise UserError(_(
                "Employee %(employee)s must have an active contract on %(date)s "
                "before the loan can be approved."
            ) % {'employee': self.employee_id.name or _('Unknown'), 'date': date})

    def _check_loan_posting(self):
        """Prevent a second disbursement entry for the same loan."""
        self.ensure_one()
        existing = self.env['account.move.line'].search([
            ('loan_id', '=', self.id),
            ('move_id.state', '!=', 'cancel'),
        ], limit=1)
        if existing:
            raise UserError(_(
                "A loan accounting entry already exists (%s). "
                "Review or reverse it before trying to approve again."
            ) % (existing.move_id.display_name,))

    def action_approve(self):
        """Approve the loan and create the initial accounting entry."""
        timenow = fields.Date.context_today(self)
        for loan in self:
            loan._check_employee_contract(timenow)
            loan._check_loan_posting()
            if not loan.loan_lines:
                raise UserError('You must compute installment before Approved')
            if not loan.pay_method.debit_account_id or not loan.pay_method.credit_account_id or not loan.pay_method.journal_id:
                raise UserError("You must enter Payment Method Credit account & Debit account and journal to approve ")

            lines_amount = sum(loan.loan_lines.mapped('amount'))
            if float_compare(loan.loan_amount, lines_amount, precision_rounding=loan.company_id.currency_id.rounding if 'company_id' in loan._fields and loan.company_id else self.env.company.currency_id.rounding) != 0:
                raise ValidationError('Loan Amount must be equal to Total Amount')
            for tab in loan.loan_lines:
                if tab.amount < 0.0:
                    raise ValidationError('One of the Installment Amount is in Negative Value')

            move = loan._create_loan_move(
                amount=loan.loan_amount,
                debit_account=loan.pay_method.debit_account_id,
                credit_account=loan.pay_method.credit_account_id,
                journal=loan.pay_method.journal_id,
                date=timenow,
                include_loan_link=True,
            )
            move.action_post()
            loan.write({'state': 'approve'})
        return True

    def _create_loan_move(self, amount, debit_account, credit_account, journal, date, include_loan_link=False):
        self.ensure_one()
        partner = self.employee_id.work_contact_id
        line_common = {
            'name': self.employee_id.name,
            'journal_id': journal.id,
            'partner_id': partner.id if partner else False,
            'date': date,
        }
        debit_vals = dict(line_common, **{
            'account_id': debit_account.id,
            'debit': amount if amount > 0.0 else 0.0,
            'credit': -amount if amount < 0.0 else 0.0,
        })
        credit_vals = dict(line_common, **{
            'account_id': credit_account.id,
            'debit': -amount if amount < 0.0 else 0.0,
            'credit': amount if amount > 0.0 else 0.0,
        })
        if include_loan_link:
            debit_vals['loan_id'] = self.id
            credit_vals['loan_id'] = self.id
        return self.env['account.move'].create({
            'narration': self.employee_id.name,
            'ref': self.name,
            'journal_id': journal.id,
            'date': date,
            'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)],
        })

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
        """Approve the loan and create the accounting entry after second approval."""
        timenow = fields.Date.context_today(self)
        for loan in self:
            loan._check_employee_contract(timenow)
            loan._check_loan_posting()
            if not loan.pay_method.debit_account_id or not loan.pay_method.credit_account_id or not loan.pay_method.journal_id:
                raise UserError("You must enter Payment Method Credit account & Debit account and journal to approve ")
            if not loan.loan_lines:
                raise UserError('You must compute Loan Request before Approved')

            lines_amount = sum(loan.loan_lines.mapped('amount'))
            if float_compare(loan.loan_amount, lines_amount, precision_rounding=loan.company_id.currency_id.rounding if 'company_id' in loan._fields and loan.company_id else self.env.company.currency_id.rounding) != 0:
                raise ValidationError('Loan Amount must be equal to Total Amount')
            for tab in loan.loan_lines:
                if tab.amount < 0.0:
                    raise ValidationError('One of the Installment Amount is in Minus Value')

            move = loan._create_loan_move(
                amount=loan.loan_amount,
                debit_account=loan.pay_method.debit_account_id,
                credit_account=loan.pay_method.credit_account_id,
                journal=loan.pay_method.journal_id,
                date=timenow,
                include_loan_link=True,
            )
            move.action_post()
            loan.write({'state': 'approve'})
        return True


class HrLoanLineAcc(models.Model):
    _inherit = "hr.loan.line"

    pay_type = fields.Selection([('deductsalary', 'Salary Deduct'), ('paycash', 'Cash Pay')], default='deductsalary',
                                string="Type", readonly=True)

    def action_paid_amount(self):
        """Create the accounting entry for each paid installment."""
        timenow = fields.Date.context_today(self)
        for line in self:
            if line.paid:
                raise UserError(_('This installment is already marked paid.'))
            if line.loan_id.state != 'approve':
                raise UserError("Loan Request must be approved")
            loan = line.loan_id
            amount = line.amount
            journal = loan.pay_method.journal_id
            debit_account = loan.pay_method.credit_account_id
            credit_account = loan.pay_method.debit_account_id
            if not debit_account or not credit_account or not journal:
                raise UserError("You must enter Payment Method Credit account & Debit account and journal to approve ")

            partner = line.employee_id.work_contact_id
            line_common = {
                'name': line.employee_id.name,
                'journal_id': journal.id,
                'partner_id': partner.id if partner else False,
                'date': timenow,
            }
            debit_vals = dict(line_common, **{
                'account_id': debit_account.id,
                'debit': amount if amount > 0.0 else 0.0,
                'credit': -amount if amount < 0.0 else 0.0,
            })
            credit_vals = dict(line_common, **{
                'account_id': credit_account.id,
                'debit': -amount if amount < 0.0 else 0.0,
                'credit': amount if amount > 0.0 else 0.0,
            })
            move = self.env['account.move'].create({
                'narration': line.employee_id.name,
                'ref': loan.name,
                'journal_id': journal.id,
                'date': timenow,
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)],
            })
            move.action_post()
            line.write({'paid': True})
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
