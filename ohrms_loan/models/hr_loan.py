# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class HrLoan(models.Model):
	_name = 'hr.loan'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_description = "Loan Request"

	@api.depends('loan_lines.paid', 'loan_lines.amount')
	def _compute_loan_amount(self):
		for loan in self:
			total_paid = 0.0
			total_amt = 0.0
			loan_ids = self.env['hr.loan'].search([('employee_id', '=', loan.employee_id.id), ('state', '=', 'approve')])
			remaining_loans_lines = loan_ids.mapped('loan_lines').filtered(lambda l: l.paid is False)
			global_balance = sum(remaining_loans_lines.mapped('amount'))
			for line in loan.loan_lines:
				total_amt += line.amount
				if line.paid:
					total_paid += line.amount
			loan.update({
				'total_amount': total_amt,
				'total_paid_amount': total_paid,
				'balance_amount': total_amt - total_paid,
			})

	@api.model
	def default_get(self, field_list):
		result = super(HrLoan, self).default_get(field_list)
		if result.get('user_id'):
			ts_user_id = result['user_id']
		else:
			ts_user_id = self.env.context.get('user_id', self.env.user.id)
		result['employee_id'] = self.env['hr.employee'].search([('user_id', '=', ts_user_id)], limit=1).id
		return result

	'''def _compute_loan_amount(self):
		for loan in self:
			total_paid = 0.0
			for line in loan.loan_lines:
				if line.paid:
					_logger.info("Confirm Ids %s"%(line.paid))
					total_paid += line.amount
					_logger.info("Confirm Ids %s"%(total_paid))
					#print("TTTTTTTTTTTTTTTTTTTTTT",total_paid)
					#_logger.info("Confirm Ids %s"%(total_paid))
			balance_amount = loan.loan_amount - total_paid
			loan.total_paid_amount = total_paid
			loan.total_amount = loan.loan_amount
			loan.balance_amount = loan.loan_amount - total_paid'''

	name = fields.Char(string="Loan Name", readonly=True, help="Name of the loan")
	multi_loan = fields.Boolean(string="Multi Loan")
	date = fields.Date(string="Date", default=fields.Date.context_today, readonly=True, help="Date")
	employee_id = fields.Many2one('hr.employee', string="Employee", required=True, help="Employee")
	department_id = fields.Many2one('hr.department', related="employee_id.department_id", readonly=True,store=True,
									string="Department", help="Employee")
	installment = fields.Integer(string="No Of Installments", default=1, help="Number of installments")
	payment_date = fields.Date(string="Payment Start Date", required=True, default=fields.Date.context_today, help="Date of "
																											 "the "
																											 "paymemt")
	loan_lines = fields.One2many('hr.loan.line', 'loan_id', string="Loan Line", index=True)
	company_id = fields.Many2one('res.company', 'Company', readonly=True, help="Company",
								 default=lambda self: self.env.user.company_id,
								 )
	currency_id = fields.Many2one('res.currency', string='Currency', required=True, help="Currency",
								  default=lambda self: self.env.user.company_id.currency_id)
	job_position = fields.Many2one('hr.job', related="employee_id.job_id", readonly=True, string="Job Position",
								   help="Job position")
	loan_amount = fields.Float(string="Loan Amount", required=True, help="Loan amount")
	total_amount = fields.Monetary(string="Total Amount", store=True, readonly=True, compute='_compute_loan_amount',
								   help="Total loan amount")
	balance_amount = fields.Monetary(string="Balance Amount", store=True, compute='_compute_loan_amount',
									 help="Balance amount")
	global_balance_amount = fields.Monetary(string="Global Balance Amount",
											compute='_compute_loan_global_balance',
											help=" Global Balance amount")
	global_remaining_amount = fields.Monetary(string="Global Remainng Amount",
											  compute='_compute_loan_global_balance',
											  help=" Global Balance amount")

	total_paid_amount = fields.Monetary(string="Total Paid Amount", store=True, compute='_compute_loan_amount',
										help="Total paid amount")
	loan_journal_count = fields.Integer(string='Journal Count', compute='_get_journal_count', store=False)
	# manual_remaining = fields.Monetary(string="Manual Remaining")
	user_id = fields.Many2one(
		'res.users',
		string="User",
		default=lambda self: self.env.user
	)
	refuse_reason = fields.Text(
		'Refusal Reason'
	)
	date_refuse = fields.Datetime(
		'Refusal Datetime'
	)

	def _get_journal_count(self):
		for record in self:
			record.loan_journal_count = self.env['account.move'].search_count([('ref', '=', record.name)])

	def open_entries(self):
		return {
			'name': _('Journal Entries'),
			'view_mode': 'list,form',
			'res_model': 'account.move',
			'view_id': False,
			'type': 'ir.actions.act_window',
			"domain": [('ref', '=', self.name)]
		}

	state = fields.Selection([
		('draft', 'Draft'),
		('waiting_approval_1', 'Submitted'),
		('approve1', 'First Approval'),
		('approve', 'Second Approval'),
		('refuse', 'Refused'),
		('cancel', 'Canceled'),
	], string="State", default='draft', tracking=True, copy=False, )

	@api.onchange('user_id')
	def _onchange_user_employees(self):
		res = {}
		if self.env.user.has_group('ohrms_loan.group_loan_submit') and not (
				self.env.user.has_group('hr.group_hr_user') or
				self.env.user.has_group('hr.group_hr_manager')
		):
			user_employee = self.env['hr.employee'].search([('user_id', '=', self.user_id.id)], limit=1)
			employee_ids = user_employee.child_ids.ids + user_employee.ids
			res['domain'] = {'employee_id': [('id', 'in', employee_ids)]}
		return res

	@api.constrains('multi_loan')
	def _validate_multi_loan(self):
		loan_count = self.env['hr.loan'].search_count(
			[('employee_id', '=', self.employee_id.id), ('state', '=', 'approve'), ('balance_amount', '!=', 0)])
		if loan_count > 2:
			if self.multi_loan == False:
				raise ValidationError(_("The employee has already a pending installment."))

	def _compute_loan_global_balance(self):
		for loan in self:
			total_paid = 0.0
			total_amt = 0.0
			loan_ids = self.env['hr.loan'].search(
				[('employee_id', '=', loan.employee_id.id), ('state', '=', 'approve'), ('id', '!=', loan.id)])
			remaining_loans_lines = loan_ids.mapped('loan_lines').filtered(lambda l: l.paid is False)
			global_balance = sum(remaining_loans_lines.mapped('amount'))
			for line in loan.loan_lines:
				total_amt += line.amount
				if line.paid:
					total_paid += line.amount
			loan.update({
				'global_balance_amount': global_balance + (total_amt - total_paid),
				'global_remaining_amount': global_balance,
			})

	def action_view_loans(self):
		loan_ids = self.env['hr.loan'].search([('employee_id', '=', self.employee_id.id), ('state', '=', 'approve')])
		return {
			'name': _('Loans'),
			'res_model': 'hr.loan',
			'type': 'ir.actions.act_window',
			'target': 'current',
			'view_mode': 'list,form',
			'context': {
				'create': 0,
			},
			'domain': [('employee_id', '=', self.employee_id.id)]
		}

	@api.model_create_multi
	def create(self, vals_list):
		"""Assign a distinct loan reference for every record (Odoo 19 multi-create)."""
		for vals in vals_list:
			if not vals.get('name') or vals['name'] == 'New':
				vals['name'] = self.env['ir.sequence'].next_by_code('hr.loan.seq') or '/'
		return super().create(vals_list)

	def compute_installment(self):
		"""This automatically create the installment the employee need to pay to
		company based on payment start date and the no of installments.
			"""
		for loan in self:
			if loan.installment <= 0:
				raise ValidationError(_('Number of installments must be greater than zero.'))
			if loan.loan_lines.filtered('paid'):
				raise ValidationError(_('Cannot recompute installments after a payment has been registered.'))
			loan.loan_lines.unlink()
			date_start = datetime.strptime(str(loan.payment_date), '%Y-%m-%d')
			amount = loan.loan_amount / loan.installment
			for i in range(1, loan.installment + 1):
				self.env['hr.loan.line'].create({
					'date': date_start,
					'amount': amount,
					'employee_id': loan.employee_id.id,
					'loan_id': loan.id})
				date_start = date_start + relativedelta(months=1)
			loan._compute_loan_amount()
		return True

	def action_refuse(self):
		return {
			'name': _('Refuse Reason'),
			'res_model': 'refuse.loan.wizard',
			'type': 'ir.actions.act_window',
			'target': 'new',
			'view_mode': 'form',
		}

	def action_submit(self):
		for record in self:
			record._validate_multi_loan()
			lines_amount = sum(record.loan_lines.mapped('amount'))
			for tab in record.loan_lines:
				if tab.amount < 0.0:
					raise ValidationError('One of the Installment Amount is in Negative Value')
			if record.loan_amount != lines_amount:
				raise ValidationError('Loan Amount must be equal to Total Amount')
			if not record.loan_lines:
				raise ValidationError('You must Schedule Loan before Submit')
		self.write({'state': 'waiting_approval_1'})

	def action_cancel(self):
		self.write({'state': 'cancel'})

	def action_approve_1(self):
		for loan in self:
			loan._validate_multi_loan()
			loan.write({'state': 'approve1'})

	def action_approve(self):
		for data in self:
			data._validate_multi_loan()
			lines_amount = sum(data.loan_lines.mapped('amount'))
			for tab in data.loan_lines:
				if tab.amount < 0.0:
					raise ValidationError('One of the Installment Amount is in Negative Value')
			if data.loan_amount != lines_amount:
				raise ValidationError('Loan Amount must be equal to Total Amount')
			if not data.loan_lines:
				raise ValidationError(_("Please Compute installment"))
			else:
				data.write({'state': 'approve'})

	def unlink(self):
		for loan in self:
			if loan.state not in ('draft', 'cancel'):
				raise UserError(
					'You cannot delete a loan which is not in draft or cancelled state')
		return super(HrLoan, self).unlink()

	# def write(self, vals):
	# 	res = super(HrLoan, self).write(vals)
	# 	if self.state == 'approve':
	# 		if self.env.user.has_group('ohrms_loan.group_loan_advance_pay'):
	# 			if self.loan_amount != self.total_amount:
	# 				raise UserError('You cannot create unequal entry, All installments must be equal to loan amount.')
	# 		else:
	# 			raise UserError('Access Denied! You dont have access to edit approved Installment.')
	# 	return res


class InstallmentLine(models.Model):
	_name = "hr.loan.line"
	_description = "Installment Line"

	date = fields.Date(string="Payment Date", required=True, help="Date of the payment")
	employee_id = fields.Many2one('hr.employee', string="Employee", help="Employee")
	amount = fields.Float(string="Amount", required=True, help="Amount")
	paid = fields.Boolean(string="Paid", help="Paid")
	loan_id = fields.Many2one('hr.loan', string="Loan Ref.", help="Loan")
	payslip_id = fields.Many2one('hr.payslip', string="Payslip Ref.", help="Payslip")
	advance_pay_group = fields.Boolean(compute='get_current_uid_group', string='Advance Pay Group')

	def get_current_uid_group(self):
		"""Return whether the current user can manage advance loan payments."""
		has_group = self.env.user.has_group('ohrms_loan.group_loan_advance_pay')
		for line in self:
			line.advance_pay_group = has_group

	def unlink(self):
		for loan in self:
			if self.env.user.has_group('ohrms_loan.group_loan_advance_pay'):
				if loan.paid:
					raise UserError('You cannot delete a Paid Installment')
			else:
				raise UserError('Access Denied! You dont have access to delete approved Installment.')
		return super(InstallmentLine, self).unlink()


class HrEmployee(models.Model):
	_inherit = "hr.employee"

	def _compute_employee_loans(self):
		"""Compute the total number of loans linked to each employee."""
		for employee in self:
			employee.loan_count = self.env['hr.loan'].search_count([('employee_id', '=', employee.id)])

	loan_count = fields.Integer(string="Loan Count", compute='_compute_employee_loans')

	'''def get_loan_deduction(self,employee, date_from, date_to):
		
		loan_obj = self.env['hr.loan']
		loan_amount = 0.00
		history_ids = self.env['hr.loan.line'].search_count([('date', '>=', date_from),('date', '<=', date_to),('employee_id', '=', employee),('paid', '=', False)])
		if history_ids:
			for each in history_ids:
				vals = self.env['hr.loan.line'].browse()
				if vals.loan_id.state == 'approve':
					loan_amount += vals.amount
					each.write({'paid': True})
		return loan_amount'''


class HrAdvanceLoanPayment(models.Model):
	_name = "hr.advance.loan.payment"
	_description = "Advance Loan Payment"
#
#     loan_name = fields.Char(string="Loan Name", required=True, readonly=True, store=True,)
#     employee_account_id = fields.Many2one('account.account', string="Credit Account", required=True, readonly=True, store=True,)
#     treasury_account_id = fields.Many2one('account.account', string="Debit Account", required=True, readonly=True, store=True,)
#     journal_id = fields.Many2one('account.journal', string="Journal", required=True, readonly=True, store=True,)
#     advance_amount = fields.Monetary(string="Advance Amount", store=True, help="Advance Amount", required=True)
#     payment_date = fields.Date(string="Payment Date", required=True, default=fields.Date.context_today,
#                                help="Date of the payment", store=True)
#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('posted', 'Posted'),
#     ], string="State", default='draft', copy=False, )
#     currency_id = fields.Many2one('res.currency', string='Currency', required=True, help="Currency",
#                                   default=lambda self: self.env.user.company_id.currency_id)
#     loan_id = fields.Many2one('hr.loan', string="Loan Ref.", help="Loan", required=True)
#     # loan_line_ids = fields.Many2many('hr.loan.line', string="Loan Lines", help="Loan", required=True,
#     #                            domain="[('loan_id', '=', loan_id)]")
#     remaining_amount = fields.Monetary(string="Remaining Amount", store=True, help="Remaining Amount", required=True, readonly=True)
#
#     @api.onchange('loan_id')
#     def _onchange_loan_id(self):
#         if self.loan_id.state == 'approve':
#             self.update({'loan_name': str(self.loan_id.name) + "-" + str(self.loan_id.employee_id.name)})
#             # self.loan_name = str(self.loan_id.name) + "-" + str(self.loan_id.employee_id.name)
#             self.employee_account_id = self.loan_id.pay_method.debit_account_id.id
#             self.treasury_account_id = self.loan_id.pay_method.credit_account_id.id
#             self.journal_id = self.loan_id.pay_method.journal_id.id
#             amount = 0.0
#             for line in self.loan_id.loan_lines:
#                 if not line.paid:
#                     amount += line.amount
#             self.remaining_amount = amount
#
#     @api.onchange('advance_amount')
#     def _onchange_advance_amount(self):
#         if self.advance_amount > self.remaining_amount:
#             raise ValidationError(_("Please enter amount less than or equal to the remaining amount"))
#
#     def action_post(self):
#         self.ensure_one()
#         for loan in self:
#             amount = loan.advance_amount
#             loan_name = loan.loan_id.employee_id.name
#             reference = loan.loan_name
#             journal_id = loan.journal_id.id
#             debit_account_id = loan.treasury_account_id.id
#             credit_account_id = loan.employee_account_id.id
#             debit_vals = {
#                 'name': loan_name,
#                 'account_id': debit_account_id,
#                 'journal_id': journal_id,
#                 'partner_id': loan.loan_id.employee_id.address_home_id.id,
#                 'date': self.payment_date,
#                 'debit': amount > 0.0 and amount or 0.0,
#                 'credit': amount < 0.0 and -amount or 0.0,
#                 'loan_id': loan.loan_id.id,
#             }
#             credit_vals = {
#                 'name': loan_name,
#                 'account_id': credit_account_id,
#                 'journal_id': journal_id,
#                 'partner_id': loan.loan_id.employee_id.address_home_id.id,
#                 'date': self.payment_date,
#                 'debit': amount < 0.0 and -amount or 0.0,
#                 'credit': amount > 0.0 and amount or 0.0,
#                 'loan_id': loan.loan_id.id,
#             }
#             vals = {
#                 'narration': loan_name,
#                 'ref': reference,
#                 'journal_id': journal_id,
#                 'date': self.payment_date,
#                 'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
#             }
#             move = self.env['account.move'].create(vals)
#             move.post()
#             self.write({'state': 'posted'})
#             # loan.loan_id.update({'manual_remaining': (loan.remaining_amount - loan.advance_amount)})
