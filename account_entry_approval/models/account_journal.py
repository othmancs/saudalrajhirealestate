# -*- coding: utf-8 -*-


from odoo import models, fields, _
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = "account.journal"


    def _get_approval_account_manager_ids(self):
        user_ids = self.env['res.users'].search([])
        account_manager_ids = user_ids.filtered(lambda l: l.has_group('account.group_account_manager'))
        return [('id', 'in', account_manager_ids.ids)]

    def _get_post_account_manager_ids(self):
        user_ids = self.env['res.users'].search([])
        account_manager_ids = user_ids.filtered(lambda l: l.has_group('account.group_account_manager'))
        return [('id', 'in', account_manager_ids.ids)]

    entry_approval_user_ids = fields.Many2many(
        "res.users",'entry_user_ids_rel',
        copy=False,
        domain=_get_approval_account_manager_ids,
        tracking=True,
    )

    entry_post_user_ids = fields.Many2many(
        "res.users",'entry_post_user_ids_rel',
        copy=False,
        domain=_get_post_account_manager_ids,
        tracking=True,
    )