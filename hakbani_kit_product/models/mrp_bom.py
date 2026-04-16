# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    is_main_product = fields.Boolean("Is Main Product", default=False)

