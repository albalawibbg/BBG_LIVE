from odoo import fields, models, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools import float_is_zero, float_compare
from odoo.addons import decimal_precision as dp
import time
from datetime import datetime, timedelta
from dateutil import relativedelta
from datetime import datetime
import babel
import datetime
from dateutil.relativedelta import relativedelta
import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp

import datetime
from dateutil.relativedelta import relativedelta
import time

import time
from datetime import datetime, timedelta
from dateutil import relativedelta
import babel


class account_move(models.Model):
    _inherit = 'account.move'

    payment_emp_id = fields.Many2one('employee.voucher', string='Employee Payment')


class hr_leave(models.Model):
    _inherit = "hr.leave"

    name = fields.Char('Description')
    voucher_ref = fields.Char('Voucher Refern')
    voucher_paid = fields.Boolean('Voucher Paid')


class hr_contract(models.Model):
    _inherit = "hr.contract"

    vacation = fields.Float('Annual Vacation Days', required=False)
    ticket = fields.Float('Eligible Employee Tickets', required=False)
    ticket_amount = fields.Float('Amount per Ticket', required=False)
    exit_entry = fields.Float('Eligible Employee Exit Re-Entry', required=False)
    exit_entry_amount = fields.Float('Amount per Exit Re-Entry', required=False)
    contract_years = fields.Integer('No of Years Contract', required=False)
    total_salary = fields.Float('Total Salary', required=False)
    gosiwage = fields.Float('Gosi Wage')
    end_less_date = fields.Date('Contract Renewal Date', requied=False)
    ticket_balance = fields.Float('Balance Ticket')
    exit_entry_balance = fields.Float('Balance Exit Re-Entry')
    rule1 = fields.Char('1')
    rule2 = fields.Char('2')
    rule3 = fields.Char('3')
    rule4 = fields.Char('4')
    rule5 = fields.Char('5')
    rule6 = fields.Char('6')
    value1 = fields.Float('val1')
    value2 = fields.Float('val2')
    value3 = fields.Float('val3')
    value4 = fields.Float('val4')
    value5 = fields.Float('val5')
    value6 = fields.Float('val6')

    working_years = fields.Float('Worked Period')
    working_months = fields.Float('Worked Months')
    working_days = fields.Float('Worked Days')


class employee_voucher(models.Model):
    _name = "employee.voucher"

    def _sel_func(self):
        obj = self.env['hr.leave']
        ids = obj.search([])
        res = obj.read(['name', 'id'])
        res = [(r['id'], r['name']) for r in res]
        return res

    name = fields.Char(string="Voucher Name", readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, readonly=True,
                                  )
    user_id = fields.Many2one('res.users', string='User',
                              related='employee_id.user_id', )
    date = fields.Date(string='date', readonly=True, default=lambda *a: time.strftime('%Y-%m-%d'))
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.user.company_id)
    # voucher_ref         = fields.Char(string='Voucher Referance', required=True)
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, readonly=True,
                                 )
    state = fields.Selection(
        [('draft', 'Draft'), ('submitted', 'Submitted'), ('confirm', 'Approval 1'), ('done', 'Approval 2'),
         ('cancel', 'Cancel')],
        string='Status', default='draft')

    balance_laon = fields.Float(string='Pending Loan Amount', readonly=True)
    ignore_loan = fields.Boolean(string='Proceed if Pending Loan')

    #################    LEGAL LEAVES    ##############################################

    legal_leave = fields.Boolean(string='Legal Leave', readonly=True, )
    voucher_method1 = fields.Many2one('employee.voucher.line', string='Employee Voucher Type1', readonly=True,
                                      default=lambda self: self.env['employee.voucher.line'].search(
                                          [('pay_type', '=', 'legal')]))
    paid_vacation = fields.Boolean(string='Paid Vacation')
    import_leave = fields.Boolean(string='Import Leave')

    @api.model
    def _populate_choice(self):
        if not self.legal_leave:
            selection = [('legal', 'Import Leave')]
        else:
            selection = [('legal', 'Import Leave'), ('paid', 'Paid Vacation')]

        return selection

    select_leave = fields.Selection(selection=_populate_choice, string='Select Leave',
                                    readonly=True, default='legal')
    leave_type_id = fields.Many2one(
        'hr.leave.type',
        string="Leave type",
        default=lambda self: self.env.ref('hr_holidays.holiday_status_cl').id
    )
    import_legal = fields.Many2one('hr.leave', string='Import Legal Leaves',
                                   domain="[('employee_id', '=', employee_id),('state','=','validate'),('holiday_status_id','=',leave_type_id),('name','!=','Paid Legalleaves'),('voucher_paid','=',False)]",
                                   selection=_sel_func, readonly=True, )

    @api.onchange('legal_leave')
    def _onchange_legal_leave(self):
        for rec in self:
            res = {}
            if rec.legal_leave:
                employee_leave_ids = self.env['employee.voucher'].search(
                    [('employee_id', '=', rec.employee_id.id), ('state', '=', 'done'),
                     ('legal_leave', '=', True)]).mapped('import_legal')
                res['domain'] = {'import_legal': [('employee_id', '=', rec.employee_id.id),
                                                  ('id', '!=', employee_leave_ids.ids),
                                                  ('state', '=', 'validate'),
                                                  ('holiday_status_id', '=', rec.leave_type_id.id),
                                                  ('voucher_paid', '=', False)
                                                  ]}
            return res

    start_date = fields.Date(string='Start Date', readonly=True)
    end_date = fields.Date(string='End Date', readonly=True)
    no_days = fields.Float(string='No. of Legal Leaves Days')
    salary_legal = fields.Float(string='Salary of Legal Leaves Days', required=False)
    per_day_salary = fields.Float(string='Salary Per Day', readonly=True)
    remaining_leaves = fields.Float(string='Remaining Legal Leaves', readonly=True)

    move_id = fields.Many2one('account.move', string='Journal Entry', help='Journal Entry for Employee voucher')
    # moves_ids           = fields.Many2many('account.move','account_move_employee_voucher_rel','employee_id','payment_emp_id',string='Journal Entries',help='Journal entries related to this Employee Voucher')

    ######################## TICKETS ###################################################

    ticket_leave = fields.Boolean(string='Employee Ticket', readonly=True, )
    voucher_method2 = fields.Many2one('employee.voucher.line', string='Employee Payment Type2', readonly=True,
                                      default=lambda self: self.env['employee.voucher.line'].search(
                                          [('pay_type', '=', 'ticket')]))
    allocated_tickets = fields.Float(string='Allowed Empolyee Tickets', readonly=True)
    allocated_amount_tickets = fields.Float(string='Allowed Employee Tickets Amount', readonly=True)
    issue_tickets = fields.Float(string='Issue Employee Tickets', )
    issue_amount_tickets = fields.Float(string='Issue Employee Tickets Amount', required=True,
                                        )

    ######################### END OF SERVICE ########################################################

    end_service = fields.Boolean(string='End of service', readonly=True, )
    voucher_method3 = fields.Many2one('employee.voucher.line', string='Employee Payment Type3', readonly=True,
                                      default=lambda self: self.env['employee.voucher.line'].search(
                                          [('pay_type', '=', 'eos')]))
    whole_working = fields.Float(string='Whole Working Days', readonly=True)
    total_unpaid = fields.Float(string='Total Unpaid Leaves', readonly=True)
    actual_working = fields.Float(string='Actual Working Days', readonly=True)
    paid_amount = fields.Float(string='Pay Amount', required=True, )
    leave_reason = fields.Selection(
        [('endservice', 'End of Contract'), ('termination', 'Termination'), ('quit', 'Quit')],
        string='Job Leaving Reason', help="Reason of Employee job leaving", default='endservice')
    paid_eos_amount = fields.Float(string='Paid EOS Amount', readonly=True)
    e_remain_eos_amount = fields.Float(string='EOS Remaining C-Amount', readonly=True)
    e_total_eos_amount = fields.Float(string='EOS Total C-Amount', readonly=True)
    t_remain_eos_amount = fields.Float(string='EOS Remaining T-Amount', readonly=True)
    t_total_eos_amount = fields.Float(string='EOS Total T-Amount', readonly=True)
    q_remain_eos_amount = fields.Float(string='EOS Remaining Q-Amount', readonly=True)
    q_total_eos_amount = fields.Float(string='EOS Total Q-Amount', readonly=True)
    record_exit = fields.Boolean(string='In Progress')
    period_year = fields.Float(string='Contract Year', readonly=True)
    period_month = fields.Float(string='Contract Month', readonly=True)
    period_day = fields.Float(string='Contract Days', readonly=True)

    end_leave_reason = fields.Char(string='Leave Reason', readonly=True)
    term_leave_reason = fields.Char(string='Leave Reason', readonly=True)
    quit_leave_reason = fields.Char(string='Leave Reason', readonly=True)
    end_years = fields.Float(string='END of Service Years', readonly=True)
    first_end = fields.Float(string='Upto 2 Years', readonly=True)
    second_end = fields.Float(string='From 2 - 5 Years', readonly=True)
    third_end = fields.Float(string='Above 5 Years', readonly=True)
    total_end = fields.Float(string='EOS- Total', readonly=True)

    term_years = fields.Float(string='END of Service Years', readonly=True)
    first_term = fields.Float(string='Upto 2 Years', readonly=True)
    second_term = fields.Float(string='From 2 - 5 Years', readonly=True)
    third_term = fields.Float(string='Above 5 Years', readonly=True)
    total_term = fields.Float(string='EOS- Total', readonly=True)

    quit_years = fields.Float(string='END of Service Years', readonly=True)
    first_quit = fields.Float(string='Upto 2 Years', readonly=True)
    second_quit = fields.Float(string='From 2 - 5 Years', readonly=True)
    third_quit = fields.Float(string='From 5 - 10 Years', readonly=True)
    fourth_quit = fields.Float(string='Above 10 Years', readonly=True)
    total_quit = fields.Float(string='EOS- Total', readonly=True)

    #################### EXIT / RE-ENTRY #########################

    exit_entry = fields.Boolean(string='Exit Entry', readonly=True, )
    voucher_method4 = fields.Many2one('employee.voucher.line', string='Employee Voucher Type4', readonly=True,
                                      default=lambda self: self.env['employee.voucher.line'].search(
                                          [('pay_type', '=', 'exitentry')]))
    allocated_exit_entry = fields.Float(string='Allowed Exit Entry', readonly=True)
    allocated_amount_exit_entry = fields.Float(string='Allowed Exit Entry Amount', readonly=True)
    issue_exit_entry = fields.Float(string='Issue Exit Entry',)
    issue_amount_exit_entry = fields.Float(string='Issue Exit Entry Amount', required=True,
                                           )

    deduct1 = fields.Boolean(string='Deduct 1', readonly=True, )
    voucher_method5 = fields.Many2one('employee.voucher.line', string='Employee Payment Type5', readonly=True,
                                      default=lambda self: self.env['employee.voucher.line'].search(
                                          [('pay_type', '=', 'deduct1')]))
    deduct1_amount = fields.Float(string='Amount', required=True, )
    deduct1_name = fields.Char(string='Deduct 1 Name', readonly=True)
    deduct1_desp = fields.Text(string='Description', )

    deduct2 = fields.Boolean(string='Deduct 2', readonly=True, )
    voucher_method6 = fields.Many2one('employee.voucher.line', string='Employee Voucher Type6', readonly=True,
                                      default=lambda self: self.env['employee.voucher.line'].search(
                                          [('pay_type', '=', 'deduct2')]))
    deduct2_amount = fields.Float(string='Amount', required=True, )
    deduct2_name = fields.Char(string='Deduct 2 Name', readonly=True)
    deduct2_desp = fields.Text(string='Description', )

    deduct3 = fields.Boolean(string='Deduct 3', readonly=True, )
    voucher_method7 = fields.Many2one('employee.voucher.line', string='Employee Voucher Type7', readonly=True,
                                      default=lambda self: self.env['employee.voucher.line'].search(
                                          [('pay_type', '=', 'deduct3')]))
    deduct3_amount = fields.Float(string='Amount', required=True, )
    deduct3_name = fields.Char(string='Deduct 4 Name', readonly=True)
    deduct3_desp = fields.Text(string='Description', )

    deduct4 = fields.Boolean(string='Deduct 4', readonly=True, )
    voucher_method8 = fields.Many2one('employee.voucher.line', string='Employee Voucher Type8', readonly=True,
                                      default=lambda self: self.env['employee.voucher.line'].search(
                                          [('pay_type', '=', 'deduct4')]))
    deduct4_amount = fields.Float(string='Amount', required=True,)
    deduct4_name = fields.Char(string='Deduct 4 Name', readonly=True)
    deduct4_desp = fields.Text(string='Description', )

    other1 = fields.Boolean(string='Other 1', readonly=True)
    voucher_method9 = fields.Many2one('employee.voucher.line', string='Employee Payment Type9', readonly=True,
                                      default=lambda self: self.env['employee.voucher.line'].search(
                                          [('pay_type', '=', 'other1')]))
    other1_amount = fields.Float(string='Amount', required=True, )
    other1_name = fields.Char(string='Other 1 Name', readonly=True)
    other1_desp = fields.Text(string='Description', )

    other2 = fields.Boolean(string='Other 2', readonly=True, )
    voucher_method10 = fields.Many2one('employee.voucher.line', string='Employee Voucher Type10', readonly=True,
                                       default=lambda self: self.env['employee.voucher.line'].search(
                                           [('pay_type', '=', 'other2')]))
    other2_amount = fields.Float(string='Amount', required=True, )
    other2_name = fields.Char(string='Other 2 Name', readonly=True)
    other2_desp = fields.Text(string='Description', )
    other3 = fields.Boolean(string='Other 3', readonly=True,)
    voucher_method11 = fields.Many2one('employee.voucher.line', string='Employee Voucher Type11', readonly=True,
                                       default=lambda self: self.env['employee.voucher.line'].search(
                                           [('pay_type', '=', 'other3')]))
    other3_amount = fields.Float(string='Amount', required=True,)
    other3_name = fields.Char(string='Other 3 Name', readonly=True)
    other3_desp = fields.Text(string='Description',)

    other4 = fields.Boolean(string='Other 4', readonly=True, )
    voucher_method12 = fields.Many2one('employee.voucher.line', string='Employee Voucher Type12', readonly=True,
                                       default=lambda self: self.env['employee.voucher.line'].search(
                                           [('pay_type', '=', 'other4')]))
    other4_amount = fields.Float(string='Amount', required=True,)
    other4_name = fields.Char(string='Other 4 Name', readonly=True)
    other4_desp = fields.Text(string='Description',)

    grand_total = fields.Float(string="Total Amount", compute='_compute_amount')
    payment_journal_count = fields.Integer(string='Journal Count', compute='_get_journal_count', store=False)
    submitted_by_id = fields.Many2one(
        'res.users',
        string='Submitted By',
        readonly=True,
    )
    approved_by1_id = fields.Many2one(
        'res.users',
        string='Approved By 1',
        readonly=True,
    )
    approved_by2_id = fields.Many2one(
        'res.users',
        string='Approved By 2',
        readonly=True,
    )
    submitted_date = fields.Datetime(
        'Submitted on',
        readonly=True,
    )
    approved_by1_date = fields.Datetime(
        'Approved By 1 on',
        readonly=True,
    )
    approved_by2_date = fields.Datetime(
        'Approved By 2 on',
        readonly=True,
    )

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('employee.payment.seq') or ' '
        res = super(employee_voucher, self).create(values)
        return res

    @api.onchange('deduct1')
    def onchange_deduct1(self):
        if self.deduct1:
            type_data = self.env['employee.voucher.line'].search([('pay_type', '=', 'deduct1')], order='id desc',
                                                                 limit=1)
            if type_data:
                self.deduct1_name = type_data.payment_name
        if not self.deduct1:
            self.deduct1_name = False

    @api.onchange('deduct2')
    def onchange_deduct2(self):
        if self.deduct2:
            type_data = self.env['employee.voucher.line'].search([('pay_type', '=', 'deduct2')], order='id desc',
                                                                 limit=1)
            if type_data:
                self.deduct2_name = type_data.payment_name
        if not self.deduct2:
            self.deduct2_name = False

    @api.onchange('deduct3')
    def onchange_deduct3(self):
        if self.deduct3:
            type_data = self.env['employee.voucher.line'].search([('pay_type', '=', 'deduct3')], order='id desc',
                                                                 limit=1)
            if type_data:
                self.deduct3_name = type_data.payment_name
        if not self.deduct3:
            self.deduct3_name = False

    @api.onchange('deduct4')
    def onchange_deduct4(self):
        if self.deduct4:
            type_data = self.env['employee.voucher.line'].search([('pay_type', '=', 'deduct4')], order='id desc',
                                                                 limit=1)
            if type_data:
                self.deduct4_name = type_data.payment_name
        if not self.deduct4:
            self.deduct4_name = False

    @api.onchange('other1')
    def onchange_other1(self):
        if self.other1:
            type_data = self.env['employee.voucher.line'].search([('pay_type', '=', 'other1')], order='id desc',
                                                                 limit=1)
            if type_data:
                self.other1_name = type_data.payment_name
        if not self.other1:
            self.other1_name = False

    @api.onchange('other2')
    def onchange_other2(self):
        if self.other2:
            type_data = self.env['employee.voucher.line'].search([('pay_type', '=', 'other2')], order='id desc',
                                                                 limit=1)
            if type_data:
                self.other2_name = type_data.payment_name
        if not self.other2:
            self.other2_name = False

    @api.onchange('other3')
    def onchange_other3(self):
        if self.other3:
            type_data = self.env['employee.voucher.line'].search([('pay_type', '=', 'other3')], order='id desc',
                                                                 limit=1)
            if type_data:
                self.other3_name = type_data.payment_name
        if not self.other3:
            self.other3_name = False

    @api.onchange('other4')
    def onchange_other4(self):
        if self.other4:
            type_data = self.env['employee.voucher.line'].search([('pay_type', '=', 'other4')], order='id desc',
                                                                 limit=1)
            if type_data:
                self.other4_name = type_data.payment_name
        if not self.other4:
            self.other4_name = False

    @api.onchange('no_days')
    def onchange_no_days(self):
        employee_id = self.employee_id.id
        contract_data = self.env['hr.contract'].search([('employee_id', '=', employee_id)], order='id desc', limit=1)
        emp_net = contract_data.value1 + contract_data.value2 + contract_data.value3 + contract_data.value4 + contract_data.value5 + contract_data.value6
        salary_day = emp_net / 30
        return {'value': {'salary_legal': self.no_days * salary_day}}

    def _compute_amount(self):
        res = {}
        grand_tot = []
        grand_tot_ded = []
        for payment_slip in self:
            if payment_slip.legal_leave == True:
                legal_1 = payment_slip.salary_legal
                grand_tot.append(legal_1)

            if payment_slip.ticket_leave == True:
                ticket_1 = payment_slip.issue_amount_tickets
                grand_tot.append(ticket_1)

            if payment_slip.end_service == True:
                end_1 = payment_slip.paid_amount
                grand_tot.append(end_1)

            if payment_slip.exit_entry == True:
                exit_1 = payment_slip.issue_amount_exit_entry
                grand_tot.append(exit_1)

            if payment_slip.deduct1 == True:
                deduct_1 = payment_slip.deduct1_amount
                grand_tot_ded.append(deduct_1)

            if payment_slip.deduct2 == True:
                deduct_2 = payment_slip.deduct2_amount
                grand_tot_ded.append(deduct_2)

            if payment_slip.deduct3 == True:
                deduct_3 = payment_slip.deduct3_amount
                grand_tot_ded.append(deduct_3)

            if payment_slip.deduct4 == True:
                deduct_4 = payment_slip.deduct4_amount
                grand_tot_ded.append(deduct_4)

            if payment_slip.other1 == True:
                other_1 = payment_slip.other1_amount
                grand_tot.append(other_1)

            if payment_slip.other2 == True:
                other_2 = payment_slip.other2_amount
                grand_tot.append(other_2)

            if payment_slip.other3 == True:
                other_3 = payment_slip.other3_amount
                grand_tot.append(other_3)

            if payment_slip.other4 == True:
                other_4 = payment_slip.other4_amount
                grand_tot.append(other_4)

            gad_tot = grand_tot
            gad_tot_ded = grand_tot_ded
            tay = sum(gad_tot) - sum(gad_tot_ded)

            self.grand_total = tay

    # return res

    def _get_journal_count(self):
        for record in self:
            record.payment_journal_count = self.env['account.move'].search_count([('payment_emp_id', '=', record.id)])

    def open_entries(self):
        return {
            'name': _('Journal Entries'),
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            "domain": [('payment_emp_id', '=', self.id)]
        }

    @api.onchange('import_legal')
    def on_change_import_legal(self):
        employee_id = self.employee_id.id
        contract_data = self.env['hr.contract'].search([('employee_id', '=', employee_id)], order='id desc', limit=1)
        emp_net = contract_data.value1 + contract_data.value2 + contract_data.value3 + contract_data.value4 + contract_data.value5 + contract_data.value6
        salary_day = emp_net / 30
        self.start_date = self.import_legal.request_date_from
        self.end_date = self.import_legal.request_date_to
        self.no_days = self.import_legal.number_of_days
        self.salary_legal = self.import_legal.number_of_days * salary_day
        '''return {'value': {'start_date': self.import_legal.date_from,
						'end_date': self.import_legal.date_to,
						'no_days': self.import_legal.number_of_days,
						'salary_legal': self.import_legal.number_of_days*salary_day,
						}}'''

    def get_remaining_tickets(self):
        employee_id = self.employee_id.id
        tick = self.issue_tickets
        # print("TTTTTTTTTTTT",tick)
        contract_data = self.env['hr.contract'].search([('employee_id', '=', employee_id)], order='id desc', limit=1)
        # print("EEEEEEEEEEEEEEEEEEE",contract_data)
        remain_tick = contract_data.ticket_balance
        # print("RRRRRRRRRRRRR",remain_tick)
        return contract_data.write({'ticket_balance': (remain_tick - tick)})

    def get_remaining_exit_entry(self):
        exit_entry = self.issue_exit_entry
        employee_id = self.employee_id.id
        contract_data = self.env['hr.contract'].search([('employee_id', '=', employee_id)], order='id desc', limit=1)
        # print"EEEEEEEEEEEEEEEEEEE",contract_data
        remain_exit_entry = contract_data.exit_entry_balance
        # print"RRRRRRRRRRRRR",remain_exit_entry
        return contract_data.write({'exit_entry_balance': (remain_exit_entry - exit_entry)})

    def getting_remaining_days(self):
        type_obj = self.env['hr.leave.type']
        holiday_obj = self.env['hr.leave']
        for payment_slip in self:
            date_format = '%Y-%m-%d'
            current_date = fields.datetime.now().strftime(date_format)
            d1 = fields.Datetime.from_string(current_date) - relativedelta.relativedelta(years=8)
            # print ("CDCDCDCDCDDCDCDCDCDCDCDCDCDC",d1)
            add1 = d1 + relativedelta.relativedelta(days=payment_slip.no_days)
            # print ("EDEDEDEDEDEDEDEDEEDEDEDEDEDEDED",add1)
            status = type_obj.search([('name', '=', 'LegalLeaves')], order='id desc', limit=1)
            print("EDEDEDEDEDEDEDEDEEDEDEDEDEDEDED", status)
            # if not status:
            # continue
            leave = holiday_obj.create(
                {'name': 'Paid Legalleaves', 'employee_id': payment_slip.employee_id.id, 'holiday_status_id': status.id,
                 'date_from': d1, 'date_to': add1, 'holiday_type': 'employee', 'number_of_days': payment_slip.no_days,
                 'voucher_ref': payment_slip.id})
            # print ("EDEDEDEDEDEDEDEDEEDEDEDEDEDEDED",leave)
            leave.action_approve()
            leave.action_validate()
            return True

    def getting_legal_days(self):
        if self.import_legal:
            self.import_legal.voucher_paid = True

    def set_draft(self):
        self.write({'state': 'draft'})
        return True

    def button_submit(self):
        for payment in self:
            payment.write({
                'state': 'submitted',
                'submitted_by_id': self.env.user.id,
                'submitted_date': fields.Datetime.now(),
            })

    def approve1_payment(self):
        ticket_amt = 0.0
        exit_entry_amt = 0.0
        import_legal = self.import_legal.id
        employee_id = self.employee_id.id
        emp_voucher_ids = self.env['employee.voucher'].search(
            [('import_legal', '=', import_legal), ('employee_id', '=', employee_id), ('state', '=', 'done')])
        # print "PPPPPPPPPPPPPPPPPPPP",emp_voucher_ids
        if self.legal_leave == True:
            if self.select_leave == 'paid':
                self.write({'import_legal': False, 'start_date': False, 'end_date': False, 'state': 'confirm'})
            elif len(emp_voucher_ids) < 1:
                self.write({'state': 'confirm'})
        # elif len(emp_voucher_ids) >= 1:
        # raise UserError(_('Selected Legal Leave has been selected by Another Entry, Now you cannot select it again, Legal Leave. must be UNIQUE!'))

        if self.legal_leave == False:
            self.write(
                {'import_legal': False, 'start_date': False, 'end_date': False, 'no_days': False, 'salary_legal': False,
                 'state': 'confirm'})

        if self.ticket_leave == True:
            self.write({'state': 'confirm'})

        if self.ticket_leave == False:
            self.write({'issue_tickets': False, 'issue_amount_tickets': False, 'state': 'confirm'})

        if self.exit_entry == True:
            self.write({'state': 'confirm'})

        if self.exit_entry == False:
            self.write({'issue_exit_entry': False, 'issue_amount_exit_entry': False, 'state': 'confirm'})

        if self.end_service == True:
            if self.leave_reason == "endservice":
                if self.paid_amount > round(self.e_total_eos_amount - self.paid_eos_amount):
                    bal = round(self.e_total_eos_amount - self.paid_eos_amount)
                    # raise UserError(_('Paying Amount %s is More than Remaining Balance Amount "%s"')% (self.paid_amount,bal))
                    raise UserError(_('Paying Amount is More than Remaining Balance Amount'))
            if self.leave_reason == "termination":
                if self.paid_amount > round(self.t_total_eos_amount - self.paid_eos_amount):
                    raise UserError(_('Paying Amount is More than Remaining Balance Amount'))
            if self.leave_reason == "quit":
                if self.paid_amount > round(self.q_total_eos_amount - self.paid_eos_amount):
                    raise UserError(_('Paying Amount is More than Remaining Balance Amount'))
            else:
                self.write({'state': 'confirm'})

        if self.end_service == False:
            self.write({'paid_amount': False, 'state': 'confirm'})
        else:
            self.write({'state': 'confirm'})
        self.write({
            'approved_by1_id': self.env.user.id,
            'approved_by1_date': fields.Datetime.now(),
        })
        return True

    ################## Voucher Cancel Functions ############################################################

    def get_inv_remaining_tickets(self):
        for move in self:
            tick = move.issue_tickets
            # print"TTTTTTTTTTTT",tick
            employee_id = move.employee_id.id
            contract_data = self.env['hr.contract'].search([('employee_id', '=', employee_id)], order='id desc',
                                                           limit=1)
            # print"EEEEEEEEEEEEEEEEEEE",contract_data
            remain_tick = contract_data.ticket_balance
        # print"RRRRRRRRRRRRR",remain_tick
        return contract_data.write({'ticket_balance': remain_tick + tick})

    def get_inv_remaining_exit_entry(self):
        for move in self:
            exit_entry = move.issue_exit_entry
            # print"EEEEEEEEEEEEEEEEEEE",exit_entry
            employee_id = move.employee_id.id
            contract_data = self.env['hr.contract'].search([('employee_id', '=', employee_id)], order='id desc',
                                                           limit=1)
            # print"EEEEEEEEEEEEEEEEEEE",contract_data
            remain_exit_entry = contract_data.exit_entry_balance
        # print"RRRRRRRRRRRRR",remain_exit_entry
        return contract_data.write({'exit_entry_balance': remain_exit_entry + exit_entry})

    def getting_inv_legal_days(self):
        if self.import_legal:
            self.import_legal.voucher_paid = False

    def getting_inv_remaining_days(self):
        type_obj = self.env['hr.leave.type']
        holiday_obj = self.env['hr.leave']
        for payment_slip in self:
            employee_id = payment_slip.employee_id.id
            emp_holidays_ids = holiday_obj.search(
                [('employee_id', '=', employee_id), ('state', '=', 'validate'), ('name', '=', 'Paid Legalleaves'),
                 ('voucher_ref', '=', payment_slip.id)])
            # print "VOVOVOVOVOVOVVVOVOVOOVVO",emp_holidays_ids
            emp_holidays_ids.write({'state': 'draft'})
            emp_holidays_ids.unlink()

    def unlink(self):
        for vou in self:
            vouch_ids = self.env['account.move'].search([('payment_emp_id', '=', vou.id)])
            # if expense.state in ['post', 'done']:
            if vouch_ids:
                raise UserError(_('You Cant Delete Employee Voucher that have Journal Entries.'))
        super(employee_voucher, self).unlink()

    def draft_payment(self):
        self.write({'state': 'draft'})
        return True

    def cancel_voucher(self):
        move_pool = self.env['account.move']
        timenow = time.strftime('%Y-%m-%d')
        holiday_obj = self.env['hr.leave']
        for payment_slip in self:
            line_ids = []
            grand_tot = []
            grand_tot_ded = []
            # prepare account move data
            name = _('Inverse: Employee Voucher for ') + (payment_slip.employee_id.name)
            move = {
                'narration': name,
                'date': timenow,
                'payment_emp_id': payment_slip.id,
                'journal_id': payment_slip.journal_id.id,
            }
            # print "MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM",move
            amount1 = payment_slip.salary_legal
            debit_account_id1 = payment_slip.voucher_method1.debit_account_id.id or False
            credit_account_id1 = payment_slip.voucher_method1.credit_account_id.id or False
            # analytic_account_id = payment_slip.payment_method.analytic_account_id.id or False

            if payment_slip.legal_leave == True:
                if payment_slip.select_leave == 'paid':
                    remain_days = self.getting_inv_remaining_days()
                if payment_slip.select_leave == 'legal':
                    remain_days = self.getting_inv_legal_days()
                if payment_slip.voucher_method1.account_analytic_true == True:
                    legal_analytic = payment_slip.employee_id.analytic_account_id and payment_slip.employee_id.analytic_account_id.id or False
                    if debit_account_id1:
                        debit_line1 = (0, 0, {
                            'name': payment_slip.voucher_method1.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id1,
                            'debit': 0.0,
                            'credit': amount1,
                            'analytic_account_id': legal_analytic or False,
                        })
                        line_ids.append(debit_line1)

                    if credit_account_id1:
                        credit_line1 = (0, 0, {
                            'name': payment_slip.voucher_method1.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id1,
                            'debit': amount1,
                            'credit': 0.0,

                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line1)
                else:
                    if debit_account_id1:
                        debit_line1 = (0, 0, {
                            'name': payment_slip.voucher_method1.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id1,
                            'debit': 0.0,
                            'credit': amount1,
                            'analytic_account_id': False,
                        })
                        line_ids.append(debit_line1)

                    if credit_account_id1:
                        credit_line1 = (0, 0, {
                            'name': payment_slip.voucher_method1.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id1,
                            'debit': amount1,
                            'credit': 0.0,

                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line1)

            amount2 = payment_slip.issue_amount_tickets
            debit_account_id2 = payment_slip.voucher_method2.debit_account_id.id or False
            credit_account_id2 = payment_slip.voucher_method2.credit_account_id.id or False

            if payment_slip.ticket_leave == True:
                inv_remain_tick = self.get_inv_remaining_tickets()
                if payment_slip.voucher_method2.account_analytic_true == True:
                    ticket_analytic = payment_slip.employee_id.analytic_account_id and payment_slip.employee_id.analytic_account_id.id or False
                    if debit_account_id2:
                        debit_line2 = (0, 0, {
                            'name': payment_slip.voucher_method2.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id2,
                            'debit': 0.0,
                            'credit': amount2,
                            'analytic_account_id': ticket_analytic or False,
                        })
                        line_ids.append(debit_line2)

                    if credit_account_id2:
                        credit_line2 = (0, 0, {
                            'name': payment_slip.voucher_method2.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id2,
                            'debit': amount2,
                            'credit': 0.0,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line2)
                else:
                    if debit_account_id2:
                        debit_line2 = (0, 0, {
                            'name': payment_slip.voucher_method2.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id2,
                            'debit': 0.0,
                            'credit': amount2,
                            'analytic_account_id': False,
                        })
                        line_ids.append(debit_line2)

                    if credit_account_id2:
                        credit_line2 = (0, 0, {
                            'name': payment_slip.voucher_method2.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id2,
                            'debit': amount2,
                            'credit': 0.0,

                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line2)

            amount3 = payment_slip.paid_amount
            debit_account_id3 = payment_slip.voucher_method3.debit_account_id.id or False
            credit_account_id3 = payment_slip.voucher_method3.credit_account_id.id or False

            if payment_slip.end_service == True:
                employee_id = payment_slip.employee_id.id
                emp_voucher_ids = self.env['employee.voucher'].search(
                    [('employee_id', '=', employee_id), ('end_service', '=', True), ('state', '=', 'done')],
                    order='id desc', limit=1)
                #   print "VOVOVOVOVOVOVVVOVOVOOVVO",emp_voucher_ids
                if payment_slip.id != emp_voucher_ids:
                    raise UserError(_('You cannot refuse paid EOS Employee voucher'))

                if payment_slip.voucher_method3.account_analytic_true == True:
                    end_service_analytic = payment_slip.employee_id.analytic_account_id and payment_slip.employee_id.analytic_account_id.id or False
                    if debit_account_id3:
                        debit_line3 = (0, 0, {
                            'name': payment_slip.voucher_method3.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id3,
                            'debit': 0.0,
                            'credit': amount3,
                            'analytic_account_id': end_service_analytic or False,
                        })
                        line_ids.append(debit_line3)

                    if credit_account_id3:
                        credit_line3 = (0, 0, {
                            'name': payment_slip.voucher_method3.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id3,
                            'debit': amount3,
                            'credit': 0.0,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line3)
                else:
                    if debit_account_id3:
                        debit_line3 = (0, 0, {
                            'name': payment_slip.voucher_method3.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id3,
                            'debit': 0.0,
                            'credit': amount3,
                            'analytic_account_id': False,
                        })
                        line_ids.append(debit_line3)

                    if credit_account_id3:
                        credit_line3 = (0, 0, {
                            'name': payment_slip.voucher_method3.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id3,
                            'debit': amount3,
                            'credit': 0.0,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line3)

            amount4 = payment_slip.issue_amount_exit_entry
            debit_account_id4 = payment_slip.voucher_method4.debit_account_id.id or False
            credit_account_id4 = payment_slip.voucher_method4.credit_account_id.id or False

            if payment_slip.exit_entry == True:
                inv_remain_exit_entry = self.get_inv_remaining_exit_entry()
                if payment_slip.voucher_method4.account_analytic_true == True:
                    exit_entry_analytic = payment_slip.employee_id.analytic_account_id and payment_slip.employee_id.analytic_account_id.id or False
                    if debit_account_id4:
                        debit_line4 = (0, 0, {
                            'name': payment_slip.voucher_method4.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id4,
                            'debit': 0.0,
                            'credit': amount4,
                            'analytic_account_id': exit_entry_analytic or False,
                        })
                        line_ids.append(debit_line4)

                    if credit_account_id4:
                        credit_line4 = (0, 0, {
                            'name': payment_slip.voucher_method4.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id4,
                            'debit': amount4,
                            'credit': 0.0,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line4)
                else:
                    if debit_account_id4:
                        debit_line4 = (0, 0, {
                            'name': payment_slip.voucher_method4.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id4,
                            'debit': 0.0,
                            'credit': amount4,
                            'analytic_account_id': False,
                        })
                        line_ids.append(debit_line4)

                    if credit_account_id4:
                        credit_line4 = (0, 0, {
                            'name': payment_slip.voucher_method4.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id4,
                            'debit': amount4,
                            'credit': 0.0,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line4)

            amount5 = payment_slip.deduct1_amount
            debit_account_id5 = payment_slip.voucher_method5.debit_account_id.id or False
            credit_account_id5 = payment_slip.voucher_method5.credit_account_id.id or False

            if payment_slip.deduct1 == True:

                if payment_slip.voucher_method5.account_analytic_true == True:
                    deduct1_analytic = payment_slip.employee_id.analytic_account_id and payment_slip.employee_id.analytic_account_id.id or False
                    if debit_account_id5:
                        debit_line5 = (0, 0, {
                            'name': payment_slip.voucher_method5.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id5,
                            'debit': 0.0,
                            'credit': amount5,
                            # 'analytic_account_id': analytic_account_id,
                        })
                        line_ids.append(debit_line5)

                    if credit_account_id5:
                        credit_line5 = (0, 0, {
                            'name': payment_slip.voucher_method5.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id5,
                            'debit': amount5,
                            'credit': 0.0,
                            'analytic_account_id': deduct1_analytic or False,
                        })
                        line_ids.append(credit_line5)
                else:
                    if debit_account_id5:
                        debit_line5 = (0, 0, {
                            'name': payment_slip.voucher_method5.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id5,
                            'debit': 0.0,
                            'credit': amount5,
                            # 'analytic_account_id': analytic_account_id,
                        })
                        line_ids.append(debit_line5)

                    if credit_account_id5:
                        credit_line5 = (0, 0, {
                            'name': payment_slip.voucher_method5.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id5,
                            'debit': amount5,
                            'credit': 0.0,
                            'analytic_account_id': False,
                        })
                        line_ids.append(credit_line5)

            amount6 = payment_slip.deduct2_amount
            debit_account_id6 = payment_slip.voucher_method6.debit_account_id.id or False
            credit_account_id6 = payment_slip.voucher_method6.credit_account_id.id or False

            if payment_slip.deduct2 == True:

                if payment_slip.voucher_method6.account_analytic_true == True:
                    deduct2_analytic = payment_slip.employee_id.analytic_account_id and payment_slip.employee_id.analytic_account_id.id or False
                    if debit_account_id6:
                        debit_line6 = (0, 0, {
                            'name': payment_slip.voucher_method6.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id6,
                            'debit': 0.0,
                            'credit': amount6,
                            # 'analytic_account_id': analytic_account_id,
                        })
                        line_ids.append(debit_line6)

                    if credit_account_id6:
                        credit_line6 = (0, 0, {
                            'name': payment_slip.voucher_method6.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id6,
                            'debit': amount6,
                            'credit': 0.0,
                            'analytic_account_id': deduct2_analytic or False,
                        })
                        line_ids.append(credit_line6)
                else:
                    if debit_account_id6:
                        debit_line6 = (0, 0, {
                            'name': payment_slip.voucher_method6.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id6,
                            'debit': 0.0,
                            'credit': amount6,
                            # 'analytic_account_id': analytic_account_id,
                        })
                        line_ids.append(debit_line6)

                    if credit_account_id6:
                        credit_line6 = (0, 0, {
                            'name': payment_slip.voucher_method6.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id6,
                            'debit': amount6,
                            'credit': 0.0,
                            'analytic_account_id': False,
                        })
                        line_ids.append(credit_line6)

            amount7 = payment_slip.deduct3_amount
            debit_account_id7 = payment_slip.voucher_method7.debit_account_id.id or False
            credit_account_id7 = payment_slip.voucher_method7.credit_account_id.id or False

            if payment_slip.deduct3 == True:

                if payment_slip.voucher_method7.account_analytic_true == True:
                    deduct3_analytic = payment_slip.employee_id.analytic_account_id and payment_slip.employee_id.analytic_account_id.id or False
                    if debit_account_id7:
                        debit_line7 = (0, 0, {
                            'name': payment_slip.voucher_method7.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id7,
                            'debit': 0.0,
                            'credit': amount7,
                            # 'analytic_account_id': analytic_account_id,
                        })
                        line_ids.append(debit_line7)

                    if credit_account_id7:
                        credit_line7 = (0, 0, {
                            'name': payment_slip.voucher_method7.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id7,
                            'debit': amount7,
                            'credit': 0.0,
                            'analytic_account_id': deduct3_analytic or False,
                        })
                        line_ids.append(credit_line7)
                else:
                    if debit_account_id7:
                        debit_line7 = (0, 0, {
                            'name': payment_slip.voucher_method7.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id7,
                            'debit': 0.0,
                            'credit': amount7,
                            # 'analytic_account_id': analytic_account_id,
                        })
                        line_ids.append(debit_line7)

                    if credit_account_id7:
                        credit_line7 = (0, 0, {
                            'name': payment_slip.voucher_method7.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id7,
                            'debit': amount7,
                            'credit': 0.0,
                            'analytic_account_id': False,
                        })
                        line_ids.append(credit_line7)

            amount8 = payment_slip.deduct4_amount
            debit_account_id8 = payment_slip.voucher_method8.debit_account_id.id or False
            credit_account_id8 = payment_slip.voucher_method8.credit_account_id.id or False

            if payment_slip.deduct4 == True:

                if payment_slip.voucher_method8.account_analytic_true == True:
                    deduct4_analytic = payment_slip.employee_id.analytic_account_id and payment_slip.employee_id.analytic_account_id.id or False
                    if debit_account_id8:
                        debit_line8 = (0, 0, {
                            'name': payment_slip.voucher_method8.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id8,
                            'debit': 0.0,
                            'credit': amount8,
                            # 'analytic_account_id': analytic_account_id,
                        })
                        line_ids.append(debit_line8)

                    if credit_account_id8:
                        credit_line8 = (0, 0, {
                            'name': payment_slip.voucher_method8.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id8,
                            'debit': amount8,
                            'credit': 0.0,
                            'analytic_account_id': deduct4_analytic or False,
                        })
                        line_ids.append(credit_line8)
                else:
                    if debit_account_id8:
                        debit_line8 = (0, 0, {
                            'name': payment_slip.voucher_method8.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id8,
                            'debit': 0.0,
                            'credit': amount8,
                            # 'analytic_account_id': analytic_account_id,
                        })
                        line_ids.append(debit_line8)

                    if credit_account_id8:
                        credit_line8 = (0, 0, {
                            'name': payment_slip.voucher_method8.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id8,
                            'debit': amount8,
                            'credit': 0.0,
                            'analytic_account_id': False,
                        })
                        line_ids.append(credit_line8)

            amount9 = payment_slip.other1_amount
            debit_account_id9 = payment_slip.voucher_method9.debit_account_id.id or False
            credit_account_id9 = payment_slip.voucher_method9.credit_account_id.id or False

            if payment_slip.other1 == True:

                if payment_slip.voucher_method9.account_analytic_true == True:
                    other1_analytic = payment_slip.employee_id.analytic_account_id and payment_slip.employee_id.analytic_account_id.id or False
                    if debit_account_id9:
                        debit_line9 = (0, 0, {
                            'name': payment_slip.voucher_method9.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id9,
                            'debit': 0.0,
                            'credit': amount9,
                            'analytic_account_id': other1_analytic or False,
                        })
                        line_ids.append(debit_line9)

                    if credit_account_id9:
                        credit_line9 = (0, 0, {
                            'name': payment_slip.voucher_method9.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id9,
                            'debit': amount9,
                            'credit': 0.0,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line9)
                else:
                    if debit_account_id9:
                        debit_line9 = (0, 0, {
                            'name': payment_slip.voucher_method9.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id9,
                            'debit': 0.0,
                            'credit': amount9,
                            'analytic_account_id': False,
                        })
                        line_ids.append(debit_line9)

                    if credit_account_id9:
                        credit_line9 = (0, 0, {
                            'name': payment_slip.voucher_method9.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id9,
                            'debit': amount9,
                            'credit': 0.0,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line9)

            amount10 = payment_slip.other2_amount
            debit_account_id10 = payment_slip.voucher_method10.debit_account_id.id or False
            credit_account_id10 = payment_slip.voucher_method10.credit_account_id.id or False

            if payment_slip.other2 == True:

                if payment_slip.voucher_method10.account_analytic_true == True:
                    other2_analytic = payment_slip.employee_id.analytic_account_id and payment_slip.employee_id.analytic_account_id.id or False
                    if debit_account_id10:
                        debit_line10 = (0, 0, {
                            'name': payment_slip.voucher_method10.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id10,
                            'debit': 0.0,
                            'credit': amount10,
                            'analytic_account_id': other2_analytic or False,
                        })
                        line_ids.append(debit_line10)

                    if credit_account_id10:
                        credit_line10 = (0, 0, {
                            'name': payment_slip.voucher_method10.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id10,
                            'debit': amount10,
                            'credit': 0.0,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line10)
                else:
                    if debit_account_id10:
                        debit_line10 = (0, 0, {
                            'name': payment_slip.voucher_method10.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id10,
                            'debit': 0.0,
                            'credit': amount10,
                            'analytic_account_id': False,
                        })
                        line_ids.append(debit_line10)

                    if credit_account_id10:
                        credit_line10 = (0, 0, {
                            'name': payment_slip.voucher_method10.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id10,
                            'debit': amount10,
                            'credit': 0.0,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line10)

            amount11 = payment_slip.other3_amount
            debit_account_id11 = payment_slip.voucher_method11.debit_account_id.id or False
            credit_account_id11 = payment_slip.voucher_method11.credit_account_id.id or False

            if payment_slip.other3 == True:

                if payment_slip.voucher_method11.account_analytic_true == True:
                    other3_analytic = payment_slip.employee_id.analytic_account_id and payment_slip.employee_id.analytic_account_id.id or False
                    if debit_account_id11:
                        debit_line11 = (0, 0, {
                            'name': payment_slip.voucher_method11.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id11,
                            'debit': 0.0,
                            'credit': amount11,
                            'analytic_account_id': other3_analytic or False,
                        })
                        line_ids.append(debit_line11)

                    if credit_account_id11:
                        credit_line11 = (0, 0, {
                            'name': payment_slip.voucher_method11.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id11,
                            'debit': amount11,
                            'credit': 0.0,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line11)
                else:
                    if debit_account_id11:
                        debit_line11 = (0, 0, {
                            'name': payment_slip.voucher_method11.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id11,
                            'debit': 0.0,
                            'credit': amount11,
                            'analytic_account_id': False,
                        })
                        line_ids.append(debit_line11)

                    if credit_account_id11:
                        credit_line11 = (0, 0, {
                            'name': payment_slip.voucher_method11.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id11,
                            'debit': amount11,
                            'credit': 0.0,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line11)

            amount12 = payment_slip.other4_amount
            debit_account_id12 = payment_slip.voucher_method12.debit_account_id.id or False
            credit_account_id12 = payment_slip.voucher_method12.credit_account_id.id or False

            if payment_slip.other4 == True:

                if payment_slip.voucher_method12.account_analytic_true == True:
                    other4_analytic = payment_slip.employee_id.analytic_account_id and payment_slip.employee_id.analytic_account_id.id or False
                    if debit_account_id12:
                        debit_line12 = (0, 0, {
                            'name': payment_slip.voucher_method12.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id12,
                            'debit': 0.0,
                            'credit': amount12,
                            'analytic_account_id': other4_analytic or False,
                        })
                        line_ids.append(debit_line12)

                    if credit_account_id12:
                        credit_line12 = (0, 0, {
                            'name': payment_slip.voucher_method12.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id12,
                            'debit': amount12,
                            'credit': 0.0,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line12)
                else:
                    if debit_account_id12:
                        debit_line12 = (0, 0, {
                            'name': payment_slip.voucher_method12.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id12,
                            'debit': 0.0,
                            'credit': amount12,
                            'analytic_account_id': False,
                        })
                        line_ids.append(debit_line12)

                    if credit_account_id12:
                        credit_line12 = (0, 0, {
                            'name': payment_slip.voucher_method12.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id12,
                            'debit': amount12,
                            'credit': 0.0,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line12)

            move.update({'line_ids': line_ids})
            move_id = move_pool.create(move)
            # print "MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM",move_id
            self.write({'move_id': move_id.id, 'state': 'cancel'})
            move_id.post()
            return True

    ################## Voucher Cancel Functions ############################################################

    def approve2_payment(self):
        move_pool = self.env['account.move']
        timenow = time.strftime('%Y-%m-%d')
        holiday_obj = self.env['hr.leave']
        for payment_slip in self:
            employee_id = payment_slip.employee_id.id
            if payment_slip.balance_laon != 0.0 and payment_slip.ignore_loan == False:
                raise UserError(_('This Employee has Balance Loan Amount, You cannot confirm this Voucher'))
            line_ids = []
            grand_tot = []
            grand_tot_ded = []

            # prepare account move data
            name = _('Employee Voucher for ') + (payment_slip.employee_id.name)
            move = {
                'narration': name,
                'date': timenow,
                'payment_emp_id': payment_slip.id,
                'journal_id': payment_slip.journal_id.id,
            }
            # print ("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM",move)

            amount1 = payment_slip.salary_legal
            debit_account_id1 = payment_slip.voucher_method1.debit_account_id.id or False
            credit_account_id1 = payment_slip.voucher_method1.credit_account_id.id or False
            # analytic_account_id = payment_slip.payment_method.analytic_account_id.id or False

            if payment_slip.legal_leave == True:
                legal_1 = payment_slip.salary_legal
                grand_tot.append(legal_1)
                if payment_slip.select_leave == 'paid':
                    remain_days = self.getting_remaining_days()
                if payment_slip.select_leave == 'legal':
                    remain_days = self.getting_legal_days()
                leave_check = self.approve1_payment()
                if payment_slip.voucher_method1.account_analytic_true == True:
                    legal_analytic = payment_slip.employee_id.analytic_account_id and payment_slip.employee_id.analytic_account_id.id or False
                    if debit_account_id1:
                        debit_line1 = (0, 0, {
                            'name': payment_slip.voucher_method1.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id1,
                            'debit': amount1,
                            'credit': 0.0,
                            'analytic_account_id': legal_analytic or False,
                        })
                        line_ids.append(debit_line1)

                    if credit_account_id1:
                        credit_line1 = (0, 0, {
                            'name': payment_slip.voucher_method1.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id1,
                            'debit': 0.0,
                            'credit': amount1,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line1)
                else:
                    if debit_account_id1:
                        debit_line1 = (0, 0, {
                            'name': payment_slip.voucher_method1.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id1,
                            'debit': amount1,
                            'credit': 0.0,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(debit_line1)

                    if credit_account_id1:
                        credit_line1 = (0, 0, {
                            'name': payment_slip.voucher_method1.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id1,
                            'debit': 0.0,
                            'credit': amount1,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line1)

            amount2 = payment_slip.issue_amount_tickets
            debit_account_id2 = payment_slip.voucher_method2.debit_account_id.id or False
            credit_account_id2 = payment_slip.voucher_method2.credit_account_id.id or False

            if payment_slip.ticket_leave == True:
                ticket_1 = payment_slip.issue_amount_tickets
                grand_tot.append(ticket_1)
                remain_tick = self.get_remaining_tickets()
                if payment_slip.voucher_method2.account_analytic_true == True:
                    ticket_analytic = payment_slip.employee_id.analytic_account_id and payment_slip.employee_id.analytic_account_id.id or False
                    if debit_account_id2:
                        debit_line2 = (0, 0, {
                            'name': payment_slip.voucher_method2.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id2,
                            'debit': amount2,
                            'credit': 0.0,
                            'analytic_account_id': ticket_analytic or False,
                        })
                        line_ids.append(debit_line2)

                    if credit_account_id2:
                        credit_line2 = (0, 0, {
                            'name': payment_slip.voucher_method2.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id2,
                            'debit': 0.0,
                            'credit': amount2,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line2)
                else:
                    if debit_account_id2:
                        debit_line2 = (0, 0, {
                            'name': payment_slip.voucher_method2.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id2,
                            'debit': amount2,
                            'credit': 0.0,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(debit_line2)

                    if credit_account_id2:
                        credit_line2 = (0, 0, {
                            'name': payment_slip.voucher_method2.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id2,
                            'debit': 0.0,
                            'credit': amount2,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line2)

            amount3 = payment_slip.paid_amount
            debit_account_id3 = payment_slip.voucher_method3.debit_account_id.id or False
            credit_account_id3 = payment_slip.voucher_method3.credit_account_id.id or False

            if payment_slip.end_service == True:
                end_1 = payment_slip.paid_amount
                grand_tot.append(end_1)
                if payment_slip.voucher_method3.account_analytic_true == True:
                    end_service_analytic = payment_slip.employee_id.analytic_account_id and payment_slip.employee_id.analytic_account_id.id or False
                    if debit_account_id3:
                        debit_line3 = (0, 0, {
                            'name': payment_slip.voucher_method3.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id3,
                            'debit': amount3,
                            'credit': 0.0,
                            'analytic_account_id': end_service_analytic or False,
                        })
                        line_ids.append(debit_line3)

                    if credit_account_id3:
                        credit_line3 = (0, 0, {
                            'name': payment_slip.voucher_method3.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id3,
                            'debit': 0.0,
                            'credit': amount3,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line3)

                else:
                    if debit_account_id3:
                        debit_line3 = (0, 0, {
                            'name': payment_slip.voucher_method3.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id3,
                            'debit': amount3,
                            'credit': 0.0,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(debit_line3)

                    if credit_account_id3:
                        credit_line3 = (0, 0, {
                            'name': payment_slip.voucher_method3.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id3,
                            'debit': 0.0,
                            'credit': amount3,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line3)

            amount4 = payment_slip.issue_amount_exit_entry
            debit_account_id4 = payment_slip.voucher_method4.debit_account_id.id or False
            credit_account_id4 = payment_slip.voucher_method4.credit_account_id.id or False

            if payment_slip.exit_entry == True:
                exit_1 = payment_slip.issue_amount_exit_entry
                grand_tot.append(exit_1)
                if payment_slip.issue_exit_entry > payment_slip.allocated_exit_entry:
                    raise UserError(_('No Sufficent Exit Entry Balance for this Employee'))
                remain_exit_entry = self.get_remaining_exit_entry()
                if payment_slip.voucher_method4.account_analytic_true == True:
                    exit_entry_analytic = payment_slip.employee_id.analytic_account_id and payment_slip.employee_id.analytic_account_id.id or False
                    if debit_account_id4:
                        debit_line4 = (0, 0, {
                            'name': payment_slip.voucher_method4.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id4,
                            'debit': amount4,
                            'credit': 0.0,
                            'analytic_account_id': exit_entry_analytic or False,
                        })
                        line_ids.append(debit_line4)

                    if credit_account_id4:
                        credit_line4 = (0, 0, {
                            'name': payment_slip.voucher_method4.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id4,
                            'debit': 0.0,
                            'credit': amount4,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line4)
                else:
                    if debit_account_id4:
                        debit_line4 = (0, 0, {
                            'name': payment_slip.voucher_method4.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id4,
                            'debit': amount4,
                            'credit': 0.0,
                            'analytic_account_id': False,
                        })
                        line_ids.append(debit_line4)

                    if credit_account_id4:
                        credit_line4 = (0, 0, {
                            'name': payment_slip.voucher_method4.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id4,
                            'debit': 0.0,
                            'credit': amount4,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line4)

            amount5 = payment_slip.deduct1_amount
            debit_account_id5 = payment_slip.voucher_method5.debit_account_id.id or False
            credit_account_id5 = payment_slip.voucher_method5.credit_account_id.id or False

            if payment_slip.deduct1 == True:
                deduct_1 = payment_slip.deduct1_amount
                grand_tot_ded.append(deduct_1)
                if payment_slip.voucher_method5.account_analytic_true == True:
                    deduct1_analytic = payment_slip.employee_id.analytic_account_id and payment_slip.employee_id.analytic_account_id.id or False
                    if debit_account_id5:
                        debit_line5 = (0, 0, {
                            'name': payment_slip.voucher_method5.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id5,
                            'debit': amount5,
                            'credit': 0.0,
                            # 'analytic_account_id': analytic_account_id,
                        })
                        line_ids.append(debit_line5)

                    if credit_account_id5:
                        credit_line5 = (0, 0, {
                            'name': payment_slip.voucher_method5.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id5,
                            'debit': 0.0,
                            'credit': amount5,
                            'analytic_account_id': deduct1_analytic or False,
                        })
                        line_ids.append(credit_line5)
                else:
                    if debit_account_id5:
                        debit_line5 = (0, 0, {
                            'name': payment_slip.voucher_method5.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id5,
                            'debit': amount5,
                            'credit': 0.0,
                            # 'analytic_account_id': analytic_account_id,
                        })
                        line_ids.append(debit_line5)

                    if credit_account_id5:
                        credit_line5 = (0, 0, {
                            'name': payment_slip.voucher_method5.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id5,
                            'debit': 0.0,
                            'credit': amount5,
                            'analytic_account_id': False,
                        })
                        line_ids.append(credit_line5)

            amount6 = payment_slip.deduct2_amount
            debit_account_id6 = payment_slip.voucher_method6.debit_account_id.id or False
            credit_account_id6 = payment_slip.voucher_method6.credit_account_id.id or False

            if payment_slip.deduct2 == True:
                deduct_2 = payment_slip.deduct2_amount
                grand_tot_ded.append(deduct_2)
                if payment_slip.voucher_method6.account_analytic_true == True:
                    deduct2_analytic = payment_slip.employee_id.analytic_account_id and payment_slip.employee_id.analytic_account_id.id or False
                    if debit_account_id6:
                        debit_line6 = (0, 0, {
                            'name': payment_slip.voucher_method6.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id6,
                            'debit': amount6,
                            'credit': 0.0,
                            # 'analytic_account_id': analytic_account_id,
                        })
                        line_ids.append(debit_line6)

                    if credit_account_id6:
                        credit_line6 = (0, 0, {
                            'name': payment_slip.voucher_method6.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id6,
                            'debit': 0.0,
                            'credit': amount6,
                            'analytic_account_id': deduct2_analytic or False,
                        })
                        line_ids.append(credit_line6)
                else:
                    if debit_account_id6:
                        debit_line6 = (0, 0, {
                            'name': payment_slip.voucher_method6.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id6,
                            'debit': amount6,
                            'credit': 0.0,
                            # 'analytic_account_id': analytic_account_id,
                        })
                        line_ids.append(debit_line6)

                    if credit_account_id6:
                        credit_line6 = (0, 0, {
                            'name': payment_slip.voucher_method6.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id6,
                            'debit': 0.0,
                            'credit': amount6,
                            'analytic_account_id': False,
                        })
                        line_ids.append(credit_line6)

            amount7 = payment_slip.deduct3_amount
            debit_account_id7 = payment_slip.voucher_method7.debit_account_id.id or False
            credit_account_id7 = payment_slip.voucher_method7.credit_account_id.id or False

            if payment_slip.deduct3 == True:
                deduct_3 = payment_slip.deduct3_amount
                grand_tot_ded.append(deduct_3)
                if payment_slip.voucher_method7.account_analytic_true == True:
                    deduct3_analytic = payment_slip.employee_id.analytic_account_id and payment_slip.employee_id.analytic_account_id.id or False
                    if debit_account_id7:
                        debit_line7 = (0, 0, {
                            'name': payment_slip.voucher_method7.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id7,
                            'debit': amount7,
                            'credit': 0.0,
                            # 'analytic_account_id': analytic_account_id,
                        })
                        line_ids.append(debit_line7)

                    if credit_account_id7:
                        credit_line7 = (0, 0, {
                            'name': payment_slip.voucher_method7.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id7,
                            'debit': 0.0,
                            'credit': amount7,
                            'analytic_account_id': deduct3_analytic or False,
                        })
                        line_ids.append(credit_line7)
                else:
                    if debit_account_id7:
                        debit_line7 = (0, 0, {
                            'name': payment_slip.voucher_method7.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id7,
                            'debit': amount7,
                            'credit': 0.0,
                            # 'analytic_account_id': analytic_account_id,
                        })
                        line_ids.append(debit_line7)

                    if credit_account_id7:
                        credit_line7 = (0, 0, {
                            'name': payment_slip.voucher_method7.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id7,
                            'debit': 0.0,
                            'credit': amount7,
                            'analytic_account_id': False,
                        })
                        line_ids.append(credit_line7)

            amount8 = payment_slip.deduct4_amount
            debit_account_id8 = payment_slip.voucher_method8.debit_account_id.id or False
            credit_account_id8 = payment_slip.voucher_method8.credit_account_id.id or False

            if payment_slip.deduct4 == True:
                deduct_4 = payment_slip.deduct4_amount
                grand_tot_ded.append(deduct_4)
                if payment_slip.voucher_method8.account_analytic_true == True:
                    deduct4_analytic = payment_slip.employee_id.analytic_account_id and payment_slip.employee_id.analytic_account_id.id or False
                    if debit_account_id8:
                        debit_line8 = (0, 0, {
                            'name': payment_slip.voucher_method8.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id8,
                            'debit': amount8,
                            'credit': 0.0,
                            # 'analytic_account_id': analytic_account_id,
                        })
                        line_ids.append(debit_line8)

                    if credit_account_id8:
                        credit_line8 = (0, 0, {
                            'name': payment_slip.voucher_method8.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id8,
                            'debit': 0.0,
                            'credit': amount8,
                            'analytic_account_id': deduct4_analytic or False,
                        })
                        line_ids.append(credit_line8)
                else:
                    if debit_account_id8:
                        debit_line8 = (0, 0, {
                            'name': payment_slip.voucher_method8.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id8,
                            'debit': amount8,
                            'credit': 0.0,
                            # 'analytic_account_id': analytic_account_id,
                        })
                        line_ids.append(debit_line8)

                    if credit_account_id8:
                        credit_line8 = (0, 0, {
                            'name': payment_slip.voucher_method8.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id8,
                            'debit': 0.0,
                            'credit': amount8,
                            'analytic_account_id': False,
                        })
                        line_ids.append(credit_line8)

            amount9 = payment_slip.other1_amount
            debit_account_id9 = payment_slip.voucher_method9.debit_account_id.id or False
            credit_account_id9 = payment_slip.voucher_method9.credit_account_id.id or False

            if payment_slip.other1 == True:
                # raise UserError(_('This Employee has unt, You cannot confirm this Voucher'))
                other_1 = payment_slip.other1_amount
                grand_tot.append(other_1)
                if payment_slip.voucher_method9.account_analytic_true == True:
                    other_analytic = payment_slip.employee_id.analytic_account_id and payment_slip.employee_id.analytic_account_id.id or False
                    if debit_account_id9:
                        debit_line9 = (0, 0, {
                            'name': payment_slip.voucher_method9.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id9,
                            'debit': amount9,
                            'credit': 0.0,
                            'analytic_account_id': other_analytic or False,
                        })
                        line_ids.append(debit_line9)

                    if credit_account_id9:
                        credit_line9 = (0, 0, {
                            'name': payment_slip.voucher_method9.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id9,
                            'debit': 0.0,
                            'credit': amount9,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line9)
                else:
                    if debit_account_id9:
                        debit_line9 = (0, 0, {
                            'name': payment_slip.voucher_method9.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id9,
                            'debit': amount9,
                            'credit': 0.0,
                            'analytic_account_id': False,
                        })
                        line_ids.append(debit_line9)

                    if credit_account_id9:
                        credit_line9 = (0, 0, {
                            'name': payment_slip.voucher_method9.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id9,
                            'debit': 0.0,
                            'credit': amount9,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line9)

            amount10 = payment_slip.other2_amount
            debit_account_id10 = payment_slip.voucher_method10.debit_account_id.id or False
            credit_account_id10 = payment_slip.voucher_method10.credit_account_id.id or False

            if payment_slip.other2 == True:
                other_2 = payment_slip.other2_amount
                grand_tot.append(other_2)
                if payment_slip.voucher_method10.account_analytic_true == True:
                    other2_analytic = payment_slip.employee_id.analytic_account_id and payment_slip.employee_id.analytic_account_id.id or False
                    if debit_account_id10:
                        debit_line10 = (0, 0, {
                            'name': payment_slip.voucher_method10.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id10,
                            'debit': amount10,
                            'credit': 0.0,
                            'analytic_account_id': other2_analytic or False,
                        })
                        line_ids.append(debit_line10)

                    if credit_account_id10:
                        credit_line10 = (0, 0, {
                            'name': payment_slip.voucher_method10.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id10,
                            'debit': 0.0,
                            'credit': amount10,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line10)
                else:
                    if debit_account_id10:
                        debit_line10 = (0, 0, {
                            'name': payment_slip.voucher_method10.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id10,
                            'debit': amount10,
                            'credit': 0.0,
                            'analytic_account_id': False,
                        })
                        line_ids.append(debit_line10)

                    if credit_account_id10:
                        credit_line10 = (0, 0, {
                            'name': payment_slip.voucher_method10.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id10,
                            'debit': 0.0,
                            'credit': amount10,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line10)

            amount11 = payment_slip.other3_amount
            debit_account_id11 = payment_slip.voucher_method11.debit_account_id.id or False
            credit_account_id11 = payment_slip.voucher_method11.credit_account_id.id or False

            if payment_slip.other3 == True:
                other_3 = payment_slip.other3_amount
                grand_tot.append(other_3)
                if payment_slip.voucher_method11.account_analytic_true == True:
                    other3_analytic = payment_slip.employee_id.analytic_account_id and payment_slip.employee_id.analytic_account_id.id or False
                    if debit_account_id11:
                        debit_line11 = (0, 0, {
                            'name': payment_slip.voucher_method11.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id11,
                            'debit': amount11,
                            'credit': 0.0,
                            'analytic_account_id': other3_analytic or False,
                        })
                        line_ids.append(debit_line11)

                    if credit_account_id11:
                        credit_line11 = (0, 0, {
                            'name': payment_slip.voucher_method11.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id11,
                            'debit': 0.0,
                            'credit': amount11,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line11)
                else:
                    if debit_account_id11:
                        debit_line11 = (0, 0, {
                            'name': payment_slip.voucher_method11.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id11,
                            'debit': amount11,
                            'credit': 0.0,
                            'analytic_account_id': False,
                        })
                        line_ids.append(debit_line11)

                    if credit_account_id11:
                        credit_line11 = (0, 0, {
                            'name': payment_slip.voucher_method11.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id11,
                            'debit': 0.0,
                            'credit': amount11,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line11)

            amount12 = payment_slip.other4_amount
            debit_account_id12 = payment_slip.voucher_method12.debit_account_id.id or False
            credit_account_id12 = payment_slip.voucher_method12.credit_account_id.id or False

            if payment_slip.other4 == True:
                other_4 = payment_slip.other4_amount
                grand_tot.append(other_4)
                if payment_slip.voucher_method12.account_analytic_true == True:
                    other4_analytic = payment_slip.employee_id.analytic_account_id and payment_slip.employee_id.analytic_account_id.id or False
                    if debit_account_id12:
                        debit_line12 = (0, 0, {
                            'name': payment_slip.voucher_method12.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id12,
                            'debit': amount12,
                            'credit': 0.0,
                            'analytic_account_id': other4_analytic or False,
                        })
                        line_ids.append(debit_line12)

                    if credit_account_id12:
                        credit_line12 = (0, 0, {
                            'name': payment_slip.voucher_method12.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id12,
                            'debit': 0.0,
                            'credit': amount12,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line12)
                else:
                    if debit_account_id12:
                        debit_line12 = (0, 0, {
                            'name': payment_slip.voucher_method12.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': debit_account_id12,
                            'debit': amount12,
                            'credit': 0.0,
                            'analytic_account_id': False,
                        })
                        line_ids.append(debit_line12)

                    if credit_account_id12:
                        credit_line12 = (0, 0, {
                            'name': payment_slip.voucher_method12.pay_type,
                            'date': timenow,
                            'partner_id': payment_slip.employee_id.address_home_id.id,
                            'account_id': credit_account_id12,
                            'debit': 0.0,
                            'credit': amount12,
                            # 'analytic_account_id': False,
                        })
                        line_ids.append(credit_line12)

            move.update({'line_ids': line_ids})
            move_id = move_pool.create(move)
            # move_id.action_post()
            # print ("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM",move_id)
            gad_tot = grand_tot
            gad_tot_ded = grand_tot_ded
            tay = sum(gad_tot) - sum(gad_tot_ded)
            # print "GGGGGGGGGGGGGGGGGGGGGGGGG",gad_tot
            self.write({'move_id': move_id.id,
                        'state': 'done',
                        'grand_total': tay,
                        'approved_by2_id': self.env.user.id,
                        'approved_by2_date': fields.Datetime.now(),
                        })
            return True

    @api.constrains('issue_tickets', 'allocated_tickets')
    def _check_ticket(self):
        if self.employee_id:
            if self.allocated_tickets == 0:
                if self.issue_tickets > self.allocated_tickets:
                    raise ValidationError(_('You dont have Ticket Balance'))
            if self.allocated_tickets > 0:
                if self.issue_tickets > self.allocated_tickets:
                    raise ValidationError(_('You are Allow to take upto "%s" Tickets') % (self.allocated_tickets))

    @api.constrains('issue_exit_entry', 'allocated_exit_entry')
    def _check_exit_entry(self):
        if self.employee_id:
            if self.allocated_exit_entry == 0:
                if self.issue_exit_entry > self.allocated_exit_entry:
                    raise ValidationError(_('You dont have Exit Entry Balance'))
            if self.allocated_exit_entry > 0:
                if self.issue_exit_entry > self.allocated_exit_entry:
                    raise ValidationError(
                        _('You are Allow to take upto "%s" Exit Re-Entry') % (self.allocated_exit_entry))

    @api.onchange('issue_tickets')
    def onchange_issue_tickets(self):
        cap = 0.0
        employee_id = self.employee_id.id
        if employee_id:
            contract_data = self.env['hr.contract'].search([('employee_id', '=', employee_id)], order='id desc',
                                                           limit=1)
            take_ticket = self.issue_tickets
            allow_ticket = contract_data.ticket_balance
            ticket_amt = contract_data.ticket_amount
            if allow_ticket == 0:
                raise UserError(_('You dont have Ticket Balance'))
            elif take_ticket > allow_ticket:
                raise UserError(_('You are Allow to take upto "%s" Tickets') % (allow_ticket))
            else:
                cap = take_ticket * ticket_amt
                return {'value': {'issue_amount_tickets': cap}}

    @api.onchange('issue_exit_entry')
    def onchange_exit_entry(self):
        cap = 0.0
        employee_id = self.employee_id.id
        if employee_id:
            contract_data = self.env['hr.contract'].search([('employee_id', '=', employee_id)], order='id desc',
                                                           limit=1)
            take_exit_entry = self.issue_exit_entry
            allow_exit_entry = contract_data.exit_entry_balance
            exit_entry_amt = contract_data.exit_entry_amount

            if allow_exit_entry == 0:
                raise UserError(_('You dont have Exit Entry Balance'))
            elif take_exit_entry > allow_exit_entry:
                raise UserError(_('You are Allow to take upto "%s" Exit Re-Entry') % (allow_exit_entry))
            else:
                cap = take_exit_entry * exit_entry_amt
                return {'value': {'issue_amount_exit_entry': cap}}

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        employee_id = self.employee_id.id
        contract_data = self.env['hr.contract'].search([('employee_id', '=', employee_id)], order='id desc', limit=1)
        # print "555555555555555555555555555555555555555",contract_data
        ticket_year = contract_data.ticket_balance
        # print "DDDDD1111111111111:",ticket_year
        ticket_money = contract_data.ticket_amount * ticket_year
        # print "DDDDD1111111111111:",ticket_money
        exit_entry_year = contract_data.exit_entry_balance
        # print "DDDDD1111111111111:",exit_entry_year
        exit_entry_money = contract_data.exit_entry_amount * exit_entry_year
        # print "DDDDD1111111111111:",exit_entry_money
        remain_leave = contract_data.employee_id.remaining_leaves
        # print "DDDDD1111111111111:",remain_leave

        bal_loan = 0.0
        emp_loan_ids = self.env['hr.loan'].search([('employee_id', '=', employee_id), ('state', '=', 'approved')])
        # print "DDDDD1111111111111:",emp_loan_ids
        for loan_data in emp_loan_ids:
            bal_loan += loan_data.balance_amount
        # print "BBBBBBBBBB22222222222222222222:",bal_loan

        emp_holidays_ids = self.env['hr.leave'].search(
            [('employee_id', '=', employee_id), ('state', '=', 'validate'), ('holiday_status_id.name', '=', 'Unpaid')])
        # print "SSSSSSSSSSSSSSSSSSSS",emp_holidays_ids
        res = []
        emp_holidays_legal_ids = self.env['hr.leave'].search(
            [('employee_id', '=', employee_id), ('state', '=', 'validate'),
             ('holiday_status_id.name', '=', 'LegalLeaves'), ('name', '!=', 'Paid Legalleaves'),
             ('voucher_paid', '=', False)], order='id desc', limit=1)
        # print "1111111111111111111111111111111111111111111",emp_holidays_legal_ids

        res = emp_holidays_legal_ids
        val = 0.0
        for hai in emp_holidays_ids:
            total_paid_amount = 0.0
            val += hai.number_of_days
        #   print "UUUUUUUUUUUUUUUUUUUU",val
        emp_voucher_data = self.env['employee.voucher'].search(
            [('employee_id', '=', employee_id), ('end_service', '=', True), ('state', '=', 'done')], order='id desc',
            limit=1)
        # print "VOVOVOVOVOVOVVVOVOVOOVVO",emp_voucher_data

        emp_eos = 0.0
        emp_tot_eos = 0.0

        emp_eos = emp_voucher_data.paid_amount
        emp_paid_eos = emp_voucher_data.paid_eos_amount
        emp_detail = emp_voucher_data.leave_reason

        emp_tot_e_eos = emp_voucher_data.e_total_eos_amount
        emp_tot_t_eos = emp_voucher_data.t_total_eos_amount
        emp_tot_q_eos = emp_voucher_data.q_total_eos_amount

        date_format = '%Y-%m-%d'

        start_date = contract_data.date_start
        end_date = contract_data.date_end
        if start_date:
            current_date = fields.datetime.now().strftime(date_format)

            d1 = fields.Datetime.from_string(start_date)
            #   print "STSSTSTSTSTSTSTTSTST",d1

            d2 = fields.Datetime.from_string(current_date)
            #  print "CDCDCDCDCDCDCDCDCDCDC",d2

            if end_date:
                d3 = fields.Datetime.from_string(end_date)
                #     print "ENEENENENENENENENNENE",d3
                if val > 0.0:
                    tab = d1 + relativedelta.relativedelta(days=val)
                    # print ("VACAGVACAVCACAGACAVACAAVACAVACA",tab)
                    r = relativedelta.relativedelta(d3, tab)
                    delta = d3 - tab
                    period_days = delta.days
                    #    print "VACAGVACAVCACAGACAVACAAVACAVACA",period_days
                    whole_days = r.days
                    #   print "VACAGVACAVCACAGACAVACAAVACAVACA",whole_days
                    whole_months = r.months
                    #  print "VACAGVACAVCACAGACAVACAAVACAVACA",whole_months
                    whole_years = r.years
                # print "VACAGVACAVCACAGACAVACAAVACAVACA",whole_years
                # cap = d1 + relativedelta.relativedelta(months=12)
                # print"CPCPCPCPCPCPCPC",cap
                else:
                    r = relativedelta.relativedelta(d3, d1)
                    delta = d3 - d1
                    period_days = delta.days
                    #    print "VACAGVACAVCACAGACAVACAAVACAVACA",period_days
                    whole_days = r.days
                    #   print "VACAGVACAVCACAGACAVACAAVACAVACA",whole_days
                    whole_months = r.months
                    #  print "VACAGVACAVCACAGACAVACAAVACAVACA",whole_months
                    whole_years = r.years
                # print "VACAGVACAVCACAGACAVACAAVACAVACA",whole_years
                # cap = d1 + relativedelta.relativedelta(months=12)
                # print"CPCPCPCPCPCPCPC",cap

                emp_net = contract_data.value1 + contract_data.value2 + contract_data.value3 + contract_data.value4 + contract_data.value5 + contract_data.value6
                # print ("PPPPPPPPPPPPPPPP",emp_net)
                day_salary = emp_net / 30
                # print "PPPPPPPPPPPPPPPP",day_salary
                actual_work_days = period_days - val
                # print "PPPPPPPPPPPPPPPP",actual_work_days
                ########### Calculation of Employee END of service  #############

                end_first = 0.0
                end_second = 0.0
                end_third = 0.0

                eos_end_years = actual_work_days / 365
                # print "qqqqqqqqqqqqqq",eos_end_years
                if eos_end_years < 2:
                    end_first = eos_end_years * emp_net / 2
                # print "E1E1E1E1E1E1EE1E1",end_first

                elif eos_end_years < 5 and eos_end_years >= 2:
                    end_first = 2 * emp_net / 2
                    second_year_sly = emp_net / 2
                    second_month_sly = second_year_sly / 12
                    second_days_sly = second_month_sly / 30
                    end_second = ((whole_years - 2) * second_year_sly) + (whole_months * second_month_sly) + (
                            whole_days * second_days_sly)
                # print "E2E2EE22E2E2E2E2EE2",end_second

                elif eos_end_years >= 5:
                    end_rem_val = eos_end_years - 5
                    # print "R1R1R1R1R1R1R1R1R1R",end_rem_val
                    end_first = 2 * emp_net / 2
                    end_second = 3 * emp_net / 2
                    third_year_sly = emp_net
                    third_month_sly = third_year_sly / 12
                    third_days_sly = third_month_sly / 30
                    end_third = ((whole_years - 5) * third_year_sly) + (whole_months * third_month_sly) + (
                            whole_days * third_days_sly)
                # print "E3E3E3E3E3E3E3E3E3E3",end_third

                ########### Calculation of Employee TERMINATION #############

                term_first = 0.0
                term_second = 0.0
                term_third = 0.0

                eos_term_years = actual_work_days / 365
                # print "qqqqqqqqqqqqqq",eos_end_years
                if eos_term_years < 2:
                    first_year_sly = emp_net / 2
                    first_month_sly = first_year_sly / 12
                    first_days_sly = first_month_sly / 30
                    term_first = (whole_years * first_year_sly) + (whole_months * first_month_sly) + (
                            whole_days * first_days_sly)
                # print "T1T1T1T1T1T1T1T1T1T1",term_first

                elif eos_term_years < 5 and eos_end_years >= 2:
                    term_first = 2 * emp_net / 2
                    second_year_sly = emp_net / 2
                    second_month_sly = second_year_sly / 12
                    second_days_sly = second_month_sly / 30
                    term_second = ((whole_years - 2) * second_year_sly) + (whole_months * second_month_sly) + (
                            whole_days * second_days_sly)
                # print "T2T2T2TT2T2T2T2T2T2T2",term_second

                elif eos_term_years >= 5:
                    term_rem_val = eos_term_years - 5
                    # print "R2R2RR22R2R2R2RR2R2RR2",term_rem_val
                    term_first = 2 * emp_net / 2
                    term_second = 3 * emp_net / 2
                    third_year_sly = emp_net
                    third_month_sly = third_year_sly / 12
                    third_days_sly = third_month_sly / 30
                    term_third = ((whole_years - 5) * third_year_sly) + (whole_months * third_month_sly) + (
                            whole_days * third_days_sly)
                # print "T3T3T3T3T3T3TT3T33T3T3T",term_third

                ########### Calculation of Employee QUIT #############

                quit_first = 0.0
                quit_second = 0.0
                quit_third = 0.0
                quit_fourth = 0.0

                eos_quit_years = actual_work_days / 365
                # print "qqqqqqqqqqqqqq",eos_end_years
                if eos_quit_years < 2:
                    quit_first = 0.0
                # print "Q1Q1Q1Q1Q1Q1Q1Q1Q1Q1Q1",quit_first

                elif eos_quit_years < 5 and eos_end_years >= 2:
                    quit_second = (eos_quit_years * emp_net / 2) * 1 / 3
                    # print "Q2Q2Q2Q2Q2Q22Q2Q2Q2Q2Q2Q2",quit_second

                    quit_first = (2 * emp_net / 2) * 1 / 3
                    second_year_sly = (emp_net / 2) * 1 / 3
                    second_month_sly = second_year_sly / 12
                    second_days_sly = second_month_sly / 30
                    quit_second = ((whole_years - 2) * second_year_sly) + (whole_months * second_month_sly) + (
                            whole_days * second_days_sly)

                elif eos_quit_years < 10 and eos_end_years >= 5:
                    quit_first = (2 * emp_net / 2) * 2 / 3
                    quit_second = (3 * emp_net / 2) * 2 / 3
                    third_year_sly = (emp_net) * 2 / 3
                    third_month_sly = third_year_sly / 12
                    third_days_sly = third_month_sly / 30
                    quit_third = ((whole_years - 5) * third_year_sly) + (whole_months * third_month_sly) + (
                            whole_days * third_days_sly)
                # print "Q3Q3Q3Q3Q3Q3Q3Q3Q3Q3Q3Q3",quit_third

                elif eos_quit_years >= 10:
                    quit_first = 2 * emp_net / 2
                    quit_second = 3 * emp_net / 2
                    quit_third = 5 * emp_net
                    fourth_year_sly = emp_net
                    fourth_month_sly = fourth_year_sly / 12
                    fourth_days_sly = fourth_month_sly / 30
                    quit_fourth = ((whole_years - 10) * fourth_year_sly) + (whole_months * fourth_month_sly) + (
                            whole_days * fourth_days_sly)
                # print "Q4Q4Q4Q4Q4Q4Q4Q4Q4Q44Q4Q4Q4",quit_fourth

                if emp_voucher_data:
                    result = {'value': {
                        'import_legal': res,
                        'allocated_tickets': ticket_year,
                        'allocated_amount_tickets': ticket_money,
                        'allocated_exit_entry': exit_entry_year,
                        'allocated_amount_exit_entry': exit_entry_money,
                        'per_day_salary': day_salary,
                        'remaining_leaves': remain_leave,

                        'period_year': whole_years,
                        'period_month': whole_months,
                        'period_day': whole_days,
                        'whole_working': period_days,
                        'total_unpaid': val,
                        'actual_working': actual_work_days,
                        'balance_laon': bal_loan,
                        'end_leave_reason': 'END OF CONTRACT',
                        'end_years': eos_end_years,
                        'first_end': end_first,
                        'second_end': end_second,
                        'third_end': end_third,
                        'total_end': end_first + end_second + end_third,

                        'term_leave_reason': 'TERMINATION',
                        'term_years': eos_term_years,
                        'first_term': term_first,
                        'second_term': term_second,
                        'third_term': term_third,
                        'total_term': term_first + term_second + term_third,

                        'quit_leave_reason': 'QUIT',
                        'quit_years': eos_quit_years,
                        'first_quit': quit_first,
                        'second_quit': quit_second,
                        'third_quit': quit_third,
                        'fourth_quit': quit_fourth,
                        'total_quit': quit_first + quit_second + quit_third + quit_fourth,

                        'e_total_eos_amount': emp_tot_e_eos,
                        't_total_eos_amount': emp_tot_t_eos,
                        'q_total_eos_amount': emp_tot_q_eos,
                        'paid_eos_amount': emp_paid_eos + emp_eos,
                        'leave_reason': emp_detail,
                        'record_exit': True,
                    }}

                else:
                    result = {'value': {
                        'import_legal': res,
                        'allocated_tickets': ticket_year,
                        'allocated_amount_tickets': ticket_money,
                        'allocated_exit_entry': exit_entry_year,
                        'allocated_amount_exit_entry': exit_entry_money,
                        'per_day_salary': day_salary,
                        'remaining_leaves': remain_leave,

                        'period_year': whole_years,
                        'period_month': whole_months,
                        'period_day': whole_days,
                        'whole_working': period_days,
                        'total_unpaid': val,
                        'actual_working': actual_work_days,
                        'balance_laon': bal_loan,
                        'end_leave_reason': 'END OF CONTRACT',
                        'end_years': eos_end_years,
                        'first_end': end_first,
                        'second_end': end_second,
                        'third_end': end_third,
                        'total_end': end_first + end_second + end_third,

                        'term_leave_reason': 'TERMINATION',
                        'term_years': eos_term_years,
                        'first_term': term_first,
                        'second_term': term_second,
                        'third_term': term_third,
                        'total_term': term_first + term_second + term_third,

                        'quit_leave_reason': 'QUIT',
                        'quit_years': eos_quit_years,
                        'first_quit': quit_first,
                        'second_quit': quit_second,
                        'third_quit': quit_third,
                        'fourth_quit': quit_fourth,
                        'total_quit': quit_first + quit_second + quit_third + quit_fourth,

                        'e_total_eos_amount': end_first + end_second + end_third,
                        'e_remain_eos_amount': end_first + end_second + end_third,
                        't_total_eos_amount': term_first + term_second + term_third,
                        't_remain_eos_amount': term_first + term_second + term_third,
                        'q_total_eos_amount': quit_first + quit_second + quit_third + quit_fourth,
                        'q_remain_eos_amount': quit_first + quit_second + quit_third + quit_fourth,
                    }}
            else:
                if val > 0.0:
                    tab = d1 + relativedelta.relativedelta(days=val)
                    # print ("VACAGVACAVCACAGACAVACAAVACAVACA",tab)
                    r = relativedelta.relativedelta(d2, tab)
                    delta = d2 - tab
                    period_days = delta.days
                    #    print "VACAGVACAVCACAGACAVACAAVACAVACA",period_days
                    whole_days = r.days
                    #   print "VACAGVACAVCACAGACAVACAAVACAVACA",whole_days
                    whole_months = r.months
                    #  print "VACAGVACAVCACAGACAVACAAVACAVACA",whole_months
                    whole_years = r.years
                # print "VACAGVACAVCACAGACAVACAAVACAVACA",whole_years
                # cap = d1 + relativedelta.relativedelta(months=12)
                # print"CPCPCPCPCPCPCPC",cap
                else:
                    r = relativedelta.relativedelta(d2, d1)
                    delta = d2 - d1
                    period_days = delta.days
                    # print "LELELELELLELELELELELELELELELELELELELELELELELLELELELE",period_days
                    whole_days = r.days
                    #    print "LELELELELLELELELELELELELELELELELELELELELELELLELELELE",whole_days
                    whole_months = r.months
                    #   print "LELELELELLELELELELELELELELELELELELELELELELELLELELELE",whole_months
                    whole_years = r.years
                #  print "LELELELELLELELELELELELELELELELELELELELELELELLELELELE",whole_years
                # cap = d1 + relativedelta.relativedelta(months=12)
                # print"CPCPCPCPCPCPCPC",cap

                emp_net = contract_data.value1 + contract_data.value2 + contract_data.value3 + contract_data.value4 + contract_data.value5 + contract_data.value6
                # print ("LELELELELLELELELELELELELELELELELELELELELELELLELELELE",emp_net)
                day_salary = emp_net / 30
                # print "LELELELELLELELELELELELELELELELELELELELELELELLELELELE",day_salary

                actual_work_days = period_days - val
                # print "LELELELELLELELELELELELELELELELELELELELELELELLELELELE",actual_work_days

                ########### Calculation of Employee END of service  #############

                end_first = 0.0
                end_second = 0.0
                end_third = 0.0

                eos_end_years = actual_work_days / 365
                # print "qqqqqqqqqqqqqq",eos_end_years
                if eos_end_years < 2:
                    end_first = 0.0
                # print "E1E1E1E1E1E1EE1E1",end_first

                elif eos_end_years < 5 and eos_end_years >= 2:
                    end_first = 2 * emp_net / 2
                    second_year_sly = emp_net / 2
                    second_month_sly = second_year_sly / 12
                    second_days_sly = second_month_sly / 30
                    end_second = ((whole_years - 2) * second_year_sly) + (whole_months * second_month_sly) + (
                            whole_days * second_days_sly)
                # print "E2E2EE22E2E2E2E2EE2",end_second

                elif eos_end_years >= 5:
                    end_rem_val = eos_end_years - 5
                    # print "R1R1R1R1R1R1R1R1R1R",end_rem_val
                    end_first = 2 * emp_net / 2
                    end_second = 3 * emp_net / 2
                    third_year_sly = emp_net
                    third_month_sly = third_year_sly / 12
                    third_days_sly = third_month_sly / 30
                    end_third = ((whole_years - 5) * third_year_sly) + (whole_months * third_month_sly) + (
                            whole_days * third_days_sly)
                # print "E3E3E3E3E3E3E3E3E3E3",end_third

                ########### Calculation of Employee TERMINATION #############

                term_first = 0.0
                term_second = 0.0
                term_third = 0.0

                eos_term_years = actual_work_days / 365
                # print "qqqqqqqqqqqqqq",eos_end_years
                if eos_term_years < 2:
                    first_year_sly = emp_net / 2
                    first_month_sly = first_year_sly / 12
                    first_days_sly = first_month_sly / 30
                    term_first = (whole_years * first_year_sly) + (whole_months * first_month_sly) + (
                            whole_days * first_days_sly)
                # print "T1T1T1T1T1T1T1T1T1T1",term_first

                elif eos_term_years < 5 and eos_end_years >= 2:
                    term_first = 2 * emp_net / 2
                    second_year_sly = emp_net / 2
                    second_month_sly = second_year_sly / 12
                    second_days_sly = second_month_sly / 30
                    term_second = ((whole_years - 2) * second_year_sly) + (whole_months * second_month_sly) + (
                            whole_days * second_days_sly)
                # print "T2T2T2TT2T2T2T2T2T2T2",term_second

                elif eos_term_years >= 5:
                    term_rem_val = eos_term_years - 5
                    # print "R2R2RR22R2R2R2RR2R2RR2",term_rem_val
                    term_first = 2 * emp_net / 2
                    term_second = 3 * emp_net / 2
                    third_year_sly = emp_net
                    third_month_sly = third_year_sly / 12
                    third_days_sly = third_month_sly / 30
                    term_third = ((whole_years - 5) * third_year_sly) + (whole_months * third_month_sly) + (
                            whole_days * third_days_sly)
                # print "T3T3T3T3T3T3TT3T33T3T3T",term_third

                ########### Calculation of Employee QUIT #############

                quit_first = 0.0
                quit_second = 0.0
                quit_third = 0.0
                quit_fourth = 0.0

                eos_quit_years = actual_work_days / 365
                # print "qqqqqqqqqqqqqq",eos_end_years
                if eos_quit_years < 2:
                    quit_first = 0.0
                # print "Q1Q1Q1Q1Q1Q1Q1Q1Q1Q1Q1",quit_first

                elif eos_quit_years < 5 and eos_end_years >= 2:
                    quit_second = (eos_quit_years * emp_net / 2) * 1 / 3
                    # print "Q2Q2Q2Q2Q2Q22Q2Q2Q2Q2Q2Q2",quit_second

                    quit_first = (2 * emp_net / 2) * 1 / 3
                    second_year_sly = (emp_net / 2) * 1 / 3
                    second_month_sly = second_year_sly / 12
                    second_days_sly = second_month_sly / 30
                    quit_second = ((whole_years - 2) * second_year_sly) + (whole_months * second_month_sly) + (
                            whole_days * second_days_sly)

                elif eos_quit_years < 10 and eos_end_years >= 5:
                    quit_first = (2 * emp_net / 2) * 2 / 3
                    quit_second = (3 * emp_net / 2) * 2 / 3
                    third_year_sly = (emp_net) * 2 / 3
                    third_month_sly = third_year_sly / 12
                    third_days_sly = third_month_sly / 30
                    quit_third = ((whole_years - 5) * third_year_sly) + (whole_months * third_month_sly) + (
                            whole_days * third_days_sly)
                # print "Q3Q3Q3Q3Q3Q3Q3Q3Q3Q3Q3Q3",quit_third

                elif eos_quit_years >= 10:
                    quit_first = 2 * emp_net / 2
                    quit_second = 3 * emp_net / 2
                    quit_third = 5 * emp_net
                    fourth_year_sly = emp_net
                    fourth_month_sly = fourth_year_sly / 12
                    fourth_days_sly = fourth_month_sly / 30
                    quit_fourth = ((whole_years - 10) * fourth_year_sly) + (whole_months * fourth_month_sly) + (
                            whole_days * fourth_days_sly)
                # print "Q4Q4Q4Q4Q4Q4Q4Q4Q4Q44Q4Q4Q4",quit_fourth

                if emp_voucher_data:
                    result = {'value': {
                        'import_legal': res,
                        'allocated_tickets': ticket_year,
                        'allocated_amount_tickets': ticket_money,
                        'allocated_exit_entry': exit_entry_year,
                        'allocated_amount_exit_entry': exit_entry_money,
                        'per_day_salary': day_salary,
                        'remaining_leaves': remain_leave,

                        'period_year': whole_years,
                        'period_month': whole_months,
                        'period_day': whole_days,
                        'whole_working': period_days,
                        'total_unpaid': val,
                        'actual_working': actual_work_days,
                        'balance_laon': bal_loan,
                        'end_leave_reason': 'END OF CONTRACT',
                        'end_years': eos_end_years,
                        'first_end': end_first,
                        'second_end': end_second,
                        'third_end': end_third,
                        'total_end': end_first + end_second + end_third,

                        'term_leave_reason': 'TERMINATION',
                        'term_years': eos_term_years,
                        'first_term': term_first,
                        'second_term': term_second,
                        'third_term': term_third,
                        'total_term': term_first + term_second + term_third,

                        'quit_leave_reason': 'QUIT',
                        'quit_years': eos_quit_years,
                        'first_quit': quit_first,
                        'second_quit': quit_second,
                        'third_quit': quit_third,
                        'fourth_quit': quit_fourth,
                        'total_quit': quit_first + quit_second + quit_third + quit_fourth,
                        'e_total_eos_amount': emp_tot_e_eos,
                        't_total_eos_amount': emp_tot_t_eos,
                        'q_total_eos_amount': emp_tot_q_eos,
                        'paid_eos_amount': emp_paid_eos + emp_eos,
                        'leave_reason': emp_detail,
                        'record_exit': True,
                    }}

                else:
                    result = {'value': {
                        'import_legal': res,
                        'allocated_tickets': ticket_year,
                        'allocated_amount_tickets': ticket_money,
                        'allocated_exit_entry': exit_entry_year,
                        'allocated_amount_exit_entry': exit_entry_money,
                        'per_day_salary': day_salary,
                        'remaining_leaves': remain_leave,

                        'period_year': whole_years,
                        'period_month': whole_months,
                        'period_day': whole_days,
                        'whole_working': period_days,
                        'total_unpaid': val,
                        'actual_working': actual_work_days,
                        # 'balance_laon':bal_loan,
                        'end_leave_reason': 'END OF CONTRACT',
                        'end_years': eos_end_years,
                        'first_end': end_first,
                        'second_end': end_second,
                        'third_end': end_third,
                        'total_end': end_first + end_second + end_third,

                        'term_leave_reason': 'TERMINATION',
                        'term_years': eos_term_years,
                        'first_term': term_first,
                        'second_term': term_second,
                        'third_term': term_third,
                        'total_term': term_first + term_second + term_third,

                        'quit_leave_reason': 'QUIT',
                        'quit_years': eos_quit_years,
                        'first_quit': quit_first,
                        'second_quit': quit_second,
                        'third_quit': quit_third,
                        'fourth_quit': quit_fourth,
                        'total_quit': quit_first + quit_second + quit_third + quit_fourth,

                        'e_total_eos_amount': end_first + end_second + end_third,
                        'e_remain_eos_amount': end_first + end_second + end_third,
                        't_total_eos_amount': term_first + term_second + term_third,
                        't_remain_eos_amount': term_first + term_second + term_third,
                        'q_total_eos_amount': quit_first + quit_second + quit_third + quit_fourth,
                        'q_remain_eos_amount': quit_first + quit_second + quit_third + quit_fourth,
                    }}
            return result


class employee_voucher_line(models.Model):
    _name = "employee.voucher.line"

    pay_type = fields.Selection(
        [('legal', 'Legal Leave'), ('exitentry', 'Exit Re-Entry'), ('ticket', 'Employee Ticket'),
         ('eos', 'End of Service'), ('deduct1', 'Deduct1'), ('deduct2', 'Deduct2'), ('deduct3', 'Deduct3'),
         ('deduct4', 'Deduct4'), ('other1', 'Other1'), ('other2', 'Other2'), ('other3', 'Other3'),
         ('other4', 'Other4')], string='Payment Type', default='draft')
    payment_name = fields.Char('Name')
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.user.company_id)
    debit_account_id = fields.Many2one('account.account', string='Debit Account', required=True,
                                       help='Debit account for journal entry')
    credit_account_id = fields.Many2one('account.account', string='Credit Account', required=True,
                                        help='Credit account for journal entry')
    account_analytic_true = fields.Boolean(string='Pick Analytic Account from Employee screen')

    @api.constrains('pay_type')
    def _validate_pay_type(self):

        for record in self:
            tab = self.env['employee.voucher.line'].search([('pay_type', '=', record.pay_type)])
            if len(tab) > 1:
                # print ("GGGGGGGGGGGGGGGGGGGGGGGGG",len(tab))
                raise ValidationError(_("This Payment Types is Already created"))


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
