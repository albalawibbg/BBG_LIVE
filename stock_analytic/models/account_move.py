from odoo import api, models


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ["account.move", "analytic.mixin"]

    @api.onchange('analytic_distribution', 'invoice_line_ids')
    def _onchange_analytic_distribution(self):
        for rec in self:
            if rec.invoice_line_ids and rec.analytic_distribution:
                for line in rec.invoice_line_ids:
                    line.analytic_distribution = rec.analytic_distribution

