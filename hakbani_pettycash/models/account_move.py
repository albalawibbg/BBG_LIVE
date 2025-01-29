# -*- coding: utf-8 -*-

from odoo import api, fields, models, _,exceptions
from odoo.exceptions import UserError, ValidationError
# from odoo.exceptions import Warning
from datetime import date, datetime

class AccountMove(models.Model):
    _inherit = 'account.move'

    vat = fields.Char(string="Supplier Taxes Number",  related='partner_id.vat',store=True)
    client_order_ref = fields.Char(string="Customer Ref")
    conract_no = fields.Char(string="Contract No")
    tsleem_invoices_id = fields.Many2one('tsleem.invoices',string="Source Document",readonly=True)


    def write(self, vals):
        if vals.get('move_type') in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']:
            if vals.get('date'):
                if datetime.strptime(str(vals.get('date')), '%Y-%m-%d') > datetime.today():
                    raise UserError(
                            _('Please Select Valid Date .'))
            if vals.get('ref') and not vals.get('partner_id') :
                move = self.env['account.move'].search([('partner_id', '=', self.partner_id.id),('ref','=',vals.get('ref'))])
                if move:
                    raise UserError(
                            _('Can Use Same Ref With Same Partner.'))
            elif vals.get('ref') and vals.get('partner_id'):
                move = self.env['account.move'].search([('partner_id', '=', vals.get('partner_id')),('ref','=',vals.get('ref'))])
                if move:
                    raise UserError(
                            _('Can Use Same Ref With Same Partner.'))

        res = super(AccountMove, self).write(vals)
        return res
    @api.model
    def create(self, vals):
        if vals.get('move_type') in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']:
            if vals.get('date'):
                if datetime.strptime(str(vals.get('date')), '%Y-%m-%d') > datetime.today():
                    raise UserError(
                            _('Please Select Valid Date .'))
            if vals.get('ref'):
                move = self.env['account.move'].search(
                    [('partner_id', '=', vals.get('partner_id')), ('ref', '=', vals.get('ref'))])
                if move:
                    raise UserError(
                        _('Can Use Same Ref With Same Partner.'))
        res = super(AccountMove, self).create(vals)
        return res

    @api.onchange('vat')
    def onchange_tax_number(self):
        if self.vat and self.state == 'draft' and self.type in ['in_invoice','in_refund','out_invoice','out_refund']:
            partner_id = self.env['res.partner'].search([('vat', '=', self.vat)])
            if partner_id:
                self.partner_id = partner_id.id
            else:
                raise ValidationError(_('No Supplier OR Customer Found From Taxes Number %s'%(self.vat)))

















