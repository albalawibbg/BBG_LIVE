# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def show_product_stock_wizard(self):
        ctx = {'product_id': self.product_id.id, 'readonly': True,'create': False}
        if self.env.user.has_group('warehouse_stock_restrictions.group_restrict_warehouse') and self.env.user.restrict_locations:
            domain =  [('product_id', '=', self.product_id.id), ('location_id.usage', '=', 'internal'),
                       ('location_id', 'in', self.env.user.stock_location_ids.ids)]
        else:
            domain = [('product_id', '=', self.product_id.id), ('location_id.usage', '=', 'internal')]

        return {
            'name': "Warehouse Product Stock",
            'view_mode': 'tree',
            'res_model': 'stock.quant',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('stock.view_stock_quant_tree').id,
            'context': ctx,
            'domain':domain,
            'target': 'new',
        }
