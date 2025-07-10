from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    unit_state = fields.Char(related='product_id.product_tmpl_id.unit_state', store=True)

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        try:
            if args is None:
                args = []
            args += [('unit_state', '=', False)]
            _logger.debug("Searching products with args: %s", args)
            return super()._name_search(
                name=name,
                args=args,
                operator=operator,
                limit=limit,
                name_get_uid=name_get_uid
            )
        except Exception as e:
            _logger.error("Error in _name_search: %s", str(e))
            raise

