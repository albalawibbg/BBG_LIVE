from odoo import api, fields, models, exceptions
from odoo.tools.safe_eval import safe_eval
from lxml import etree
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def create(self, vals):
        # Check if the user has the create access right for product.template
        if not self.env.user.has_group('hakbani_product_access.group_product_creator'):
            raise exceptions.AccessError("You do not have the create access right for product.template.")

        return super(ProductTemplate, self).create(vals)

    @api.model
    def get_views(self, views, options=None):
        res = super().get_views(views, options)
        has_edit_access = self.env.user.has_group('hakbani_product_access.group_product_editor')
        if has_edit_access:
            for view_type in res['views']:
                doc = etree.XML(res['views'][view_type]['arch'])
                if view_type == 'form':
                    nodes_form = doc.xpath("//form")
                    for node in nodes_form:
                        node.set('edit', '1')
                    res['views'][view_type]['arch'] = etree.tostring(doc)
        else:
            for view_type in res['views']:
                doc = etree.XML(res['views'][view_type]['arch'])
                if view_type == 'form':
                    nodes_form = doc.xpath("//form")
                    for node in nodes_form:
                        node.set('edit', '0')
                res['views'][view_type]['arch'] = etree.tostring(doc)
        return res


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def get_views(self, views, options=None):
        res = super().get_views(views, options)
        has_edit_access = self.env.user.has_group('hakbani_product_access.group_product_editor')
        if has_edit_access:
            for view_type in res['views']:
                doc = etree.XML(res['views'][view_type]['arch'])
                if view_type == 'form':
                    nodes_form = doc.xpath("//form")
                    for node in nodes_form:
                        node.set('edit', '1')
                    res['views'][view_type]['arch'] = etree.tostring(doc)
        else:
            for view_type in res['views']:
                doc = etree.XML(res['views'][view_type]['arch'])
                if view_type == 'form':
                    nodes_form = doc.xpath("//form")
                    for node in nodes_form:
                        node.set('edit', '0')
                res['views'][view_type]['arch'] = etree.tostring(doc)
        return res
    @api.model
    def create(self, vals):
        # Check if the user has the create access right for product.product
        if not self.env.user.has_group('hakbani_product_access.group_product_creator'):
            raise exceptions.AccessError("You do not have the create access right for product.product.")

        return super(ProductProduct, self).create(vals)
