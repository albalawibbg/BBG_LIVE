from odoo import api, models, _
from odoo.exceptions import AccessError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def _hakbani_check_line_access(self, orders=None):
        user = self.env.user
        if (not self.env.su and user.sudo().hakbani_sales_readonly
                and user.has_group('sales_team.group_sale_salesman_all_leads')):
            raise AccessError(_('You cannot modify quotation or sales order lines with Sales Orders Read Only enabled.'))

    @api.model_create_multi
    def create(self, vals_list):
        self._hakbani_check_line_access()
        return super().create(vals_list)

    def write(self, vals):
        self._hakbani_check_line_access()
        return super().write(vals)

    def unlink(self):
        self._hakbani_check_line_access()
        return super().unlink()
