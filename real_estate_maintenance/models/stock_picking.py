from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    maintenance_request_id = fields.Many2one('maintenance.request')
