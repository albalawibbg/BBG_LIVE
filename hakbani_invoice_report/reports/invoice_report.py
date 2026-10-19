from odoo import models, api, fields
from num2words import num2words


class AccountMove(models.AbstractModel):
    _name = 'report.hakbani_invoice_report.report_custom_invoice_template'
    _description = 'Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)

        company = self.env.company

        def get_arabic_total_word(attrb):
            word = str(("%.2f" % attrb)).split('.')
            word_b = (num2words(int(word[0]), lang='ar')).title()
            word_a = (num2words(int(word[1]), lang='ar')).title()
            word_f = str(word_b) + ' ريال '
            sym = '' if str(word[1]) == '00' else ' و ' + word_a + ' هللة '
            Rword = word_f + '' + sym
            return Rword

        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': docs,
            'data': data,
            'company': company,
            'get_arabic_total_word': get_arabic_total_word,
        }