# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.constrains('state', 'location_id', 'location_dest_id')
    def check_user_location_rights(self):
        for move in self:
            user_locations = move.env.user.stock_location_ids
            if move.env.user.restrict_locations and move.env.user.stock_location_ids and move.state == "done":
                if move.location_dest_id not in user_locations:
                    raise ValidationError(
                        'You cannot process this move since you do not have control on destination location')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        user_locations = self.env.user.stock_location_ids
        if self.env.user.restrict_locations:
            if user_locations:
                if self.location_id not in user_locations:
                    raise ValidationError('You cannot process this move since you do not have control on destination')
        return res
