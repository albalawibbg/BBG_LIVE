# -*- coding: utf-8 -*-
# Odoo Imports
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee"
    )