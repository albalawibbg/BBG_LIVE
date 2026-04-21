# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.depends('detailed_type')
    def _compute_kit_product(self):
        for rec in self:
            if rec.detailed_type == 'consu' and rec.bom_ids:
                rec.is_kit_product = True
            elif rec.bom_ids:
                rec.is_kit_product = True
            else:
                rec.is_kit_product = False
    is_kit_product = fields.Boolean("Is Kit Product", compute='_compute_kit_product')
