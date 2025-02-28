# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, api, fields


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "analytic.mixin"]

    @api.onchange('analytic_distribution', 'move_ids_without_package')
    def _onchange_analytic_distribution(self):
        for rec in self:
            if rec.move_ids_without_package and rec.analytic_distribution:
                for line in rec.move_ids_without_package:
                    line.analytic_distribution = rec.analytic_distribution
            if rec.move_line_ids and rec.analytic_distribution:
                for line in rec.move_line_ids:
                    line.analytic_distribution = rec.analytic_distribution

    # def button_validate(self):
    #     self = self.with_context(validate_analytic=True)
    #     return super().button_validate()


class AccountAnalyticApplicability(models.Model):
    _inherit = "account.analytic.applicability"

    business_domain = fields.Selection(
        selection_add=[("stock_picking", "Stock Picking")],
        ondelete={"stock_picking": "cascade"},
    )
