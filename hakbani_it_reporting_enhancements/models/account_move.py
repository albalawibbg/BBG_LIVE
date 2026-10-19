from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    hakbani_team_leader_id = fields.Many2one(
        'res.users', string='Team Leader', compute='_compute_hakbani_team_leader_id',
        store=True, index=True, compute_sudo=True,
    )

    @api.depends('invoice_user_id', 'invoice_line_ids.sale_line_ids.order_id.team_id')
    def _compute_hakbani_team_leader_id(self):
        Team = self.env['crm.team'].sudo()
        for move in self:
            team = False
            # Prefer the actual originating sales order's team when present.
            for line in move.invoice_line_ids:
                if 'sale_line_ids' in line._fields:
                    order_lines = line.sale_line_ids
                    if order_lines:
                        team = order_lines[:1].order_id.team_id
                        if team:
                            break
            # On databases with the standard invoice sales team, use it.
            if not team and 'team_id' in move._fields:
                team = move.team_id
            if not team and move.invoice_user_id:
                team = Team.search([('member_ids', 'in', move.invoice_user_id.id)], limit=1)
                if not team:
                    team = Team.search([('user_id', '=', move.invoice_user_id.id)], limit=1)
            move.hakbani_team_leader_id = team.user_id if team else False
