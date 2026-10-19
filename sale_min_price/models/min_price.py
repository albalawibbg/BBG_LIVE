# -*- coding: utf-8 -*-
# Python import
from dateutil.relativedelta import relativedelta

# Odoo Imports
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Saleminprice(models.Model):
    _name = 'salesteam.min.price'

    min_sale_price = fields.Float(
        string="Min Price",
    )
    team_id = fields.Many2one(comodel_name="crm.team", string="Sales Team", required=False, )
    product_id = fields.Many2one(comodel_name="product.template", string="Product Template", required=False, )
    variant_id = fields.Many2one(comodel_name="product.product", string="Product Variant", required=False, )

    @api.onchange('product_id')
    @api.constrains('product_id','team_id')
    def onchange_product(self):
        for rec in self:
            if rec.ids:
                if self.search([('id','!=',rec.ids[0]),('product_id','=',rec.product_id.id),('team_id','=',rec.team_id.id)]):
                    raise ValidationError(_("This Product:{} is already exist with the same team".format(rec.product_id.display_name)))
            rec.variant_id = self.env['product.product'].search([('product_tmpl_id','=',rec.product_id.id)],limit=1).id


