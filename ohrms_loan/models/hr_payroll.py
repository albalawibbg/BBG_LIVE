# -*- coding: utf-8 -*-
import time
import babel
from odoo import models, fields, api, tools, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class Employee(models.Model):
    _inherit = 'hr.employee'

    def get_loan_deduction(self, employee, date_from, date_to):
        employee_id = self.browse([employee])
        lon_obj = self.env['hr.loan'].search([('employee_id', '=', employee_id.id), ('state', '=', 'approve')])
        loan_line_ids = self.env['hr.loan.line'].search([('loan_id', 'in', lon_obj.ids), 
                        ('date', '>=', date_from.strftime(DEFAULT_SERVER_DATE_FORMAT)), 
                        ('date', '<=', date_to.strftime(DEFAULT_SERVER_DATE_FORMAT)), 
                        ('paid', '=', False)])
        amount = round(sum(loan_line_ids.mapped('amount')), 2) if loan_line_ids else 0.0
        return amount

'''class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    loan_line_ids = fields.Many2many('hr.loan.line', string='Loan Installment', help="Loan installment")'''

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    '''@api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return

        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to
        contract_ids = []

        ttyme = datetime.fromtimestamp(time.mktime(time.strptime(str(date_from), "%Y-%m-%d")))
        locale = self.env.context.get('lang') or 'en_US'
        self.name = _('Salary Slip of %s for %s') % (
            employee.name, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))
        self.company_id = employee.company_id

        if not self.env.context.get('contract') or not self.contract_id:
            contract_ids = self._get_contracts(date_from, date_to)
            if not contract_ids:
                return
            self.contract_id = self.env['hr.contract'].browse(contract_ids[0])

        if not self.contract_id.struct_id:
            return
        self.struct_id = self.contract_id.struct_id

        # computation of the salary input
        contracts = self.env['hr.contract'].browse(contract_ids)
        worked_days_line_ids = self.get_worked_day_lines(contracts, date_from, date_to)
        if worked_days_line_ids:
            worked_days_lines = self.worked_days_line_ids.browse([])
            for r in worked_days_line_ids:
                worked_days_lines += worked_days_lines.new(r)
            self.worked_days_line_ids = worked_days_lines
        if contracts:
            input_line_ids = self.get_inputs(contracts, date_from, date_to)
            print (">input_line_ids", input_line_ids)
            input_lines = self.input_line_ids.browse([])
            for r in input_line_ids:
                input_lines += input_lines.new(r)
            self.input_line_ids = input_lines
        return

    def get_inputs(self, contract_ids, date_from, date_to):
        
        res = super(HrPayslip, self).get_inputs(contract_ids, date_from, date_to)
        contract_obj = self.env['hr.contract']
        emp_id = contract_obj.browse(contract_ids[0].id).employee_id
        lon_obj = self.env['hr.loan'].search([('employee_id', '=', emp_id.id), ('state', '=', 'approve')])
        loan_line_ids = self.env['hr.loan.line'].search([('loan_id', 'in', lon_obj.ids), 
                        ('date', '>=', date_from.strftime(DEFAULT_SERVER_DATE_FORMAT)), 
                        ('date', '<=', date_to.strftime(DEFAULT_SERVER_DATE_FORMAT)), 
                        ('paid', '=', False)])
        amount = round(sum(loan_line_ids.mapped('amount')), 2) if loan_line_ids else 0.0
        line_ids = [(6, 0, loan_line_ids.ids)] if loan_line_ids else [(6, 0, [])]
        for result in res:
            if result.get('code') == 'LO':
                result['amount'] = amount
                result['loan_line_ids'] = line_ids
        return res'''

    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()
        for slip in self:
            lon_obj = self.env['hr.loan'].search([('employee_id', '=', slip.employee_id.id), ('state', '=', 'approve')])
            loan_line_ids = self.env['hr.loan.line'].search([('loan_id', 'in', lon_obj.ids),
                            ('date', '>=', slip.date_from.strftime(DEFAULT_SERVER_DATE_FORMAT)),
                            ('date', '<=', slip.date_to.strftime(DEFAULT_SERVER_DATE_FORMAT)),
                            ('paid', '=', False)])
            loan_line_ids.write({'paid': True})
        return res
