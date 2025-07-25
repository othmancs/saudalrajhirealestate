from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    analytic_group = fields.Many2one('account.analytic.group', related='analytic_account_id.group_id', store=True)
