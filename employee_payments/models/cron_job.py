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
#from dateutil import relativedelta
import babel


class hr_contract(models.Model):

	_inherit='hr.contract'
	
	def process_eos_scheduler_queue(self):
		scheduler_line_ids = self.env['hr.contract'].search([])
		#print ("SSSSSSSSSSSSSSSSSSS",scheduler_line_ids)
		for scheduler_line_id in scheduler_line_ids :
			employee_id = scheduler_line_id.employee_id.id
			#print ("CDCDCDCDCDCDCDCDCDCDC",employee_id)
			#emp_holidays_ids = self.env['hr.leave'].search([('employee_id', '=', employee_id),('state','=','validate'),('holiday_status_id.name', '=', 'Unpaid')])
			#print "SSSSSSSSSSSSSSSSSSSS",emp_holidays_ids
			#print('TTTTTTTTTTTTTTTTTTTTTTTTTT',emp_holidays_ids)
			#val = 0.0
			#for hai in emp_holidays_ids:
				#val +=hai.number_of_days
				#print ("UUUUUUUUUUUUUUUUUUUU",val)
			date_format = '%Y-%m-%d'
			start_date = scheduler_line_id.date_start
			print ("STSSTSTSTSTSTSTTSTST",start_date)
			end_date = scheduler_line_id.date_end
			print ("STSSTSTSTSTSTSTTSTST",end_date)
			if start_date and scheduler_line_id.state == 'open':
				current_date = fields.datetime.now().strftime('%Y-%m-%d')
				d1 = fields.Datetime.from_string(start_date)
				print ("STSSTSTSTSTSTSTTSTST",d1)
				d2 = fields.Datetime.from_string(end_date)
				d2 = fields.Datetime.from_string(current_date)
				print ("CDCDCDCDCDCDCDCDCDCDC",d2)
				r = relativedelta(d2,d1)
				delta = d2 - d1
				period_days = delta.days
				print ("CDCDCDCDCDCDCDCDCDCDC",period_days)
				whole_days = r.days
				print ("CDCDCDCDCDCDCDCDCDCDC",whole_days)
				whole_months = r.months
				print ("CDCDCDCDCDCDCDCDCDCDC",whole_months)
				whole_years = r.years
				scheduler_line_id.write({'working_years': whole_years,'working_months': whole_months,'working_days': whole_days})
					
	def process_ticket_scheduler_queue(self):
		scheduler_line_ids = self.env['hr.contract'].search([])
		#print ("SSSSSSSSSSSSSSSSSSS",scheduler_line_ids)
		remaining_leaves = 0.0
		for contract_data in scheduler_line_ids :
			#print (":::::::::NAME::::::NAME::::::",contract_data.employee_id.name)
			ticket_assign = contract_data.ticket
			emp_ticket = contract_data.ticket
			#print (":::::::::TTTTT::::::TTTTTT::::::",emp_ticket)
			emp_exit_entry = contract_data.exit_entry
			#print (":::::::::EEEEEE::::::EEEEE::::::",emp_exit_entry)
			emp_ticket_bal = contract_data.ticket_balance
			#print (":::::::::TBTBTB::::::TBTBTTBT::::::",emp_ticket_bal)
			emp_exit_entry_bal = contract_data.exit_entry_balance
			#print (":::::::::EBEBEBEBE::::::EBEBEBE::::::",emp_exit_entry_bal)
			st_date = contract_data.end_less_date
			
			if st_date and contract_data.state == 'open':
				curr_date = fields.datetime.now().strftime('%Y-%m-%d')
				current_date = fields.Datetime.from_string(curr_date)
				#print (":::::::::CRCRCRCRCRR::::::CRRCCRCRRCRC::::::",current_date)
				start_date = fields.Datetime.from_string(contract_data.end_less_date)
				#print ("STSTSTSTSTSTSTSTSTSTSTSTSTSTSTSTTST",start_date)
				end_date =  start_date + relativedelta(years=contract_data.contract_years)
				#print ("ENEENENENENENENENNENE",end_date)
				if current_date == start_date:   
					contract_data.write({'ticket_balance': (emp_ticket_bal+emp_ticket),'exit_entry_balance': (emp_exit_entry_bal+emp_exit_entry),'end_less_date': end_date})
			

