from odoo import api, fields, models,_
import logging
_logger = logging.getLogger(__name__)
from odoo.osv import expression

class Users(models.Model):
    _inherit = 'res.users'

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        _logger.info(">>>>>>>>>>>>>>>>>>>>>{}".format(self.env.context))
        if domain == ['!', ['id', 'in', []]] and not self.env.user.has_group('partner_aged_receivable_filters.group_show_aged_sp') and self.env.user.has_group('sale_custom.group_specific_sales_persons'):
            domain = expression.AND([[('id', 'in', self.env.user.sales_users.ids)], domain])
        return self._search(domain, limit=limit, order=order)
    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        domain = domain or []
        _logger.info("************************{}".format(self.env.context))

        if not domain or (domain and any(d[0] == 'id' and d[1] == [] and len(domain) == 1 for d in domain )) and not self.env.user.has_group('partner_aged_receivable_filters.group_show_aged_sp')  and self.env.user.has_group('sale_custom.group_specific_sales_persons'):
            domain = expression.AND([[('id', 'in', self.env.user.sales_users.ids)], domain])
        return super()._search(domain, offset, limit, order, access_rights_uid)
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    invoice_user_id = fields.Many2one(
        'res.users',
        string='Sales Person',
        related="move_id.invoice_user_id",
        store=True,
    )



