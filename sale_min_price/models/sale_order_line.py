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

    @api.constrains('price_unit')
    def _check_product_price_unit(self):
        for line in self:
            if line.price_unit < line.min_sale_price:
                raise ValidationError(
                    _('The product price of "%s" cannot be less than %s %s') % (
                        line.product_id.name, line.min_sale_price, line.currency_id.name))
