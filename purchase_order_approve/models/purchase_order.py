from odoo import fields, models, api, _, SUPERUSER_ID
from odoo.exceptions import ValidationError

from markupsafe import Markup


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    is_creator = fields.Boolean( compute='compute_creator' )
    def compute_creator(self):
        for rec in self:
            rec.is_creator = rec.create_uid == self.env.user
    def action_submit(self):
        for rec in self:
            message = f"You has been assigned to Approve the Purchase Order: {rec.name}."
            users = self.env.ref('purchase_order_approve.group_purchase_gm_approval').users
            rec.create_activity(users, message)
            rec.state = 'submitted'
    def action_gm_approve(self):
        for order in self:
            message = f"You has been assigned to Approve the Purchase Order: {order.name}."
            users = self.env.ref('purchase_order_approve.group_purchase_cfo_approval').users
            order.create_activity(users, message)
            order.state = "gm_approved"
    def action_cfo_approve(self):
        for order in self:
            message = f"You has been assigned to Confirm the Purchase Order: {order.name}."
            users = self.env.ref('account.group_account_manager').users
            order.create_activity(users, message)
            order.state = "cfo_approved"
    def button_draft(self):
        super().button_draft()
        for rec in self:
            if self.env.user.id != rec.create_uid.id:
                message = f"You Order: {rec.name} has been set to draft."
                users = rec.create_uid
                rec.create_activity(users, message)

    state = fields.Selection(
        selection_add=[('submitted', 'Submitted'),('sent',),
        ('gm_approved', 'GM Approved'),('sent',),
        ('cfo_approved', 'CFO Approved'),('sent',),
         ('rejected', 'Rejected')],
        ondelete={'rejected': 'set default','gm_approved': 'set default','cfo_approved': 'set default'}
    )
    def create_activity(self,users,message):
        for record in self:
            if users:
                # Construct the notification message
                for user in users:
                    todos = {
                        'res_id': record.id,
                        'res_model_id': self.env['ir.model'].search([('model', '=', 'purchase.order')]).id,
                        'user_id': user.id,
                        'summary': 'Purchase Order Assignment',
                        'note': message,
                        'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                        'date_deadline': record.date_order,
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
            message = f"Your Purchase order:{rec.name} has been Rejected ."
            users = rec.create_uid
            rec.create_activity(users, message)
            rec.state='rejected'
    def button_cfo_reject(self):
        for rec in self:
            message = f"Your Purchase order:{rec.name} has been Rejected ."
            users = rec.create_uid
            rec.create_activity(users, message)
            rec.state='rejected'
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent','cfo_approved']:
                continue
            order.order_line._validate_analytic_distribution()
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True

