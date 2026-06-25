from odoo import api, fields, models, exceptions
from odoo.tools.safe_eval import safe_eval
from lxml import etree
class Partner(models.Model):
    _inherit = 'res.partner'
    @api.model
    def get_views(self, views, options=None):
        res = super().get_views(views, options)
        has_edit_access = self.env.user.has_group('hakbani_partner_access.group_partner_edit')
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

