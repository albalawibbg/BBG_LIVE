# Copyright 2015 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Accountpayment(models.Model):
    _inherit = "account.payment"

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        if self.env.user.has_group('sale_custom.group_own_customers') and  self.env.context.get('default_payment_type') == 'inbound':
            user_domain = [
                '|', ('create_uid', '=', self.env.user.id), ('partner_id.user_id', '=', self.env.user.id)
            ]
            domain = domain + user_domain
        return super(Accountpayment, self)._search(domain, offset=offset, limit=limit, order=order,
                                                   access_rights_uid=access_rights_uid)

    valid_payment_partner_ids = fields.Many2many('res.partner', string='Valid payment partners', compute='compute_valid_payment_partners')

    @api.depends('payment_type')
    def compute_valid_payment_partners(self):
        for move in self:
            if move.payment_type in ['inbound'] :
                if self.env.user.has_group('sale_custom.group_own_customers'):
                    customer_ids = self.env['res.partner'].search(
                        [('user_id', '=', self.env.user.id)])
                    move.valid_payment_partner_ids = customer_ids.ids
                else:
                    customer_ids = self.env['res.partner'].search(
                        [ ('customer_rank', '!=', 0)])
                    move.valid_payment_partner_ids = customer_ids.ids
            elif move.payment_type in ['outbound']:
                supplier_ids = self.env['res.partner'].search(
                    [ ('supplier_rank','!=',0)])
                move.valid_payment_partner_ids = supplier_ids.ids
            else:
                move.valid_payment_partner_ids = False

