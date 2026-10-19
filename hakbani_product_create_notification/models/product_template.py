# -*-coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        # module_category_rec = self.env['ir.module.category'].search([('name', '=', 'Contracts')])
        group_rec = self.env['res.groups'].search([('name', '=', 'Product Create Notification Access')])
        print(1111111111111111111111111111111111111111111111111111111111, group_rec)
        for rec in group_rec:
            for group_user in rec.users:
                abc = res.with_user(group_user).message_post(
                    body=_('New product %s is created') % (res.name),
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment')
                print(2222222222222222222222222222222222222222222222222222222, abc)
        return res

