# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductPendingOrdersWizard(models.TransientModel):
    _name = 'product.pending.orders'
    _rec_name = 'product_id'

    product_pending_order_ids = fields.Many2many('stock.request.line',
                                           string='Product Pending Orders',
                                           help="shows the product pending orders")
    product_id = fields.Many2one('product.product', string="Product:")


