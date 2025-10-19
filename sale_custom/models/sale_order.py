# Copyright 2015 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"


    valid_customer_ids = fields.Many2many('res.partner',string='Valid customers',compute='compute_valid_customers')

    @api.depends('user_id')
    def compute_valid_customers(self):
        for order in self:
            if self.env.user.has_group('sale_custom.group_own_customers'):
                customer_ids = self.env['res.partner'].sudo().search(
                    [('company_id', '=', self.env.company.id),('user_id','=',self.env.user.id)])

                order.valid_customer_ids = customer_ids.ids
            else:
                order.valid_customer_ids = self.env['res.partner'].sudo().search([('company_id','=',self.env.company.id),('customer_rank','!=',0)]).ids

