# -*- coding: utf-8 -*-

from odoo import api, models,fields


class AccountPaymentRegister(models.TransientModel):
    """ Adding allowed journal in functionality"""
    _inherit = 'account.payment.register'

    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee",default=lambda self:self.env.user.employee_id.id
    )
    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super()._create_payment_vals_from_wizard(batch_result)
        payment_vals.update({'employee_id':self.employee_id.id})
        return payment_vals