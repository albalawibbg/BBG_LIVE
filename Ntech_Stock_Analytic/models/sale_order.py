# -*- coding: utf-8 -*-
# Odoo Imports
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_default_analytic_account_id(self):
        if self.team_id:
            return self.team_id.analytic_account_id

    analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account',
        # Unrequired company
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="The analytic account related to a sales order.",
        compute='_compute_analytic_account',
        inverse='_inverse_analytic_account',
    )

    @api.depends('team_id')
    def _compute_analytic_account(self):
        for order in self:
            if order.team_id.analytic_account_id:
                order.analytic_account_id = order.team_id.analytic_account_id

    def _inverse_analytic_account(self):
        pass

    def check_analytic_account_id(self):
        if not self.analytic_account_id:
            raise ValidationError(_('Please Select an analytic account and proceed'))

    def action_confirm(self):
        self.check_analytic_account_id()
        return super(SaleOrder, self).action_confirm()

    def copy(self, default=None):
        # OVERRIDE to get default analytic account
        default = default or {}
        if not default.get('name'):
            default['analytic_account_id'] = self.team_id.analytic_account_id.id
        return super().copy(default=default)
