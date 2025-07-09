from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    @api.onchange('product_id')
    def _onchange_product_id_filter(self):
        if self.product_id and self.product_id.unit_state:
            return {
                'warning': {
                    'title': "Product Not Available",
                    'message': "This product cannot be selected because it has a unit state.",
                },
                'value': {'product_id': False},
            }
    
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('from_sale_order'):
            args += [('unit_state', '=', False)]
        return super(SaleOrderLine, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)