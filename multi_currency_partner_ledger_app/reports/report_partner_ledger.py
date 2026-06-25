# -*- coding: utf-8 -*-

from odoo import api, models, fields


class MultiReportPartnerLedger(models.AbstractModel):
    _name = 'report.multi_currency_partner_ledger_app.report_partnerledger'

    def _lines(self, data, partner, currency):
        domain = [('move_id.partner_id','=', partner.id), ('move_id.currency_id','=', currency.id)]            
        move_state = data['move_state']
        if move_state == ['posted']:
            domain +=[('move_id.state','=', 'posted')]
        else:
            domain +=[('move_id.state','in', ['draft','posted'])]
        
        account_type = data['account_type']
        if account_type == ['supplier']:
            domain +=[('account_id.account_type', '=', 'liability_payable')]
        elif account_type == ['customer']:
            domain +=[('account_id.account_type', '=', 'asset_receivable')]
        else:
            domain +=[('account_id.account_type', 'in', ['asset_receivable', 'liability_payable'])]

        # for opening balance
        opening_bal = 0
        partner_opening_bal = 0
        if data['date_from']:
            debits = 0
            credit = 0
            entries_before = self.env['account.move.line'].search(domain + [('date', '<', data['date_from'])])
            for x in entries_before:
                debits = debits + x.debit
                credit = credit + x.credit
                opening_bal = debits - credit
                partner_opening_bal += x.amount_currency

        if data['date_from'] and not data['date_to']:
            domain +=[('date', '>=', data['date_from'])]
        elif data['date_to'] and not data['date_from']:
            domain +=[('date', '<=', data['date_to'])]
        elif data['date_from'] and data['date_to']:
            domain +=[('date', '>=', data['date_from']),('date', '<=', data['date_to'])]
        else:
            domain +=[]
        invoice_ids = self.env['account.move.line'].search(domain)
        full_account = []
        for invoice in invoice_ids.sorted(lambda x: x.move_id.date, reverse=False):
            displayed_name = str(invoice.move_id.name or '') + '-' + str(invoice.move_id.payment_reference or '')
            # customer_po_no = str(invoice.move_id.customer_po_no or '')
            opening_bal = opening_bal + invoice.amount_currency
            partner_opening_bal = partner_opening_bal + invoice.amount_currency
            vals = {
                'debit' : invoice.debit,
                'credit' : invoice.credit,
                'amount_currency' : invoice.amount_currency,
                'progress': invoice.balance,
                'date': invoice.move_id.invoice_date or invoice.move_id.date,
                'date_due': invoice.move_id.invoice_date_due,
                'code' : invoice.journal_id.code,
                # 'a_code' : customer_po_no,
                'displayed_name': displayed_name,
                'currency_id': invoice.currency_id.symbol,
                'invoice_id': invoice.move_id.id,
                'balance_opening_amt': opening_bal,
                'partner_opening_bal': partner_opening_bal
            }
            full_account.append(vals)
        # full_account.sort(key=lambda x: x.get('date'))
        return full_account

    def _sum_partner(self, data, partner, currencys):
        total_credit = 0.0
        total_debit = 0.0
        total_balance = 0.0
        total_amount_lst = []
        for currency in currencys:
            records = self._lines(data, partner, currency)
            for record in records:
                total_credit += record['credit']
                total_debit  += record['debit']
                total_balance  += record['progress']
        total_amount_lst.append({'total_credit': total_credit,
                                 'total_debit': total_debit,
                                 'total_balance': total_balance})
        return total_amount_lst

    @api.model
    def _get_report_values(self, docids, data=None):
        context = data.get('context')
        currency_ids = self.env['res.currency'].browse(context.get('currency_ids'))
        partner_ids = self.env['res.partner'].browse(data.get('docs'))

        # get opening Balance for partner
        def get_opening_balance(data, partner, date_from, currency):
            print(partner, date_from)
            debits = 0.0
            credit = 0.0
            domain = [('move_id.partner_id', '=', partner.id), ('move_id.currency_id', '=', currency.id), ('date', '<', data['date_from'])]
            move_state = data['move_state']
            if move_state == ['posted']:
                domain += [('move_id.state', '=', 'posted')]
            else:
                domain += [('move_id.state', 'in', ['draft', 'posted'])]

            account_type = data['account_type']
            if account_type == ['supplier']:
                domain += [('account_id.account_type', '=', 'liability_payable')]
            elif account_type == ['customer']:
                domain += [('account_id.account_type', '=', 'asset_receivable')]
            else:
                domain += [('account_id.account_type', 'in', ['asset_receivable', 'liability_payable'])]
            partner_opening_bal = 0
            opening_bal = 0
            entries_before = self.env['account.move.line'].search(domain)
            for x in entries_before:
                debits = debits + x.debit
                credit = credit + x.credit
                opening_bal = debits - credit
                partner_opening_bal += x.amount_currency
            return opening_bal, partner_opening_bal

        return {
            'currency_ids': currency_ids,
            'doc_model': self.env['res.partner'],
            'docs': partner_ids,
            'lines': self._lines,
            'extra': data,
            'sum_partner': self._sum_partner,
            'get_opening_balance': get_opening_balance,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: