from odoo import fields, models, api


class StockRequest(models.Model):
    _inherit = 'stock.request'

    maintenance_request_id = fields.Many2one('maintenance.request')
