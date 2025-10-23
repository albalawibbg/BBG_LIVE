# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'res.users'

    sales_users = fields.Many2many(comodel_name="res.users", relation="sale_user_rel", column1="sid", column2="usid", string="Sales Users", )
    is_manager = fields.Boolean('Sales Manager')