# -*- coding: utf-8 -*-
# Odoo Imports
from odoo import fields, models
from odoo.tools.float_utils import float_round


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    min_sale_price = fields.Monetary(
        string='Min Sale Price',
        currency_field="currency_id",
    )
    min_price_editable = fields.Boolean(
        string="Min price editable ?",
        compute="_compute_min_price_editable"
    )

    # Compute Methods

    def _compute_min_price_editable(self):
        user = self.env.user
        for product in self:
            user_access = user.has_group('sale_min_price.group_sale_min_price')
            product.min_price_editable = user_access
