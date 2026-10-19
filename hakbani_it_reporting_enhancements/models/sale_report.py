from odoo import fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    # Descriptive dimensions for Pivot Group By (not numerical measures).
    team_leader_id = fields.Many2one(
        'res.users', string='Sales Leader', readonly=True,
    )

    # Numerical measures that appear in the Measures menu.
    team_sales_amount = fields.Monetary(
        string='Sales Team Sales Amount', readonly=True,
    )
    leader_sales_amount = fields.Monetary(
        string='Sales Leader Sales Amount', readonly=True,
    )

    def _select_additional_fields(self):
        result = super()._select_additional_fields()
        leader_sql = '(SELECT ct.user_id FROM crm_team ct WHERE ct.id = s.team_id)'
        result['team_leader_id'] = leader_sql
        # Currency normalization follows Odoo 17's sale.report price_subtotal.
        base_amount = f"""CASE WHEN l.product_id IS NOT NULL THEN
            SUM(l.price_subtotal
                / {self._case_value_or_one('s.currency_rate')}
                * {self._case_value_or_one('currency_table.rate')})
            ELSE 0 END"""
        result['team_sales_amount'] = (
            f'CASE WHEN s.team_id IS NOT NULL THEN ({base_amount}) ELSE 0 END'
        )
        result['leader_sales_amount'] = (
            f'CASE WHEN {leader_sql} IS NOT NULL THEN ({base_amount}) ELSE 0 END'
        )
        return result
