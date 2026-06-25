from odoo import api, fields, models
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.depends('type')
    def _compute_show_qty_status_button(self):
        for template in self:
            template.show_on_hand_qty_status_button = template.type == 'product' and self.env.user.has_group('access_qty_onhand.group_access_on_hand_qty')
            template.show_forecasted_qty_status_button = template.type == 'product' and self.env.user.has_group('access_qty_onhand.group_access_forecast_qty')