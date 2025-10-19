# Copyright 2015 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    # @api.model
    # def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
    #     user = self.env.user
    #     if user.has_group('sale_custom.group_specific_sales_persons') and self.env.context.get(
    #             'default_move_type') == 'out_invoice':
    #         domain = [('invoice_user_id', 'in', user.sales_users.ids)]
    #     return super(AccountMove, self)._search(domain, offset, limit, order, access_rights_uid)

    valid_partner_ids = fields.Many2many('res.partner', string='Valid partners', compute='compute_valid_partners')
    @api.depends('user_id','move_type')
    def compute_valid_partners(self):
        for move in self:
            if self.env.user.has_group('sale_custom.group_own_customers'):
                if move.move_type in ['out_invoice','out_refund'] :
                    customer_ids = self.env['res.partner'].search(
                        [ ('user_id', '=', move.user_id.id or self.env.user.id)])
                    move.valid_partner_ids = customer_ids.ids
                elif move.move_type in ['in_invoice', 'in_refund']:
                    supplier_ids = self.env['res.partner'].search(
                        [('supplier_rank','!=',0)])
                    move.valid_partner_ids = supplier_ids.ids
                else:
                    move.valid_partner_ids = self.env['res.partner'].search(
                        ['|', ('customer_rank', '!=', 0),('supplier_rank','!=',0)]).ids
            else:
                    move.valid_partner_ids = self.env['res.partner'].search(
                        ['|', ('customer_rank', '!=', 0),('supplier_rank','!=',0)]).ids



