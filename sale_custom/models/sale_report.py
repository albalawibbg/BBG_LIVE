# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"
    sales_manager_id = fields.Many2one(comodel_name="res.users", string="Sales Manager",)

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res["sales_manager_id"] = "s.sales_manager_id"
        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """, s.sales_manager_id"""
        return res
