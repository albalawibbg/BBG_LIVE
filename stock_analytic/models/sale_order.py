from odoo import api, models


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "analytic.mixin"]

    @api.onchange('analytic_distribution', 'order_line')
    def _onchange_analytic_distribution(self):
        for rec in self:
            if rec.order_line and rec.analytic_distribution:
                for line in rec.order_line:
                    line.analytic_distribution = rec.analytic_distribution

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if self.analytic_distribution and self.picking_ids:
            for pick in self.picking_ids:
                pick.analytic_distribution = self.analytic_distribution
                for line in pick.move_ids_without_package:
                    line.analytic_distribution = self.analytic_distribution
        return res

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res['analytic_distribution'] = self.analytic_distribution
        return res

