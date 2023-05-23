from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    agreement_no = fields.Integer(string='Agreements No.', required=True, default=3)
    picking_type_id = fields.Many2one('stock.picking.type', string='Operation Type',
                                      domain=[('code', '=', 'internal')])
    location_dest_id = fields.Many2one('stock.location', string='Destination Location', readonly=False,
                                       domain="[('usage', '=', 'internal')]")
    purchase_operation_type = fields.Selection([('tender', 'Make Tender'), ('rfq', 'Make RFQ')],
                                               default='tender')


class PurchaseConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    agreement_no = fields.Integer(string='Agreements No.', required=True,
                                  related='company_id.agreement_no', readonly=False)
    picking_type_id = fields.Many2one('stock.picking.type', related='company_id.picking_type_id',
                                      string='Operation Type', readonly=False,
                                      domain=[('code', '=', 'internal')])
    location_dest_id = fields.Many2one('stock.location', related='company_id.location_dest_id',
                                       string='Destination Location', readonly=False,
                                       domain="[('usage', '=', 'internal')]")
    purchase_operation_type = fields.Selection([('tender', 'Make Tender'), ('rfq', 'Make RFQ')],
                                               related='company_id.purchase_operation_type',
                                               string='Purchase Operation Type', readonly=False,
                                               )
