# Copyright 2016 ForgeFlow S.L.
#   (<http://www.forgeflow.com>).
# Copyright 2016 Therp BV (<http://therp.nl>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, exceptions, fields, models


class AccountDaysOverdue(models.Model):
    _name = "account.overdue.term"
    _description = "Account Overdue Term"

    name = fields.Char(size=10, required=True)
    from_day = fields.Integer(string="From day", required=True)
    to_day = fields.Integer(string="To day", required=True)
    tech_name = fields.Char(
        string="Technical name",
        readonly=True,
        compute="_compute_technical_name",
        store=True,
    )

    def _get_technical_name(self):
        self.ensure_one()
        # Odoo 17 only accepts dynamically added field names that are
        # Python-defined fields or valid custom/manual field names.
        return "x_overdue_term_%d_%d" % (self.from_day, self.to_day)

    @api.depends("from_day", "to_day")
    def _compute_technical_name(self):
        for rec in self:
            rec.tech_name = rec._get_technical_name()

    def init(self):
        """Normalize stored technical names when upgrading from older versions."""
        self.env.cr.execute(
            """
            UPDATE account_overdue_term
               SET tech_name = 'x_overdue_term_' || from_day || '_' || to_day
             WHERE tech_name IS NULL
                OR tech_name NOT LIKE 'x_overdue_term_%'
            """
        )

    def _refresh_account_move_line_terms(self):
        self.env["account.move.line"]._register_hook()
        self.env.registry.registry_invalidated = True

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._refresh_account_move_line_terms()
        return records

    def write(self, vals):
        res = super().write(vals)
        self._refresh_account_move_line_terms()
        return res

    def unlink(self):
        res = super().unlink()
        self.env.registry.registry_invalidated = True
        return res

    @api.constrains("from_day", "to_day")
    def check_overlap(self):
        """Check that overdue terms do not overlap."""
        for rec in self:
            if rec.from_day < 0 or rec.to_day < 0:
                raise exceptions.ValidationError(
                    _("Overdue term days must be positive numbers.")
                )
            if rec.from_day > rec.to_day:
                raise exceptions.ValidationError(
                    _("From day must be lower than or equal to To day.")
                )
            date_domain = [
                ("from_day", "<=", rec.to_day),
                ("to_day", ">=", rec.from_day),
                ("id", "!=", rec.id),
            ]
            overlap = self.search(date_domain, limit=1)
            if overlap:
                raise exceptions.ValidationError(
                    _("Overdue Term %(rec_name)s overlaps with %(overlap_name)s")
                    % {"rec_name": rec.name, "overlap_name": overlap.name}
                )
