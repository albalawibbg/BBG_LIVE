# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo import api, fields, models, _
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError


class TsleemInvoices(models.Model):
    _name = 'tsleem.invoices'
    _rec_name = 'order_number'

    order_number = fields.Char(string='Sequence', default=lambda self: _('New'), readonly=True, store=True)

    name = fields.Char(string='Petty Cash Ref', required=True)
    date = fields.Date(string='Date', required=True, default=datetime.today())
    # @ibralsmn : domain with cash journals
    journal_id = fields.Many2one('account.journal', string="Journal", domain=[('type', 'in', ['cash'])])
    tsleem_invoices_line_id = fields.One2many('tsleem.invoices.line', 'tsleem_invoices_id', string="Tsleem invoices")
    # @ibralsmn :  add sate and handle it actions
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('submitted', 'Submitted'), ('approve', 'Approved'), ('post', 'Posted')],
        default='draft')
    submitted_uid = fields.Many2one(comodel_name='res.users', string='Submitted By')
    # @ibralsmn
    approve_uid = fields.Many2one(comodel_name='res.users', string='Approved By')
    # @ibralsmn
    post_uid = fields.Many2one(comodel_name='res.users', string='Posted By')
    # @ibralsmn get bills and payment count related with petty cash transaction
    bills_count = fields.Integer(compute='_compute_bills_payment_counts')
    payment_count = fields.Integer()
    # @ibralsmn add employee related to petty cash
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee', required=True)

    @api.depends('journal_id')
    def _compute_company_id(self):
        for record in self:
            record.company_id = record.journal_id.company_id or self.env.company

    company_id = fields.Many2one(comodel_name='res.company', string='Company',
                                 store=True, readonly=True,
                                 compute='_compute_company_id')
    company_currency_id = fields.Many2one(string='Company Currency', readonly=True,
                                          related='company_id.currency_id')
    amount_untaxed = fields.Monetary(string='Untaxed Amount Total',  readonly=True,
                                     compute='_compute_amount', currency_field='company_currency_id')
    amount_tax = fields.Monetary(string='Tax Total',  readonly=True,
                                 compute='_compute_amount', currency_field='company_currency_id')
    amount_total = fields.Monetary(string='Total',readonly=True,
                                   compute='_compute_amount', currency_field='company_currency_id')

    # @ibralsmn : recompute total with new tax fields
    @api.depends('amount_untaxed','amount_tax','amount_total')
    def _compute_amount(self):
        for record in self:
            amount_tax = 0.0
            amount_untaxed = 0.0
            total = 0.0
            for line in record.tsleem_invoices_line_id:
                amount_tax += sum([tax.amount for tax in line.tax_id])
                amount_untaxed += line.price_unit
                total += line.price_unit_after_tax
            record.amount_tax = amount_tax
            record.amount_untaxed = amount_untaxed
            record.amount_total = total

    def _compute_bills_payment_counts(self):
        for record in self:
            invoice_lines = self.env['tsleem.invoices.line'].search([('tsleem_invoices_id', '=', record.id)])
            if invoice_lines:
                record.bills_count = len(invoice_lines.invoice_id)
                record.payment_count = len(invoice_lines.payment_id)
            else:
                record.bills_count = 0.0
                record.payment_count = 0.0

    def action_open_bills_payment(self):
        self.ensure_one()
        lines = invoice_lines = self.env['tsleem.invoices.line'].search([('tsleem_invoices_id', '=', self.id)])
        if self.env.context.get('action_to') == 'bill':
            model = 'account.move'
            title = 'Bills'
            domain = [('id', 'in', lines.invoice_id.ids)]
        else:
            model = 'account.payment'
            title = 'Payment'
            domain = [('id', 'in', lines.payment_id.ids)]
        return {
            'name': _(title),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': model,
            'context': {'create': False},
            'domain': domain,
        }

    def function_posted_all(self):
        for record in self:
            for line in record.tsleem_invoices_line_id:
                if line.state == 'draft':
                    line.function_posted()
            record.state = 'post'
            record.post_uid = self.env.uid

    def sum_of_subtotal(self):
        for me in self:
            sum = 0.0
            for line in me.tsleem_invoices_line_id:
                sum += line.price_unit_after_tax
            return sum

    def action_submit(self):
        for record in self:
            record.state = 'submitted'
            record.submitted_uid = self.env.uid

    def action_approve(self):
        for record in self:
            record.state = 'approve'
            record.approve_uid = self.env.uid

    @api.model
    def create(self, vals_list):
        vals_list['order_number'] = self.env['ir.sequence'].next_by_code('petty.cash.seq') or _('New')
        vals_list['order_number'] = self.env['ir.sequence'].next_by_code('petty.cash.seq') or _('New')
        return super(TsleemInvoices, self).create(vals_list)


class TsleemInvoicesLine(models.Model):
    _name = 'tsleem.invoices.line'

    tsleem_invoices_id = fields.Many2one('tsleem.invoices', string="Tsleem invoices")
    supplier_id = fields.Many2one('res.partner', string="Supplier ID", required=True)
    # supplier_id = fields.Many2one('res.partner',string="Supplier ID", required=True,  compute='_compute_supplier_id',store=True)
    # tax_supplier_id = fields.Many2one('res.partner',string="Tax Number", required=True,  compute='_compute_tax_supplier_id',store=True)
    ref = fields.Char(string="Bill Reference", required=True)
    # construction_id = fields.Many2one('construction.module',string="Construction", required=True)
    product_id = fields.Many2one('product.product', string="Product", required=True,
                                 domain=[('is_petty_cash', '=', True)])
    ref_product = fields.Char(string="Ref Product", required=True, compute='_compute_ref_product', store=True)
    date_invoice = fields.Date(string='Bill Date', required=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")
    price_unit = fields.Float(string="Price Unit", required=True)
    # @ibralsmn : domain with purchase taxs only and change itfrom Many2one to Many2many
    tax_id = fields.Many2many('account.tax', string="Purchase Tax", domain=[('type_tax_use','=','purchase')])
    tax_amount = fields.Float(string="TAX Amount", compute='_compute_price_unit_after_tax', store=True)
    price_unit_after_tax = fields.Float(string="Subtotal", compute='_compute_price_unit_after_tax', store=True)

    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], default='draft', tracking=True,
                             copy=False)

    # @ibralsmn : add two fields invoice_id payment_id
    invoice_id = fields.Many2one('account.move', string="Vendor Bill", readonly=True)
    payment_id = fields.Many2one('account.payment', string="Payment", readonly=True)

    # @ibralsmn : get product tax on change product
    @api.onchange('ref')
    def onchange_vendor_ref(self):
        if self.supplier_id.id and self.ref:
            exist_ref = self.env['account.move'].search([('partner_id','=',self.supplier_id.id),
                                                         ('ref','=',self.ref),
                                                         ('id','!=',self._origin.id)])
            if exist_ref :
                raise ValidationError('Try Other Reference with vendor')

    # @ibralsmn : get product tax on change product
    @api.onchange('product_id')
    def onchange_product_id_tax_ids(self):
        self.ensure_one()
        self.tax_id = False
        self.tax_id = self.product_id.supplier_taxes_id.ids if self.product_id.supplier_taxes_id else False

    @api.depends('product_id')
    def _compute_ref_product(self):
        for me in self:
            me.ref_product = me.product_id.name


    @api.depends('price_unit', 'tax_id')
    def _compute_price_unit_after_tax(self):
        for me in self:
            # @ibralsmn : recompute tax_total with new Many2many field
            tax_total = sum([x.amount for x in me.tax_id])
            if me.tax_id and me.price_unit:
                me.tax_amount = round(((me.price_unit) / 100) * (tax_total), 2)
                me.price_unit_after_tax = me.price_unit + me.tax_amount
            elif not me.tax_id:
                me.price_unit_after_tax = me.price_unit

    def unlink(self):
        for me in self:
            if me.invoice_id or me.payment_id:
                raise UserError(_('You cannot delete because Have Bill Or Payment'))
            return super(TsleemInvoicesLine, self).unlink()

    def function_posted(self):
        if self.analytic_account_id:
            analytic_account_id = self.analytic_account_id.id
        else:
            analytic_account_id = None

        if not self.invoice_id:
            invoice_id = self.env['account.move'].create(
                {
                    'move_type': 'in_invoice',
                    'vat': self.supplier_id.vat,
                    'partner_id': self.supplier_id.id,
                    'ref': self.ref,
                    'invoice_date': self.date_invoice,
                    'tsleem_invoices_id': self.tsleem_invoices_id.id,
                    'invoice_line_ids': [
                        {'product_id': self.product_id.id, 'analytic_account_id': analytic_account_id,
                         'name': self.ref_product, 'price_unit': self.price_unit,
                         # @ibralsmn : pass taxes to invoice
                         'tax_ids': self.tax_id
                         }],
                }
            )
            invoice_id.action_post()
            self.invoice_id = invoice_id.id

        else:
            if self.invoice_id.state == 'posted':
                self.invoice_id.button_draft()
            self.invoice_id.vat = self.supplier_id.vat
            self.invoice_id.partner_id = self.supplier_id.id
            self.invoice_id.ref = self.ref
            self.invoice_id.invoice_date = self.date_invoice
            # self.invoice_id.construction_id_in_invoice = self.construction_id.id
            self.invoice_id.line_ids = [(6, 0, [])]
            line_move = self.env['account.move.line'].create(
                {'move_id': self.invoice_id.id, 'product_id': self.product_id.id,
                 'analytic_account_id': analytic_account_id, 'name': self.ref_product, 'price_unit': self.price_unit,
                 # @ibralsmn fix tx unknown variable
                 'tax_ids': self.tax_id,
                 'account_id': self.product_id.property_account_expense_id.id or self.product_id.categ_id.property_account_expense_categ_id.id})
            self.invoice_id.invoice_line_ids = [(6, 0, [line_move.id])]
            self.invoice_id.action_post()

        if not self.payment_id:
            payment_id = self.env['account.payment'].create(
                {
                    'payment_type': 'outbound',
                    'partner_type': 'supplier',
                    'partner_id': self.supplier_id.id,
                    'date': self.date_invoice,
                    'amount': invoice_id.amount_total,
                    'journal_id': self.tsleem_invoices_id.journal_id.id,
                    'payment_method_id': self.env['account.payment.method'].search([], limit=1).id,
                    'invoice_vendor_bill_id' : invoice_id.id
                })
            payment_id.action_post()
            self.payment_id = payment_id.id
        else:
            if self.payment_id.state == 'posted':
                self.payment_id.action_draft()
            self.payment_id.partner_id = self.supplier_id.id
            self.payment_id.date = self.date_invoice
            self.payment_id.amount = self.invoice_id.amount_total
            self.payment_id.journal_id = self.tsleem_invoices_id.journal_id.id
            self.payment_id.payment_method_id = False
            self.payment_id.post()

        self.state = 'posted'

    def function_cancel(self):
        self.invoice_id.button_draft()
        self.payment_id.action_draft()
        self.state = 'draft'
