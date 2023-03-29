from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    maintenance_request_id = fields.Many2one('maintenance.request')
