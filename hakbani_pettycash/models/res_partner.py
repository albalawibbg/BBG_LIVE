# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    iban_number = fields.Char(string="IBAN Number")
    tax_number = fields.Char(string="Taxes Number")
    payment_customer_count = fields.Integer('Payment Customer count', compute='_compute_payment_customer_count')
    payment_supplier_count = fields.Integer('Payment Supplier count', compute='_compute_payment_supplier_count')

    def change_name_current(self):
        for me in self:
            partners = me.env['res.partner'].search([])
            for p in partners:
                p.name = p.name

    def _compute_payment_customer_count(self):
        for me in self:
            payment_ids = me.env['account.payment'].search(
                [('partner_id', '=', me.id), ('partner_type', 'in', ('customer', 'supplier'))])
            me.payment_customer_count = len(payment_ids)

    # def _compute_payment_supplier_count(self):
    #     for me in self:
    #         payment_ids = me.env['account.payment'].search(
    #             [('partner_id', '=', me.id), ('partner_type', '=', 'supplier')])
    #         me.payment_supplier_count = len(payment_ids)

    def show_payment_customer(self):
        context = self._context.copy()
        return {
            'name': 'Payments',
            'view_type': 'tree',
            'view_mode': 'list,form',
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'domain': [('partner_id', '=', self.id), ('partner_type', 'in', ('customer','supplier'))],
            'context': context,
        }

    # def show_payment_supplier(self):
    #     context = self._context.copy()
    #     return {
    #         'name': 'Payment Supplier',
    #         'view_type': 'tree',
    #         'view_mode': 'list,form',
    #         'res_model': 'account.payment',
    #         'type': 'ir.actions.act_window',
    #         'domain': [('partner_id', '=', self.id), ('partner_type', '=', 'supplier')],
    #         'context': context,
    #     }

    @api.model
    def create(self, vals):
        if not self.env.user.has_group('hakbani_pettycash.create_supplier_security'):
            raise UserError(
                _('Current User Cant Create Partner Please Contact Your Administrator.'))

        if vals.get('tax_number'):
            partner_id = self.env['res.partner'].search([('vat', '=', vals['vat'])])
            if partner_id:
                raise UserError(_("Tax Number Uniq."))
        res = super(ResPartner, self).create(vals)
        return res


    def unlink(self):
        if not self.env.user.has_group('hakbani_pettycash.create_supplier_security'):
            raise UserError(
                _('Current User Can\'t Delete Partner \n Please Contact Your Administrator.'))
        res = super(ResPartner, self).unlink()
        return res

    def name_get(self):
        result = []
        for record in self:
            if record.tax_number:
                result.append((record.id, "[{}] {}".format(record.tax_number, record.name)))
            else:
                result.append((record.id, "{}".format(record.name)))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.search([('tax_number', operator, name)] + args, limit=limit)
        if not recs.ids:
            return super(ResPartner, self).name_search(name=name, args=args,
                                                       operator=operator,
                                                       limit=limit)
        return recs.name_get()
    # def name_get(self):
    #     result = []
    #     for record in self:
    #         if record.env.context.get('tax_supplier_search', False) :
    #             result.append((record.id, "{}".format(record.tax_number)))
    #         else:
    #             result.append((record.id, "{}".format(record.name)))
    #     return result
    #
    # @api.model
    # def name_search(self, name, args=None, operator='ilike', limit=100):
    #     if self.env.context.get('tax_supplier_search', False):
    #         args = args or []
    #         recs = self.search([('tax_number', operator, name)] + args, limit=limit)
    #         if not recs.ids:
    #             return super(ResPartner, self).name_search(name=name, args=args,
    #                                                        operator=operator,
    #                                                        limit=limit)
    #         return recs.name_get()
    #     else:
    #         args = args or []
    #         recs = self.search([('name', operator, name)] + args, limit=limit)
    #         if not recs.ids:
    #             return super(ResPartner, self).name_search(name=name, args=args,
    #                                                        operator=operator,
    #                                                        limit=limit)
    #         return recs.name_get()
