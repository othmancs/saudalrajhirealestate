# -*- coding: utf-8 -*-


from traceback import print_tb
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date


class AccountMove(models.Model):
    _inherit = "account.move"

    state = fields.Selection(
        selection_add=[('waiting_approval', 'Waiting For Approval'),
                       ('second_approval', 'Waiting For Approval'),
                       ('approved', 'Approved'),
                       ('rejected', 'Rejected')],
        ondelete={'waiting_approval': 'set default', 'second_approval': 'set default', 'approved': 'set default', 'rejected': 'set default'})


class AccountPayment(models.Model):
    _inherit = "account.payment"
    _inherits = {'account.move': 'move_id'}

    approval_ids = fields.One2many('account.payment.approvals', 'payment_id')
    paid_through = fields.Selection([('transfer', 'Transfer'), ('cheque', 'Cheque'),
                                     ('cash', 'Cash')], default='transfer', string='Paid Through')
    cheque_number = fields.Char(string='Cheque No.')

    @api.depends('journal_id', 'payment_type', 'user_id')
    def _check_need_approve(self):
        # self.need_approve = True 
        self.user_for_approve = False 
        self.user_for_post = False 
        approval = self.env['ir.config_parameter'].sudo().get_param('account_payment_approval.payment_approval')
        if approval:
            if self.payment_type == 'outbound':
                outbound_approval = self.env['ir.config_parameter'].sudo().get_param('account_payment_approval.approval_outbound')
                if outbound_approval:
                    if self.journal_id.id in self.company_id.approval_outbound_journals.ids:
                        self.need_approve = True
                    else:
                        self.need_approve = False
                else:
                    self.need_approve = False
                
                if self.env.user.id in self.journal_id.outbound_user_ids.ids and self.state == 'second_approval':
                    self.user_for_approve = True

                if self.env.user.id in self.journal_id.outbound_accountant_ids.ids and self.state == 'waiting_approval':
                    self.user_for_approve = True
                
                if self.env.user.id in self.journal_id.outbound_post_user_ids.ids:
                    self.user_for_post = True

            elif self.payment_type == 'inbound':
                inbound_approval = self.env['ir.config_parameter'].sudo().get_param('account_payment_approval.approval_inbound')
                if inbound_approval:
                    if self.journal_id.id in self.company_id.approval_inbound_journals.ids:
                        self.need_approve = True
                    else:
                        self.need_approve = False
                else:
                    self.need_approve = False
            
                if self.env.user.id in self.journal_id.inbound_user_ids.ids and self.state == 'second_approval':
                    self.user_for_approve = True
                if self.env.user.id in self.journal_id.inbound_accountant_ids.ids and self.state == 'waiting_approval':
                    self.user_for_approve = True

                if self.env.user.id in self.journal_id.inbound_post_user_ids.ids:
                    self.user_for_post = True
        else :
            self.need_approve = False

    is_approver = fields.Boolean(readonly=True)

    need_approve = fields.Boolean(compute=_check_need_approve, readonly=True)
    user_for_approve = fields.Boolean(compute=_check_need_approve, readonly=True)
    user_for_post = fields.Boolean(compute=_check_need_approve, readonly=True)

    def add_approval(self, action):
        self.write({
            'approval_ids': [(0, 0, {'user_id': self.env.user.id, 'action': action,
                                     'approval_date': date.today()})],
        })

    def action_post(self):
        """Overwrites the _post() to validate the payment in the 'approved' stage too.
        Currently Odoo allows payment posting only in draft stage.
        """
        if self.need_approve and self.state not in ['second_approval', 'approved']:
            self.state = 'waiting_approval'
            self.add_approval('create')
        else:
            self.move_id._post(soft=False)
            self.filtered(
                lambda pay: pay.is_internal_transfer and not pay.paired_internal_transfer_payment_id
            )._create_paired_internal_transfer_payment()
            self.add_approval('post')

    def action_first_approval(self):
        self.write({
            'state': 'second_approval'
        })
        self.add_approval('approve')

    def action_second_approval(self):
        self.write({
            'state': 'approved'
        })
        self.add_approval('approve')

    def reject_transfer(self):
        self.write({
            'state': 'rejected'
        })

    def action_draft(self):
        res = super(AccountPayment, self).action_draft()
        self.approval_ids.unlink()