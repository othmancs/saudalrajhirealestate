# -*- coding: utf-8 -*-


from odoo import models, fields, _
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = "account.journal"

    def _get_inbound_user_ids_account_manager_ids(self):
        inbound_user_ids = self.env['res.users'].search([])
        account_manager_ids = inbound_user_ids.filtered(
            lambda l: l.has_group('account.group_account_manager'))
        return [('id', 'in', account_manager_ids.ids)]

    def _get_outbound_user_ids_account_manager_ids(self):
        inbound_user_ids = self.env['res.users'].search([])
        account_manager_ids = inbound_user_ids.filtered(
            lambda l: l.has_group('account.group_account_manager'))
        return [('id', 'in', account_manager_ids.ids)]

    def _get_accountant_ids(self):
        user_ids = self.env['res.users'].search([])
        accountant_ids = user_ids.filtered(
            lambda l: l.has_group('account.group_account_user'))
        return [('id', 'in', accountant_ids.ids)]

    inbound_user_ids = fields.Many2many("res.users",'inbound_journals_users_rel', 'x_id', 'journal_id',
                                        string="Second Approval Users", copy=False, domain=_get_inbound_user_ids_account_manager_ids, tracking=True)
    inbound_accountant_ids = fields.Many2many("res.users",'inbound_journals_accountant_rel', 'x_id', 'journal_id', string="First Approval Users", copy=False, domain=_get_accountant_ids, tracking=True)
    inbound_post_user_ids = fields.Many2many("res.users",'inbound_post_journals_users_rel', 'x_id', 'journal_id', string="Post Users", copy=False, domain=_get_inbound_user_ids_account_manager_ids, tracking=True)

    outbound_accountant_ids = fields.Many2many("res.users",'outbound_journals_accountant_rel', 'x_id', 'journal_id',
                                               string="First Approval Users", copy=False, domain=_get_accountant_ids, tracking=True)
    outbound_user_ids = fields.Many2many("res.users", 'outbound_journals_users_rel', 'x_id', 'journal_id',
                                         string="Second Approval Users", copy=False, domain=_get_outbound_user_ids_account_manager_ids, tracking=True)
    outbound_post_user_ids = fields.Many2many("res.users",'outbound_post_journals_users_rel', 'x_id', 'journal_id', string="Post Users", copy=False, domain=_get_inbound_user_ids_account_manager_ids, tracking=True)
