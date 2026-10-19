# Copyright (C) 2026 Bahaa Adel
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_round


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    hakbani_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)

    hakbani_raw_cost = fields.Monetary(
        string='Actual Materials Cost', compute='_compute_hakbani_cost_audit',
        currency_field='hakbani_currency_id', compute_sudo=True)
    hakbani_operation_cost = fields.Monetary(
        string='Manufacturing Operations Cost', compute='_compute_hakbani_cost_audit',
        currency_field='hakbani_currency_id', compute_sudo=True)
    hakbani_additional_cost = fields.Monetary(
        string='Additional Manufacturing Cost', compute='_compute_hakbani_cost_audit',
        currency_field='hakbani_currency_id', compute_sudo=True)
    hakbani_total_cost = fields.Monetary(
        string='Total Actual Production Cost', compute='_compute_hakbani_cost_audit',
        currency_field='hakbani_currency_id', compute_sudo=True)
    hakbani_finished_value = fields.Monetary(
        string='Posted Finished Goods Value', compute='_compute_hakbani_cost_audit',
        currency_field='hakbani_currency_id', compute_sudo=True)
    hakbani_byproduct_value = fields.Monetary(
        string='Posted By-product Value', compute='_compute_hakbani_cost_audit',
        currency_field='hakbani_currency_id', compute_sudo=True)
    hakbani_valuation_difference = fields.Monetary(
        string='Cost vs Inventory Valuation Difference', compute='_compute_hakbani_cost_audit',
        currency_field='hakbani_currency_id', compute_sudo=True)
    hakbani_cost_status = fields.Selection([
        ('pending', 'Not Posted'), ('matched', 'Matched'),
        ('review', 'Needs Review'), ('standard', 'Standard Cost Policy'),
    ], string='Cost Audit Result', compute='_compute_hakbani_cost_audit', compute_sudo=True)

    def _hakbani_material_cost(self, moves):
        """Use posted valuation layers where available, else native move value.

        Outgoing component layers are normally negative; their absolute net value
        represents consumed inventory cost. No layers are modified by this method.
        """
        amount = 0.0
        for move in moves:
            layers = move.stock_valuation_layer_ids
            if layers:
                # In some valuation configurations move.value is computed using
                # a unit cost from one lot. Posted layers are the better evidence.
                amount += abs(sum(layers.mapped('value')))
            else:
                amount += abs(move.value) if 'value' in move._fields else 0.0
        return amount

    def _cal_price(self, consumed_moves):
        """Cost finished products from actual consumption + operations + extra cost.

        Keep Odoo's normal downstream SVL/STJ posting and standard-cost policy.
        This override only sets price_unit BEFORE core posting, preventing any
        duplicate valuation/accounting journal entries.
        """
        self.ensure_one()
        result = super()._cal_price(consumed_moves)
        finished = self.move_finished_ids.filtered(
            lambda m: m.product_id == self.product_id
            and m.state not in ('done', 'cancel')
            and m.product_uom.compare(m.quantity, 0) > 0)
        if not finished:
            return result
        quantities = [
            m.product_uom._compute_quantity(m.quantity, m.product_id.uom_id)
            for m in finished]
        total_qty = sum(quantities)
        if float_is_zero(total_qty, precision_rounding=self.product_id.uom_id.rounding):
            return result

        material = self._hakbani_material_cost(consumed_moves)
        operations = sum(wo._cal_cost() for wo in self.workorder_ids)
        additions = self.extra_cost * total_qty  # Standard mrp_account field: unit extra cost
        total = material + operations + additions
        byproducts = self.move_byproduct_ids.filtered(
            lambda m: m.state not in ('done', 'cancel')
            and m.product_uom.compare(m.quantity, 0) > 0)
        share = sum(byproducts.mapped('cost_share'))
        if share > 100.000001 or share < -0.000001 or any(b.cost_share < 0 for b in byproducts):
            raise UserError(_('The total by-product cost share must be between 0 and 100 percent.'))
        for byproduct in byproducts:
            bqty = byproduct.product_uom._compute_quantity(
                byproduct.quantity, byproduct.product_id.uom_id)
            if byproduct.product_id.cost_method in ('fifo', 'average'):
                byproduct.price_unit = total * byproduct.cost_share / 100.0 / bqty if bqty else 0.0
            else:
                byproduct.price_unit = byproduct.product_id.with_company(self.company_id).standard_price
        main = total * float_round(1 - share / 100.0, precision_rounding=0.0001)
        if self.product_id.cost_method in ('fifo', 'average'):
            unit_cost = main / total_qty
            for move in finished:
                move.price_unit = unit_cost
        else:
            for move in finished:
                move.price_unit = move.product_id.with_company(self.company_id).standard_price
        return result

    @api.depends('move_raw_ids.state', 'move_finished_ids.state',
                 'move_raw_ids.quantity', 'move_finished_ids.quantity',
                 'workorder_ids.duration', 'extra_cost', 'state')
    def _compute_hakbani_cost_audit(self):
        for mo in self:
            raw = mo.move_raw_ids.filtered(lambda m: m.state == 'done')
            finished = mo.move_finished_ids.filtered(lambda m: m.state == 'done')
            materials = mo._hakbani_material_cost(raw)
            operations = sum(wo._cal_cost() for wo in mo.workorder_ids)
            qty = sum(m.product_uom._compute_quantity(m.quantity, m.product_id.uom_id)
                      for m in finished if m.product_id == mo.product_id)
            additional = mo.extra_cost * qty
            total = materials + operations + additional
            main_moves = finished.filtered(lambda m: m.product_id == mo.product_id)
            byproduct_moves = finished - main_moves
            main_value = sum(sum(m.stock_valuation_layer_ids.mapped('value')) for m in main_moves)
            byproduct_value = sum(sum(m.stock_valuation_layer_ids.mapped('value')) for m in byproduct_moves)
            difference = total - main_value - byproduct_value
            currency = mo.company_id.currency_id
            if not finished:
                status = 'pending'
            elif mo.product_id.cost_method == 'standard':
                status = 'standard'
            elif currency.is_zero(difference):
                status = 'matched'
            else:
                status = 'review'
            mo.update({
                'hakbani_raw_cost': materials,
                'hakbani_operation_cost': operations,
                'hakbani_additional_cost': additional,
                'hakbani_total_cost': total,
                'hakbani_finished_value': main_value,
                'hakbani_byproduct_value': byproduct_value,
                'hakbani_valuation_difference': difference,
                'hakbani_cost_status': status,
            })

    def action_hakbani_open_valuation(self):
        self.ensure_one()
        move_ids = (self.move_raw_ids | self.move_finished_ids).ids
        return {
            'name': _('Manufacturing Valuation Layers'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.valuation.layer',
            'view_mode': 'tree,form',
            'domain': [('stock_move_id', 'in', move_ids)],
            'context': {'search_default_group_by_product_id': 1},
        }

    def action_hakbani_open_entries(self):
        self.ensure_one()
        move_ids = (self.move_raw_ids | self.move_finished_ids).ids
        layers = self.env['stock.valuation.layer'].search([('stock_move_id', 'in', move_ids)])
        entries = layers.mapped('account_move_id')
        return {
            'name': _('Manufacturing Accounting Entries'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', entries.ids)],
        }
