# -*- coding: utf-8 -*-

from odoo import fields, models, api


class Users(models.Model):
    _inherit = 'res.users'

    journal_ids = fields.Many2many(
        'account.journal',
        'users_journals_restrict',
        'user_id',
        'journal_id',
        'Allowed Journals',
    )
