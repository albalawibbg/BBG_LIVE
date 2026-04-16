# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def show_product_stock_wizard(self):
        ctx = {'product_id': self.product_id.id, 'readonly': True,'create': False}
        return {
            'name': "Warehouse Product Stock",
            'view_mode': 'tree',
            'res_model': 'stock.quant',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('stock.view_stock_quant_tree').id,
            'context': ctx,
            'domain': [('product_id', '=', self.product_id.id), ('location_id.usage','=', 'internal')],
            'target': 'new',
        }
