from odoo import fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    # Sales Team is already a standard field (team_id) of Odoo 17 sale.report.
    # The leader is the manager configured directly on the order's sales team.
    team_leader_id = fields.Many2one(
        'res.users', string='Sales Leader', readonly=True,
    )

    def _select_additional_fields(self):
        result = super()._select_additional_fields()
        # Scalar lookup: no join cardinality change, so turnover is not inflated.
        result['team_leader_id'] = '(SELECT ct.user_id FROM crm_team ct WHERE ct.id = s.team_id)'
        return result
