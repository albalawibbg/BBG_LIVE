# -*- coding: utf-8 -*-
from odoo import api, fields, models
import base64
from random import choice
from string import digits
import itertools
# from werkzeug import url_encode
import pytz
from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError
from odoo.modules.module import get_module_resource
from odoo.addons.resource.models.resource_mixin import timezone_datetime

import json
import time
from ast import literal_eval
from collections import defaultdict
from datetime import date
from itertools import groupby
from operator import itemgetter

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, format_datetime
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.tools.misc import format_date
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_auto_reconcile_customer(self):
        if not self:
            return

        invoices = self.filtered(lambda inv: inv.move_type == 'out_invoice' and inv.state == 'posted' and inv.amount_residual > 0.0)
        if not invoices:
            raise UserError("No valid posted invoices with residual amount found.")

        # Ensure all selected invoices are for the same customer
        partners = invoices.mapped('partner_id')
        if len(partners) > 1:
            raise UserError("Please select invoices for the same customer only.")

        customer = partners[0]
        receivable_account = customer.property_account_receivable_id
        # Get unreconciled customer payments
        payments = self.env['account.move.line'].search([
            ('account_id.account_type', '=', 'asset_receivable'),
            ('move_id.state', '=', 'posted'),
            ('partner_id', '=', customer.id),
            ('payment_id', '!=', False),
            ('full_reconcile_id', '=', False),
            ('balance', '<', 0),
        ], order='date asc')

        for invoice in invoices.sorted(lambda inv: inv.invoice_date or inv.date):
            invoice_lines = invoice.line_ids.filtered(lambda l: l.account_id.account_type == 'asset_receivable' and not l.reconciled)
            for line in invoice_lines:
                if line.amount_residual <= 0:
                    continue

                to_reconcile = self.env['account.move.line']
                remaining = line.amount_residual

                for payment_line in payments:
                    if payment_line.reconciled:
                        continue
                    if abs(payment_line.amount_residual) <= 0:
                        continue

                    to_reconcile += payment_line
                    remaining += payment_line.balance

                    if remaining <= 0:
                        break

                if to_reconcile:
                    (to_reconcile + line).reconcile()

        return True
class Accountpayment(models.Model):
    _inherit = 'account.payment'

    def action_auto_reconcile_customer(self):
        invoices = self.env['account.move'].sudo().search([('partner_id', '=',self.partner_id.id) ,('move_type', '=', 'out_invoice') , ('state', '=' ,'posted'),('amount_residual', '>', 0.0)], order='invoice_date_due asc')
        if invoices:

            receivable_account = self.partner_id.property_account_receivable_id
            # Get unreconciled customer payments
            payment_move_line = self.move_id.line_ids.filtered_domain([
                ('account_id.account_type', '=', 'asset_receivable'),
                ('move_id.state', '=', 'posted'),
                ('partner_id', '=', self.partner_id.id),
                ('full_reconcile_id', '=', False),
                ('balance', '<', 0),
            ])
            credit = payment_move_line.credit
            for invoice in invoices:
                invoice_lines = invoice.line_ids.filtered(lambda l: l.account_id.account_type == 'asset_receivable' and not l.reconciled)
                for line in invoice_lines:
                    if line.amount_residual <= 0:
                        continue

                    to_reconcile = self.env['account.move.line']
                    remaining = line.amount_residual

                    for payment_line in payment_move_line:
                        if payment_line.reconciled:
                            continue
                        if abs(payment_line.amount_residual) <= 0:
                            continue

                        to_reconcile += payment_line
                        remaining += payment_line.balance

                        if remaining <= 0:
                            break

                    if to_reconcile:
                        (to_reconcile + line).reconcile()
    def action_post(self):
        res =  super(Accountpayment, self).action_post()

        if self.env.context.get('active_model') == 'account.payment' and  not self.reconciled_invoice_ids and self.payment_type == 'inbound':
            self.action_auto_reconcile_customer()
        return res