# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class Invoice(models.Model):
    _inherit = 'account.move'

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        user = self.env.user
        if user.has_group('sale_custom.group_specific_sales_persons') and self.env.context.get('default_move_type') == 'out_invoice':
            domain = [('invoice_user_id', 'in', user.sales_users.ids)]
        return super(Invoice, self)._search(domain, offset, limit, order, access_rights_uid)
