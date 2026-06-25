# -*- coding: utf-8 -*-
from odoo import fields, models


class ArtecBaseDocumentLayout(models.TransientModel):
    _inherit = 'base.document.layout'

    custom_header = fields.Boolean(
        string="Custom header",
        related="company_id.custom_header"
    )
    img_custom_header = fields.Binary(
        string="Custom header",
        related="company_id.img_custom_header"
    )
    custom_footer = fields.Boolean(
        string="Custom Footer",
        related="company_id.custom_footer"
    )
    img_custom_footer = fields.Binary(
        string="Custom Footer",
        related="company_id.img_custom_footer"
    )
