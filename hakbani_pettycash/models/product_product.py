from odoo import fields, models, api


class ModelName(models.Model):
    _inherit = 'product.product'

    is_petty_cash = fields.Boolean(string='Is Betty Cash', default=False)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_petty_cash = fields.Boolean(string='Is Betty Cash', default=False)

    @api.model
    def default_get(self, fields):
        res = super(ProductTemplate, self).default_get(fields)
        res['type'] = 'service'
        res['detailed_type'] = 'service'
        return res
