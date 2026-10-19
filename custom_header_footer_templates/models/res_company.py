# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ArtecResCompany(models.Model):
    _inherit = 'res.company'

    custom_header = fields.Boolean(
        string="Custom header"
    )
    img_custom_header = fields.Binary(
        string="Custom header"
    )
    custom_footer = fields.Boolean(
        string="Custom Footer"
    )
    img_custom_footer = fields.Binary(
        string="Custom Footer"
    )
