# -*- coding: utf-8 -*-

from odoo import models, api, fields, _


class ProductMarginReport(models.TransientModel):
    _name = "product.margin.report.wizard"
    _description = "Product Margin Wizard"

    date_from = fields.Date("From", required=True)
    date_to = fields.Date("To", required=False)

    def generate_product_margin_xlsx(self):
        return self.env.ref('hakbani_product_margin_report.report_product_margin_xlsx').report_action(self)

    def generate_product_margin_pdf(self):
        return self.env.ref('hakbani_product_margin_report.report_product_margin').report_action(self)
