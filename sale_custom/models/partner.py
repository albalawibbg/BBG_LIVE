# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class Invoice(models.Model):
    _inherit = 'res.partner'
    def get_default_user(self):
        if self.env.context.get('default_customer_rank'):
            return self.env.user.id
        else:
            return False

    user_id = fields.Many2one(default=lambda self:self.get_default_user())
    can_edit_sp = fields.Boolean(string="Edit SalesPerson",compute='check_sp_edit'  )
    @api.depends('can_edit_sp')
    def check_sp_edit(self):
        for rec in self:
            rec.can_edit_sp = self.env.user.has_group('sale_custom.group_edit_customer_persons')