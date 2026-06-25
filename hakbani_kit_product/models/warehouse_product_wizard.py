from odoo import api, fields, models, _


class WarehouseProductWizard(models.TransientModel):
    _name = 'warehouse.product.wizard'

    warehouse_product_ids = fields.One2many('warehouse.product.stock', 'warehouse_product_id',
                                            string='Warehouse Products')

    @api.model
    def default_get(self, default_fields):
        res = super(WarehouseProductWizard, self).default_get(default_fields)
        if self._context.get('active_model') == 'sale.order.line':
            product_warehouse_stock_data = []
            stock_quant = self.env['stock.quant']
            sale_product = self.env['product.template'].browse(self._context.get('product_id'))
            # bom_lis = []
            # for bom in sale_product.bom_ids:
            #     for line in bom.bom_line_ids:
            #         if line.is_main_product:
            #             bom_lis.append(line.product_id.id)
            product = self.env['product.product'].browse(sale_product.product_variant_id.id)
            if product:
                warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)])
                for record in warehouse:
                    available_qty = product.with_context(location=record.lot_stock_id.id).qty_available
                    # available_qty_for_sale = product._get_qty_available_sale_location(record.lot_stock_id)
                    available_qty_on_hand = stock_quant._get_available_quantity(product_id=product,
                                                                                         location_id=record.lot_stock_id,
                                                                                         lot_id=None,
                                                                                         package_id=None,
                                                                                         owner_id=None,
                                                                                         strict=False)
                    if (available_qty and available_qty_on_hand) > 0:
                        product_warehouse_stock_data.append((0, 0, {
                            'product_id': product.id,
                            'warehouse_id': record.id,
                            'location_id': record.lot_stock_id.id,
                            'available_qty_on_hand': available_qty,
                            # 'available_qty_for_sale': available_qty_for_sale,
                            'qty': available_qty_on_hand,
                        }))
            res.update({'warehouse_product_ids': product_warehouse_stock_data})
        return res


class WarehouseProductStock(models.TransientModel):
    _name = 'warehouse.product.stock'

    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    location_id = fields.Many2one('stock.location', string='Location')
    product_id = fields.Many2one('product.product', string='Product')
    qty = fields.Float(string='Available Qty')
    available_qty_for_sale = fields.Float(string='Available Qty for Sale')
    available_qty_on_hand = fields.Float(string='On Hand Qty')
    warehouse_product_id = fields.Many2one('warehouse.product.wizard', string='Warehouse Products')