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


class stock_picking(models.Model):
    _inherit = 'stock.picking'

    analytic_account_id = fields.Many2one(related="sale_id.analytic_account_id", string="Analytic Account", store=True,
                                          readonly=False)


# analytic_account_id = fields.Many2one('account.analytic.account',  string="Analytic Account", store=True, readonly=False)




class stock_move(models.Model):
    _inherit = 'stock.move'

    analytic_account_id = fields.Many2one(related="picking_id.analytic_account_id", string="Analytic Account",
                                          store=True, readonly=False)

    # def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id,
    #                                    credit_account_id, description):
    #     # This method returns a dictionary to provide an easy extension hook to modify the valuation lines (see purchase for an example)
    #     self.ensure_one()
    #     centro = False
    #     costo = False
    #     if self.location_id and self.location_id.usage == 'customer':  # goods returned from customer
    #         centro = self.analytic_account_id.id
    #     if self.location_id and self.location_id.usage == 'internal':
    #         costo = self.analytic_account_id.id
    #     debit_line_vals = {
    #         'name': description,
    #         'product_id': self.product_id.id,
    #         'quantity': qty,
    #         'product_uom_id': self.product_id.uom_id.id,
    #         'ref': description,
    #         'partner_id': partner_id,
    #         'debit': debit_value if debit_value > 0 else 0,
    #         'credit': -debit_value if debit_value < 0 else 0,
    #         'account_id': debit_account_id,
    #         'analytic_account_id': costo or False,
    #     }
    #
    #     credit_line_vals = {
    #         'name': description,
    #         'product_id': self.product_id.id,
    #         'quantity': qty,
    #         'product_uom_id': self.product_id.uom_id.id,
    #         'ref': description,
    #         'partner_id': partner_id,
    #         'credit': credit_value if credit_value > 0 else 0,
    #         'debit': -credit_value if credit_value < 0 else 0,
    #         'account_id': credit_account_id,
    #         'analytic_account_id': centro or False,
    #     }
    #
    #     rslt = {'credit_line_vals': credit_line_vals, 'debit_line_vals': debit_line_vals}
    #     if credit_value != debit_value:
    #         # for supplier returns of product in average costing method, in anglo saxon mode
    #         diff_amount = debit_value - credit_value
    #         price_diff_account = self.product_id.property_account_creditor_price_difference
    #
    #         if not price_diff_account:
    #             price_diff_account = self.product_id.categ_id.property_account_creditor_price_difference_categ
    #         if not price_diff_account:
    #             raise UserError(_(
    #                 'Configuration error. Please configure the price difference account on the product or its category to process this operation.'))
    #
    #         rslt['price_diff_line_vals'] = {
    #             'name': self.name,
    #             'product_id': self.product_id.id,
    #             'quantity': qty,
    #             'product_uom_id': self.product_id.uom_id.id,
    #             'ref': description,
    #             'partner_id': partner_id,
    #             'credit': diff_amount > 0 and diff_amount or 0,
    #             'debit': diff_amount < 0 and -diff_amount or 0,
    #             'account_id': price_diff_account.id,
    #         }
    #     return rslt
    #
