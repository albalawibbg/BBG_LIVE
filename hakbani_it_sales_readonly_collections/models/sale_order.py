from odoo import api, fields, models, _
from odoo.exceptions import AccessError
from lxml import etree


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    hakbani_collected_amount = fields.Monetary(
        string='Collected', currency_field='currency_id', compute='_compute_hakbani_collection',
        groups='sales_team.group_sale_salesman_all_leads',
    )
    hakbani_invoiced_amount = fields.Monetary(
        string='Invoiced', currency_field='currency_id', compute='_compute_hakbani_collection',
        groups='sales_team.group_sale_salesman_all_leads',
    )
    hakbani_outstanding_amount = fields.Monetary(
        string='Outstanding', currency_field='currency_id', compute='_compute_hakbani_collection',
        groups='sales_team.group_sale_salesman_all_leads',
    )

    @api.model
    def _hakbani_is_sales_readonly_user(self):
        user = self.env.user
        return bool(
            not self.env.su
            and user.sudo().hakbani_sales_readonly
            and user.has_group('sales_team.group_sale_salesman_all_leads')
        )

    @api.model
    def _hakbani_check_sales_write(self):
        if self._hakbani_is_sales_readonly_user():
            raise AccessError(_('Your Sales Orders Read Only permission does not allow creating, editing, confirming, or deleting quotations and sales orders.'))

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        result = super().get_view(view_id=view_id, view_type=view_type, **options)
        if view_type in ('form', 'tree') and self._hakbani_is_sales_readonly_user():
            doc = etree.fromstring(result['arch'])
            doc.set('create', 'false')
            doc.set('edit', 'false')
            doc.set('delete', 'false')
            doc.set('duplicate', 'false')
            if view_type == 'form':
                for button in doc.xpath('//header/button | //form/sheet//button'):
                    button.set('invisible', '1')
            result['arch'] = etree.tostring(doc, encoding='unicode')
        return result

    @api.model_create_multi
    def create(self, vals_list):
        self._hakbani_check_sales_write()
        return super().create(vals_list)

    def write(self, vals):
        self._hakbani_check_sales_write()
        return super().write(vals)

    def unlink(self):
        self._hakbani_check_sales_write()
        return super().unlink()

    @api.depends('order_line.invoice_lines.move_id.state',
                 'order_line.invoice_lines.move_id.amount_residual',
                 'order_line.invoice_lines.move_id.amount_total',
                 'order_line.invoice_lines.price_subtotal',
                 'order_line.invoice_lines.move_id.currency_id')
    def _compute_hakbani_collection(self):
        """Allocate reconciled invoice payments to a sale by its invoice lines.

        A shared invoice is allocated proportionally by invoice-line untaxed amounts.
        Refunds linked to the SO are deducted. The result is an indicator of
        invoice settlement, not a cash-basis or payment-journal audit report.
        """
        for order in self:
            invoiced = collected = outstanding = 0.0
            if not order.currency_id:
                order.hakbani_invoiced_amount = 0
                order.hakbani_collected_amount = 0
                order.hakbani_outstanding_amount = 0
                continue
            invoice_lines = order.order_line.invoice_lines.filtered(
                lambda line: line.move_id.state == 'posted'
                and line.move_id.move_type in ('out_invoice', 'out_refund')
                and not line.display_type
            )
            moves = invoice_lines.mapped('move_id')
            for move in moves:
                linked_lines = invoice_lines.filtered(lambda ln: ln.move_id == move)
                part = sum(linked_lines.mapped('price_subtotal'))
                # Invoice-level due/paid includes taxes; allocate using the
                # invoice's full untaxed lines (even those for other SOs).
                untaxed = sum(move.invoice_line_ids.filtered(
                    lambda ln: not ln.display_type
                ).mapped('price_subtotal'))
                share = part / untaxed if untaxed else 0.0
                sign = -1.0 if move.move_type == 'out_refund' else 1.0
                total = move.amount_total * share * sign
                due = move.amount_residual * share * sign
                paid = total - due
                conv_date = move.invoice_date or fields.Date.context_today(order)
                to_order = lambda x: move.currency_id._convert(
                    x, order.currency_id, order.company_id, conv_date)
                invoiced += to_order(total)
                outstanding += to_order(due)
                collected += to_order(paid)
            order.hakbani_invoiced_amount = invoiced
            order.hakbani_collected_amount = collected
            order.hakbani_outstanding_amount = outstanding
