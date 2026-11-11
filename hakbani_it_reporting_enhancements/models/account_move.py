from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    hakbani_team_leader_id = fields.Many2one(
        'res.users', string='Team Leader', compute='_compute_hakbani_team_leader_id',
        store=True, index=True, compute_sudo=True,
    )

    @api.depends('invoice_user_id', 'team_id', 'invoice_line_ids.sale_line_ids.order_id.team_id')
    def _compute_hakbani_team_leader_id(self):
        # Odoo 17: crm.team.member links users to teams, while crm.team.user_id
        # identifies the team leader. Resolve memberships in one query to avoid
        # one search per invoice during installation / stored-field recomputation.
        missing = self.filtered(lambda move: not move.team_id and move.invoice_user_id)
        membership_by_user = {}
        if missing and 'crm.team.member' in self.env:
            members_model = self.env['crm.team.member'].sudo()
            if {'user_id', 'crm_team_id'}.issubset(members_model._fields):
                memberships = members_model.search([
                    ('user_id', 'in', missing.mapped('invoice_user_id').ids),
                ])
                for member in memberships:
                    membership_by_user.setdefault(member.user_id.id, member.crm_team_id)

        for move in self:
            team = False
            # Prefer the sales order's assigned sales team when present.
            for line in move.invoice_line_ids:
                sale_lines = line.sale_line_ids
                if sale_lines:
                    team = sale_lines[:1].order_id.team_id
                    if team:
                        break
            if not team:
                team = move.team_id
            if not team and move.invoice_user_id:
                team = membership_by_user.get(move.invoice_user_id.id)
            move.hakbani_team_leader_id = team.user_id if team else False
