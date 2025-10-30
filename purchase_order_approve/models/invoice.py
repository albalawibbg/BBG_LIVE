from odoo import fields, models, api, _, SUPERUSER_ID
from odoo.exceptions import ValidationError

from markupsafe import Markup


class PurchaseOrder(models.Model):
    _inherit = 'account.move'
    is_creator = fields.Boolean( compute='compute_creator' )
    def compute_creator(self):
        for rec in self:
                rec.is_creator = rec.create_uid == self.env.user
    def action_submit(self):
        for rec in self:
            if rec.move_type == 'in_invoice':
                message = f"You has been assigned to Approve the Invoice: {rec.name}."
                users = self.env.ref('purchase_order_approve.group_purchase_gm_approval').users
                rec.create_activity(users, message)
                rec.state = 'submitted'
    def action_gm_approve(self):
        for order in self:
            if order.move_type == 'in_invoice':
                message = f"You has been assigned to Approve the Invoice: {order.name}."
                users = self.env.ref('purchase_order_approve.group_purchase_cfo_approval').users
                order.create_activity(users, message)
                order.state = "gm_approved"

    def action_cfo_approve(self):
        for order in self:
            if order.move_type == 'in_invoice':
                message = f"You has been assigned to Confirm the Invoice: {order.name}."
                users = self.env.ref('account.group_account_manager').users
                order.create_activity(users, message)
                order.state = "cfo_approved"

    def button_draft(self):
        for rec in self:
            if rec.state == 'rejected':
                rec.state='cancel'
        super().button_draft()
        for rec in self:
            if rec.move_type == 'in_invoice':
                if self.env.user.id != rec.create_uid.id:
                    message = f"You Invoice: {rec.name} has been set to draft."
                    users = rec.create_uid
                    rec.create_activity(users, message)

    state = fields.Selection(
        selection_add=[('submitted', 'Submitted'),('draft',),
        ('gm_approved', 'GM Approved'),('draft',),
        ('cfo_approved', 'CFO Approved'),('draft',),
         ('rejected', 'Rejected')],
        ondelete={'rejected': 'set default','submitted': 'set default','gm_approved': 'set default','cfo_approved': 'set default'}
    )
    def create_activity(self,users,message):
        for record in self:
            if not record.invoice_date:
                raise ValidationError(_("Enter Bill Date"))
            if users:
                # Construct the notification message
                for user in users:
                    todos = {
                        'res_id': record.id,
                        'res_model_id': self.env['ir.model'].search([('model', '=', 'account.move')]).id,
                        'user_id': user.id,
                        'summary': 'Invoice Assignment',
                        'note': message,
                        'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                        'date_deadline': record.invoice_date,
                    }
                    self.env['mail.activity'].create(todos)

                    # # Send a real-time notification to the project manager
                    # self.env['bus.bus']._sendone(
                    #     user.partner_id.id,
                    #     'simple_notification',
                    #     {
                    #         'title': 'Purchase Order',
                    #         'message': message,
                    #         'sticky': False,  # False means the notification disappears after a few seconds
                    #     }
                    # )

    def button_gm_reject(self):
        for rec in self:
            if rec.move_type == 'in_invoice':
                message = f"Your Invoice :{rec.name} has been Rejected ."
                users = rec.create_uid
                rec.create_activity(users, message)
                rec.state='rejected'
    def button_cfo_reject(self):
        for rec in self:
            if rec.move_type == 'in_invoice':
                message = f"Your Invoice:{rec.name} has been Rejected ."
                users = rec.create_uid
                rec.create_activity(users, message)
                rec.state='rejected'


