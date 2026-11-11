# -*- coding: utf-8 -*-
from odoo import fields, models


class AccConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    loan_approve = fields.Boolean(
        string="Approval from Accounting Department",
        help="Loan Approval from account manager",
        config_parameter='account.loan_approve',
    )
