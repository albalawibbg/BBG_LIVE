# -*- coding: utf-8 -*-
# Python import
from dateutil.relativedelta import relativedelta

# Odoo Imports
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    min_sale_price = fields.Monetary(
        string="Min Price",
        related='product_id.min_sale_price',
        store=True,
    )

    @api.onchange('price_unit','product_id','order_id.team_id')
    @api.constrains('price_unit','product_id')
    def _check_product_price_unit(self):
        for line in self:
            min_price = self.env['salesteam.min.price'].search([('product_id', '=', line.product_id.id),
                            ('team_id', '=', line.order_id.team_id.id)],limit=1).min_sale_price
            if min_price == 0:
                min_price = line.min_sale_price
            if line.price_unit < min_price:
                raise ValidationError(
                    _('The product price of "%s" cannot be less than %s %s') % (
                        line.product_id.name, min_price, line.currency_id.name))
