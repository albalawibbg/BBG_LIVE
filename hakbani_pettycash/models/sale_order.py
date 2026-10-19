# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    conract_no = fields.Char(string="Contract No")




class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def create_invoices(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        res = super(SaleAdvancePaymentInv, self).create_invoices()
        print ('sale_orders',res)
        for inv in sale_orders.invoice_ids:
            inv.client_order_ref = sale_orders.client_order_ref
            inv.conract_no = sale_orders.conract_no

        return res
