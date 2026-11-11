import base64
import io
from datetime import datetime

import xlsxwriter

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PartnerLedgerExport(models.TransientModel):
    _name = 'hakbani.it.partner.ledger.export'
    _description = 'Export Partner Ledger to Excel'

    partner_id = fields.Many2one('res.partner', required=True, string='Customer / Vendor')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    posted_only = fields.Boolean(default=True, string='Posted Entries Only')
    receivable_only = fields.Boolean(default=True, string='Receivable / Payable Accounts Only')
    include_children = fields.Boolean(default=False, string='Include Child Contacts')
    export_file = fields.Binary(readonly=True, attachment=False)
    export_filename = fields.Char(readonly=True)

    @api.model
    def default_get(self, field_names):
        values = super().default_get(field_names)
        context = self.env.context
        if not values.get('partner_id') and context.get('active_model') == 'res.partner':
            active_ids = context.get('active_ids') or []
            partner_id = context.get('active_id') or (active_ids[0] if len(active_ids) == 1 else False)
            if partner_id:
                values['partner_id'] = partner_id
        if not values.get('partner_id') and context.get('default_partner_id'):
            values['partner_id'] = context['default_partner_id']
        return values

    def action_export_xlsx(self):
        self.ensure_one()
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise UserError(_('Date From cannot be later than Date To.'))
        domain = [('partner_id', 'child_of' if self.include_children else '=', self.partner_id.id),
                  ('company_id', 'in', self.env.companies.ids),
                  ('display_type', 'not in', ('line_section', 'line_note'))]
        if self.posted_only:
            domain.append(('parent_state', '=', 'posted'))
        if self.receivable_only:
            domain.append(('account_id.account_type', 'in', ['asset_receivable', 'liability_payable']))
        if self.date_from:
            domain.append(('date', '>=', self.date_from))
        if self.date_to:
            domain.append(('date', '<=', self.date_to))
        lines = self.env['account.move.line'].search(domain, order='date asc, move_id asc, id asc')
        stream = io.BytesIO()
        book = xlsxwriter.Workbook(stream, {'in_memory': True})
        sheet = book.add_worksheet('Partner Ledger')
        heading = book.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#21476B', 'border': 1})
        title = book.add_format({'bold': True, 'font_size': 15, 'font_color': '#21476B'})
        date_style = book.add_format({'num_format': 'yyyy-mm-dd'})
        money = book.add_format({'num_format': '#,##0.00;[Red](#,##0.00)'})
        bold_money = book.add_format({'bold': True, 'num_format': '#,##0.00', 'top': 1})
        sheet.merge_range(0, 0, 0, 11, 'Partner Ledger / Customer Journal Items', title)
        sheet.write(1, 0, 'Partner')
        sheet.write(1, 1, self.partner_id.display_name)
        sheet.write(2, 0, 'From')
        sheet.write(2, 1, str(self.date_from or 'All'))
        sheet.write(2, 2, 'To')
        sheet.write(2, 3, str(self.date_to or 'All'))
        sheet.write(3, 0, 'Entries')
        sheet.write_number(3, 1, len(lines))
        headers = ['Date', 'Journal Entry', 'Journal', 'Account', 'Partner', 'Label',
                   'Reference', 'Matching Number', 'Debit', 'Credit', 'Balance', 'Running Balance']
        header_row = 5
        for col, header in enumerate(headers):
            sheet.write(header_row, col, header, heading)
        totals = [0.0, 0.0, 0.0]
        running = 0.0
        for idx, line in enumerate(lines, start=header_row + 1):
            debit = line.debit
            credit = line.credit
            balance = line.balance
            running += balance
            totals[0] += debit
            totals[1] += credit
            totals[2] += balance
            sheet.write_datetime(idx, 0, datetime.combine(line.date, datetime.min.time()), date_style)
            sheet.write(idx, 1, line.move_id.name or '')
            sheet.write(idx, 2, line.journal_id.display_name or '')
            sheet.write(idx, 3, line.account_id.display_name or '')
            sheet.write(idx, 4, line.partner_id.display_name or '')
            sheet.write(idx, 5, line.name or '')
            sheet.write(idx, 6, line.ref or '')
            sheet.write(idx, 7, line.matching_number or '')
            for col, amount in enumerate([debit, credit, balance, running], start=8):
                sheet.write_number(idx, col, amount, money)
        total_row = header_row + 1 + len(lines)
        sheet.write(total_row, 7, 'TOTAL', heading)
        for col, amount in enumerate(totals, start=8):
            sheet.write_number(total_row, col, amount, bold_money)
        sheet.write_number(total_row, 11, running, bold_money)
        sheet.set_column(0, 0, 14)
        sheet.set_column(1, 4, 24)
        sheet.set_column(5, 7, 32)
        sheet.set_column(8, 11, 18)
        sheet.freeze_panes(6, 0)
        sheet.autofilter(header_row, 0, max(total_row - 1, header_row), 11)
        book.close()
        filename = 'partner_ledger_%s_%s.xlsx' % (self.partner_id.id, fields.Date.today())
        self.write({'export_file': base64.b64encode(stream.getvalue()), 'export_filename': filename})
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/?model=%s&id=%s&field=export_file&filename_field=export_filename&download=true' % (self._name, self.id),
            'target': 'self',
        }
