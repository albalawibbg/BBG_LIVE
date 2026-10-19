# -*-coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError
class SaleMarginReport(models.Model):
    _inherit = 'sale.report'
    margin = fields.Float(groups='sale_margin_access.sale_margin_group')

class SaleMargin(models.Model):
    _inherit = 'sale.order'

    margin = fields.Monetary(groups='sale_margin_access.sale_margin_group')
    margin_percent = fields.Float(groups='sale_margin_access.sale_margin_group')

class SaleLineMargin(models.Model):
    _inherit = 'sale.order.line'
    can_edit_price = fields.Boolean(compute='compute_price_edit')
    @api.depends('product_id')
    def compute_price_edit(self):
        for rec in self:
            rec.can_edit_price = self.env.user.has_group('sale_margin_access.sale_price_edit_group')

    margin = fields.Float(groups='sale_margin_access.sale_margin_group')
    margin_percent = fields.Float(groups='sale_margin_access.sale_margin_group')

