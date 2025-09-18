from odoo import api, fields, models, exceptions
from odoo.tools.safe_eval import safe_eval
from lxml import etree
class Partner(models.Model):
    _inherit = 'account.move'

    @api.model
    def get_views(self, views, options=None):
        res = super().get_views(views, options)
        has_edit_access = self.env.user.has_group('hakbani_partner_access.group_person_team_edit')
        if has_edit_access:
            for view_type in res['views']:
                doc = etree.XML(res['views'][view_type]['arch'])
                if view_type == 'form':
                    nodes_form = doc.xpath("//form//field[@name='invoice_user_id']")
                    for node in nodes_form:
                        node.set('readonly', '1')
                    nodes_form = doc.xpath("//form//field[@name='team_id']")
                    for node in nodes_form:
                        node.set('readonly', '1')

                    res['views'][view_type]['arch'] = etree.tostring(doc)
        else:
            for view_type in res['views']:
                doc = etree.XML(res['views'][view_type]['arch'])
                if view_type == 'form':
                    nodes_form = doc.xpath("//form//field[@name='invoice_user_id']")
                    for node in nodes_form:
                        node.set('readonly', '0')
                    nodes_form = doc.xpath("//form//field[@name='team_id']")
                    for node in nodes_form:
                        node.set('readonly', '0')
                res['views'][view_type]['arch'] = etree.tostring(doc)
        return res

