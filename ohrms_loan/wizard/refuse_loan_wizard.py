from odoo import api, fields, models, _


class RefuseLoanWizard(models.TransientModel):
    _name = 'refuse.loan.wizard'
    _description = 'Refuse Loan wizard'

    refuse_reason = fields.Text(
        string='Reason',
        required=True,
        readonly=False,
    )

    def confirm(self):
        if self.env.context.get('active_id'):
            active_id = self.env.context.get('active_id')
            loan_id = self.env['hr.loan'].browse(active_id)
            loan_id.write({
                'refuse_reason': self.refuse_reason,
                'date_refuse': fields.datetime.now(),
                'state': 'refuse',
            })
