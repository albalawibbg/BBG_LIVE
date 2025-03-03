# -*- coding: utf-8 -*-

from odoo import models, api, fields, _


class SaleForecasting(models.TransientModel):
    _name = "sale.forecast.wizard"
    _description = "Sale Forecast Wizard"

    avg_period = fields.Selection([
        ('3', '3 Month'),
        ('4', '4 Month'),
        ('5', '5 Month'),
        ('6', '6 Month'),
    ], 'Average Period', default='3')
    product_ids = fields.Many2many('product.product', string="Products")

    file = fields.Binary('Download Report')
    name = fields.Char()

    def generate_sale_forecast_xlsx(self):
        rec = self.env.ref('hakbani_sale_forecast_report.sale_forecast_xlsx_report_new').report_action(self)
        return rec
