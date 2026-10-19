# -*- coding: utf-8 -*-

from collections import defaultdict
from markupsafe import Markup

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero, plaintext2html


class HrPayroll(models.Model):
    _inherit = 'hr.payslip'

    def _action_create_account_move(self):
        precision = self.env['decimal.precision'].precision_get('Payroll')

        # Add payslip without run
        payslips_to_post = self.filtered(lambda slip: not slip.payslip_run_id)

        # Adding pay slips from a batch and deleting pay slips with a batch that is not ready for validation.
        payslip_runs = (self - payslips_to_post).payslip_run_id
        for run in payslip_runs:
            if run._are_payslips_ready():
                payslips_to_post |= run.slip_ids

        # A payslip need to have a done state and not an accounting move.
        payslips_to_post = payslips_to_post.filtered(lambda slip: slip.state == 'done' and not slip.move_id)

        # Check that a journal exists on all the structures
        if any(not payslip.struct_id for payslip in payslips_to_post):
            raise ValidationError(_('One of the contract for these payslips has no structure type.'))
        if any(not structure.journal_id for structure in payslips_to_post.mapped('struct_id')):
            raise ValidationError(_('One of the payroll structures has no account journal defined on it.'))

        # Map all payslips by structure journal and pay slips month.
        # Case 1: Batch all the payslips together -> {'journal_id': {'month': slips}}
        # Case 2: Generate account move separately -> [{'journal_id': {'month': slip}}]
        if self.company_id.batch_payroll_move_lines:
            all_slip_mapped_data = defaultdict(lambda: defaultdict(lambda: self.env['hr.payslip']))
            for slip in payslips_to_post:
                all_slip_mapped_data[slip.struct_id.journal_id.id][slip.date or fields.Date().end_of(slip.date_to, 'month')] |= slip
            all_slip_mapped_data = [all_slip_mapped_data]
        else:
            all_slip_mapped_data = [{
                slip.struct_id.journal_id.id: {
                    slip.date or fields.Date().end_of(slip.date_to, 'month'): slip
                }
            } for slip in payslips_to_post]

        for slip_mapped_data in all_slip_mapped_data:
            for journal_id in slip_mapped_data: # For each journal_id.
                for slip_date in slip_mapped_data[journal_id]: # For each month.
                    # debit_sum = 0.0
                    # credit_sum = 0.0
                    date = slip_date
                    move_dict = {
                        'narration': '',
                        'ref': fields.Date().end_of(slip_mapped_data[journal_id][slip_date][0].date_to, 'month').strftime('%B %Y'),
                        'journal_id': journal_id,
                        'date': date,
                    }

                    for slip in slip_mapped_data[journal_id][slip_date]:
                        line_ids = []

                        move_dict['narration'] += plaintext2html(slip.number or '' + ' - ' + slip.employee_id.name or '')
                        move_dict['narration'] += Markup('<br/>')
                        slip_lines = slip._prepare_slip_lines(date, line_ids)
                        line_ids.extend(slip_lines)

                    # for line_id in line_ids: # Get the debit and credit sum.
                    #     debit_sum += line_id['debit']
                    #     credit_sum += line_id['credit']

                    # The code below is called if there is an error in the balance between credit and debit sum.
                    # if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
                    #     slip._prepare_adjust_line(line_ids, 'credit', debit_sum, credit_sum, date)
                    # elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
                    #     slip._prepare_adjust_line(line_ids, 'debit', debit_sum, credit_sum, date)

                    # Add accounting lines in the move
                        move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
                        move = self._create_account_move(move_dict)
                        slip.write({'move_id': move.id, 'date': date})
        return True
    def _prepare_line_values(self, line, account_id, date, debit, credit):
        if not self.company_id.batch_payroll_move_lines and line.code == "NET":
            partner = self.employee_id.work_contact_id
        else:
            partner = line.partner_id or line.employee_id.address_id
        if not partner:
            partner = line.employee_id.address_id
        return {
            'name': line.name,
            'partner_id': partner.id,
            'account_id': account_id,
            'journal_id': line.slip_id.struct_id.journal_id.id,
            'date': date,
            'debit': debit,
            'credit': credit,
            'analytic_distribution': (line.salary_rule_id.analytic_account_id and {line.salary_rule_id.analytic_account_id.id: 100}) or
                                     (line.slip_id.contract_id.analytic_account_id.id and {line.slip_id.contract_id.analytic_account_id.id: 100})
        }
