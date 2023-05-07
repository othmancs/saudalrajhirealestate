# -*- coding: utf-8 -*-

from traceback import print_tb
from odoo import models, fields, _


class ProductQuantity(models.TransientModel):
    _name = 'product.quantity'

    quant_id = fields.Many2many(
        'stock.quant', string="Location", compute="_compute_stock_quant_ids")


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    transfer_qty = fields.Float(string='Transfer Quantity')

    def do_transfer(self):
        active_request = self.env.context.get('stock_request_id')
        obj = self.env['stock.request'].browse(active_request)
        if self.transfer_qty > 0:
            picking_type_id = self.env['stock.picking.type'].search(
                [('code', '=', 'internal'), ('default_location_src_id', '=', self.location_id.id)])
            picking_id = self.env['stock.picking'].search([('stock_request_id', '=', obj.id), ('state', '=', 'draft'), ('location_id', '=', self.location_id.id), ('location_dest_id', '=', obj.location_dest_id.id)])
            if not picking_id:
                picking = {
                    'company_id': obj.company_id.id,
                    'location_id': self.location_id.id,
                    'location_dest_id': obj.location_dest_id.id,
                    'stock_request_id': obj.id,
                    'picking_type_id': picking_type_id.id
                }
                picking_id = self.env['stock.picking'].create(picking)
            line_id = [
                x.id for x in obj.lines if x.product_id == self.product_id]
            request_line_id = self.env["stock.request.line"].sudo().browse(
                line_id[0])
            if not (request_line_id.qty_in_transfer + self.transfer_qty > request_line_id.qty):
                dd = self.env['stock.move'].create({
                    'picking_id': picking_id.id,
                    'product_id': self.product_id.id,
                    'product_uom': self.product_id.uom_id.id,
                    'product_uom_qty': self.transfer_qty,
                    'request_line_id': line_id[0],
                    'name': self.product_id.name,
                    'location_id': self.location_id.id,
                    'location_dest_id': obj.location_dest_id.id,
                })
                print(dd)
                self.transfer_qty = 0
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'info',
                        'sticky': False,
                        'message': _("Transfer Created Successfully"),
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'warning',
                        'sticky': False,
                        'message': _("Cannot create transfer with quantity greater than approved!"),
                    }
                }
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'warning',
                'sticky': False,
                'message': _("Cannot create transfer with quantity 0!"),
            }
        }
        # return {
        #     'name': 'Product Avilable Quantity',
        #     'view_mode': 'tree',
        #     'view_id': self.env.ref('stock_request.stock_quant_quantity_view').id,
        #     'res_model': 'stock.quant',
        #     'type': 'ir.actions.act_window',
        #     'target': 'new',
        #     'domain': [("product_id","=",self.product_id.id),("location_id","!=",obj.location_dest_id.id)],
        #     'context': {'search_default_internal_loc': 1,'stock_request_id':obj.id}
        # }
