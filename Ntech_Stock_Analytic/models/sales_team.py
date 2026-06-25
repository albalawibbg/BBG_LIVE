# -*- coding: utf-8 -*-
# Odoo Imports
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, UserError


class SaleTeam(models.Model):
    _inherit = 'crm.team'

    analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Analytic Account",
    )
