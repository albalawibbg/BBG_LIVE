# -*-coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    @api.model
    def create(self, vals):
        program = super(AccountAnalyticAccount, self).create(vals)
        if not self.env.user.has_group('hakbani_analytic_account_access.group_analytic_account_access'):
            raise AccessError(_("You don't have access rights to create analytic account."))
        return program