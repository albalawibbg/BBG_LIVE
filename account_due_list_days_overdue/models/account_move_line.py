# Copyright 2016 ForgeFlow S.L. (
#   (<http://www.forgeflow.com>).
# Copyright 2016 Therp BV (<http://therp.nl>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import datetime

from lxml import etree

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    days_overdue = fields.Integer(
        compute="_compute_days_overdue",
        search="_search_days_overdue",
        string="Days overdue",
    )

    @api.depends("date_maturity", "amount_residual")
    def _compute_days_overdue(self):
        today_date = fields.Date.context_today(self)
        for line in self:
            days = False
            if line.date_maturity and line.amount_residual:
                date_maturity = fields.Date.to_date(line.date_maturity)
                days_overdue = (today_date - date_maturity).days
                if days_overdue > 0:
                    days = days_overdue
            line.days_overdue = days

    def _search_days_overdue(self, operator, value):
        if operator in ("!=", "<>", "in", "not in"):
            raise ValueError("Invalid operator: {}".format(operator))
        try:
            value = int(value)
        except (TypeError, ValueError) as error:
            raise ValueError("Days overdue value must be an integer") from error

        due_date = fields.Date.context_today(self) - datetime.timedelta(days=value)
        if operator == ">":
            operator = "<"
        elif operator == "<":
            operator = ">"
        elif operator == ">=":
            operator = "<="
        elif operator == "<=":
            operator = ">="
        return [("date_maturity", operator, due_date)]

    @api.depends("date_maturity", "amount_residual")
    def _compute_overdue_terms(self):
        today_date = fields.Date.context_today(self)
        overdue_terms = self.env["account.overdue.term"].search([])
        for line in self:
            for term in overdue_terms:
                field_name = term._get_technical_name()
                if field_name in line._fields:
                    line[field_name] = 0.0
            if line.date_maturity and line.amount_residual:
                date_maturity = fields.Date.to_date(line.date_maturity)
                days_overdue = (today_date - date_maturity).days

                for overdue_term in overdue_terms:
                    field_name = overdue_term._get_technical_name()
                    if field_name not in line._fields:
                        continue
                    if (
                        overdue_term.to_day >= days_overdue >= overdue_term.from_day
                        and abs(line.amount_residual) > 0.0
                    ):
                        line[field_name] = line.amount_residual

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(
            view_id=view_id, view_type=view_type, **options
        )
        if view_type in ("tree", "list"):
            overdue_terms = self.env["account.overdue.term"].search(
                [], order="from_day DESC"
            )
            for placeholder in arch.xpath("//field[@name='days_overdue']"):
                for overdue_term in overdue_terms:
                    field_name = overdue_term._get_technical_name()
                    if field_name not in self._fields:
                        continue
                    elem = etree.Element(
                        "field",
                        {
                            "name": field_name,
                            "readonly": "1",
                            "sum": "Total",
                            "optional": "show",
                        },
                    )
                    placeholder.addnext(elem)
        return arch, view

    @api.model
    def _add_terms(self, field_name, term_name):
        if field_name in self._fields:
            return False
        self._add_field(
            field_name,
            fields.Float(string=term_name, compute="_compute_overdue_terms"),
        )
        return True

    def _register_hook(self):
        term_obj = self.env["account.overdue.term"]
        added = False
        for term in term_obj.search([]):
            field_name = term._get_technical_name()
            added = self._add_terms(field_name, term.name) or added
        if added:
            self._setup_fields()
            self._setup_complete()
        return super()._register_hook()
