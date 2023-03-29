from odoo import fields, models, api


class MaintenanceRequestProduct(models.Model):
    _name = 'maintenance.request.product'
    _description = 'Property Maintenance Request Product'

    @api.model
    def _get_default_location_src_id(self):
        company_id = self.env.context.get('default_company_id', self.env.company.id)
        location = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1).lot_stock_id
        return location and location.id or False

    maintenance_request_id = fields.Many2one('maintenance.request')
    location_id = fields.Many2one("stock.location", "Stock Location", required=1,
                                  domain=[('usage', '=', 'internal')],
                                  default=_get_default_location_src_id)
    product_id = fields.Many2one("product.product", "Product", domain=[('partner_id', '=', False),
                                                                       ('detailed_type', '=', 'product')])
    quantity = fields.Float("Quantity", digits="Product Unit Of Measure")

    def get_move_vals(self, picking, group):
        self.ensure_one()

        return {
            'name': self.product_id and self.product_id.name or 'Warehouse Transfer',
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_id.id,
            'product_uom_qty': self.quantity,
            'picking_id': picking.id,
            'group_id': group.id,
        }
