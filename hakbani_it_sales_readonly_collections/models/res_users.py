from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    hakbani_sales_readonly = fields.Boolean(
        string='Sales Orders Read Only',
        help='For Sales All Documents users: prevent editing, creating, deleting, and confirming quotations/sales orders. Does not restrict accounting documents.',
    )
