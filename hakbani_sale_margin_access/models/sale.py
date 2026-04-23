# -*-coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError


# class AccountMove(models.Model):
#     _inherit = "account.move"
#
#     def write(self, vals):
#         program = super(AccountMove, self).write(vals)
#         move_rec = self.env['account.move'].search([
#             ('ref', '=', self.ref),
#             ('id', '!=', self._origin.id)
#         ])
#         if move_rec:
#             raise ValidationError(_('Reference must be unique!'))
#         return program
#
#     def action_post(self):
#         result = super(AccountMove, self).action_post()
#         if not self.env.user.has_group('hakbani_account_post_button_access.group_post_button_access'):
#             raise UserError(_("You don't have access to Post this record!"))
#         return result
#
#     def button_draft(self):
#         res = super(AccountMove, self).button_draft()
#         if not self.env.user.has_group('hakbani_account_post_button_access.group_post_button_access'):
#             raise UserError(_("You don't have access to move draft stage this record!"))
#         return res
