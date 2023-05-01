from odoo import fields, models, api


class PaymentApprovals(models.Model):
    _name = 'account.payment.approvals'
    _description = 'Account Payment Approvals'

    user_id = fields.Many2one('res.users', string='Approver')
    approval_date = fields.Date(string='Approval Date')
    payment_id = fields.Many2one('account.payment')
    action = fields.Selection([('create', 'Create'), ('approve', 'Approve'), ('post', 'Post')],
                              string='Action Type')
