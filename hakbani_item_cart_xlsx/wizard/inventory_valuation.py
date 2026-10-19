# -*- coding: utf-8 -*-

from odoo import models, api, fields, _


class InventoryValuation(models.TransientModel):
    _name = "inventory.valuation.wizard"
    _description = "Inventory Valuation Wizard"

    date_from = fields.Date("From", required=True)
    date_to = fields.Date("To", required=True)
    # categ_ids = fields.Many2many(comodel_name='product.category', string='Product Category')
    product_ids = fields.Many2many(comodel_name='product.product', string='Products',
                                   domain="[('sale_ok','=',True),('purchase_ok','=',True)]",
                                   required=True)
    location_ids = fields.Many2many(comodel_name='stock.location', string='Location',
                                    domain="[('usage', '=', 'internal')]", required=True)

    file = fields.Binary('Download Report')
    name = fields.Char()

    @api.onchange ('categ_ids')
    def onchange_category(self):
        if self.categ_ids:
            return {'domain': {'product_ids': [('categ_id', 'in', self.categ_ids.ids)]}}

    def generate_valuation_xlsx(self):
        return self.env.ref('hakbani_item_cart_xlsx.inventory_valuation_summary_report').report_action(self)
