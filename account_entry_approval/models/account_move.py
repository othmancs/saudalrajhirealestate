# -*- coding: utf-8 -*-


from traceback import print_tb
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    state = fields.Selection(
        selection_add=[('waiting_approval', 'Waiting For Approval'),
                       ('approved', 'Approved'),
                       ('rejected', 'Rejected')],
        ondelete={'waiting_approval': 'set default', 'approved': 'set default', 'rejected': 'set default'})
    
    is_approver = fields.Boolean(readonly=True)
    need_approve = fields.Boolean(compute="_check_need_approve", readonly=True)
    user_for_approve = fields.Boolean(compute="_check_need_approve", readonly=True)
    user_for_post = fields.Boolean(compute="_check_need_approve", readonly=True)
    show_post = fields.Boolean(string='',compute="_get_show")
    
    @api.depends('journal_id', 'move_type', 'user_id')
    def _check_need_approve(self):
        for record in self:
            self.need_approve = False
            self.user_for_approve = False
            self.user_for_post = False
            approval = self.env['ir.config_parameter'].sudo().get_param('account_entry_approval.entry_approval')


            if approval:
                # if record.move_type == 'entry':
                if record.journal_id.id in record.company_id.need_approval_journals.ids:
                    record.need_approve = True
                else:
                    record.need_approve = False
                # else:
                #     record.need_approve = False

                if self.env.user.id in record.journal_id.entry_approval_user_ids.ids:
                    record.user_for_approve = True

                if self.env.user.id in record.journal_id.entry_post_user_ids.ids:
                    record.user_for_post = True

        
    def _get_show(self):
        if self.need_approve:
            if self.state in ('draft','approved') and self.user_for_approve == True and self.auto_post == False and self.need_approve == True :
                self.show_post = True

            else :
                self.show_post = False
        elif not self.need_approve and self.state in ('draft','approved'):
                self.show_post = True
        else : 
            self.show_post = False

    def action_post(self):
        """Overwrites the _post() to validate the payment in the 'approved' stage too.
        Currently Odoo allows payment posting only in draft stage.
        """
        # res = super(AccountMove, self).action_post()
        for record in self:
            if record.need_approve:
                print("dfdfdfdf", record.state)
                if record.state == 'approved':
                    self._post(soft=False)
                else:
                    record.state = 'waiting_approval'
            else:
                if record.state not in ['posted', 'cancel', 'rejected']:
                    self._post(soft=False)

    def approve_transfer(self):
        self.write({
            'state': 'approved'
        })

    def reject_transfer(self):
        self.write({
            'state': 'rejected'
        })
