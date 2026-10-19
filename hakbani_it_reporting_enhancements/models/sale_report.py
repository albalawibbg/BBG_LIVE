from odoo import fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    team_leader_id = fields.Many2one('res.users', string='Sales Manager / Team Leader', readonly=True)

    def _select_additional_fields(self):
        fields_dict = super()._select_additional_fields()
        # team_id is already part of Odoo's aggregated sale.report query.
        # This scalar lookup avoids introducing joins that multiply sales totals.
        fields_dict['team_leader_id'] = '(SELECT ct.user_id FROM crm_team ct WHERE ct.id = s.team_id)'
        return fields_dict
