# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    @api.depends('payment_type', 'company_id', 'can_edit_wizard')
    def _compute_available_journal_ids(self):
        for wizard in self:
            if self.env.user.has_group('account_journal_restrict.journal_restrict_group'):
                wizard.available_journal_ids = self.env.user.journal_ids.filtered(lambda l: l.type in ('bank', 'cash'))
            else:
                if wizard.can_edit_wizard:
                    batch = wizard._get_batches()[0]
                    wizard.available_journal_ids = wizard._get_batch_available_journals(batch)
                else:
                    wizard.available_journal_ids = self.env['account.journal'].search([
                        *self.env['account.journal']._check_company_domain(wizard.company_id),
                        ('type', 'in', ('bank', 'cash')),
                    ])
