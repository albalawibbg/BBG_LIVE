# -*- coding: utf-8 -*-

from odoo import models, api, fields, _


class SalePurchaseRegister(models.TransientModel):
    _name = "sale.purchase.register.wizard"
    _description = "Sale Purchase Register Wizard"

    date_from = fields.Date("From", required=True)
    date_to = fields.Date("To", required=True)
    product_ids = fields.Many2many(comodel_name='product.product', string='Products')
    location_id = fields.Many2one(comodel_name='stock.location', string='Location',
                                    domain="[('usage', '=', 'internal')]", required=True)
    transaction_type = fields.Selection([
        ('is_in', 'IN'),
        ('is_out', 'OUT'),
    ], string='Transaction Type', default='is_out', required=True)

    file = fields.Binary('Download Report')
    name = fields.Char()

    def generate_sale_purchase_register_xlsx(self):
        return self.env.ref('hakbani_holding_item_xlsx.sale_purchase_register_report').report_action(self)
