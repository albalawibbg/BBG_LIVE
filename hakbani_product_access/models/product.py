from odoo import api, fields, models, exceptions

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def create(self, vals):
        # Check if the user has the create access right for product.template
        if not self.env.user.has_group('hakbani_product_access.group_product_creator'):
            raise exceptions.AccessError("You do not have the create access right for product.template.")

        return super(ProductTemplate, self).create(vals)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def create(self, vals):
        # Check if the user has the create access right for product.product
        if not self.env.user.has_group('hakbani_product_access.group_product_creator'):
            raise exceptions.AccessError("You do not have the create access right for product.product.")

        return super(ProductProduct, self).create(vals)
