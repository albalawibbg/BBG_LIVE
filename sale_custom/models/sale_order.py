# Copyright 2015 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def get_default_user(self):
        if self.env.context.get('default_customer_rank'):
            return self.env.user.id
        else:
            return False
    user_id = fields.Many2one(default=lambda self: self.get_default_user())
    sales_manager_id = fields.Many2one(comodel_name="res.users", string="Sales Manager", required=False,compute='compute_sales_manager',store=True )
    @api.depends('user_id')
    def compute_sales_manager(self):
        for rec in self:
            manager = self.env['res.users']
            if rec.user_id:
                manager = self.env['res.users'].sudo().search([('sales_users','in',rec.user_id.id),('is_manager','=',True)],limit=1)
            rec.sales_manager_id = manager.id

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        users = self.env['res.users']
        if self.env.user.has_group('sale_custom.group_specific_sales_persons'):
            users |= self.env.user.sales_users
        if self.env.user.has_group('sale_custom.group_own_customers') and not self.env.user.has_group('sale_custom.access_all_customers'):
            users |=self.env.user
            user_domain = ['|', ('user_id', 'in', users.ids), ('partner_id.user_id', '=', self.env.user.id)]
            domain = domain + user_domain



        return super(SaleOrder, self)._search(domain, offset=offset, limit=limit, order=order,
                                              access_rights_uid=access_rights_uid)

    valid_customer_ids = fields.Many2many('res.partner',string='Valid customers',compute='compute_valid_customers')

    @api.depends('user_id')
    def compute_valid_customers(self):
        for order in self:
            if self.env.user.has_group('sale_custom.group_own_customers'):
                customer_ids = self.env['res.partner'].sudo().search(
                    [('user_id','=',order.user_id.id or self.env.user.id)])

                order.valid_customer_ids = customer_ids.ids
            else:
                order.valid_customer_ids = self.env['res.partner'].sudo().search([('customer_rank','!=',0)]).ids

