# -*- coding: utf-8 -*-

from odoo import models, api, fields, _


class InventoryValuation(models.TransientModel):
    _name = "one.location.product.wizard"
    _description = "One Location Product Wizard"

    product_ids = fields.Many2many(comodel_name='product.product', string='Products', domain=[('type', '=', 'product')])

    file = fields.Binary('Download Report')
    name = fields.Char()

    def generate_product_location_xlsx(self):
        return self.env.ref('hakbani_product_in_one_location.one_location_product_report').report_action(self)

