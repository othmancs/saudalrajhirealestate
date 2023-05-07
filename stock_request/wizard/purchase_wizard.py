# -*- coding: utf-8 -*-

from email.policy import default
from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    stock_request_id = fields.Many2one(comodel_name='stock.request', string='')
      
    def button_confirm(self):
        super(PurchaseOrder, self).button_confirm()
        if self.stock_request_id:
            for l in self.order_line:
                l.request_line_id.transfer_status = "purchased"
                l.request_line_id.purchased_qty = l.product_qty
        
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    request_line_id = fields.Many2one(
        comodel_name='stock.request.line', string='')

    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        self.ensure_one()
        self._check_orderpoint_picking_type()
        product = self.product_id.with_context(lang=self.order_id.dest_address_id.lang or self.env.user.lang)
        date_planned = self.date_planned or self.order_id.date_planned
        return {
            # truncate to 2000 to avoid triggering index limit error
            # TODO: remove index in master?
            'name': (self.name or '')[:2000],
            'product_id': self.product_id.id,
            'date': date_planned,
            'date_deadline': date_planned,
            'request_line_id': self.request_line_id.id,
            'location_id': self.order_id.partner_id.property_stock_supplier.id,
            'location_dest_id': (self.orderpoint_id and not (self.move_ids | self.move_dest_ids)) and self.orderpoint_id.location_id.id or self.order_id._get_destination_location(),
            'picking_id': picking.id,
            'partner_id': self.order_id.dest_address_id.id,
            'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
            'state': 'draft',
            'purchase_line_id': self.id,
            'company_id': self.order_id.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': self.order_id.picking_type_id.id,
            'group_id': self.order_id.group_id.id,
            'origin': self.order_id.name,
            'description_picking': product.description_pickingin or self.name,
            'propagate_cancel': self.propagate_cancel,
            'warehouse_id': self.order_id.picking_type_id.warehouse_id.id,
            'product_uom_qty': product_uom_qty,
            'product_uom': product_uom.id,
            'product_packaging_id': self.product_packaging_id.id,
        }
  
class PurchaseWizard(models.TransientModel):
    _name = 'purchase.wizard'
 
    partner_id = fields.Many2one(comodel_name='res.partner',domain=[('supplier_rank','>',0)], string='Vendor')
    qty = fields.Float(string='Quantity')
    date = fields.Datetime(string='Deadline Time',
                           default=fields.Datetime.now())
    
    def do_order(self):
        active_request = self.env.context.get('stock_request_id')
        active_line = self.env.context.get('active_id')
        obj = self.env['stock.request'].browse(active_request)
        line_object = self.env['stock.request.line'].browse(active_line)
        picking_type_id = self.env['stock.picking.type'].search([('code', '=', 'incoming'),('return_picking_type_id','!=', False)])
        order_id = self.env['purchase.order'].search(
            [('stock_request_id', '=', obj.id),('partner_id','=',self.partner_id.id),('state','=', 'draft')])
        if not order_id:
            order = {
                'partner_id': self.partner_id.id,
                'date_order': self.date,
                'picking_type_id': picking_type_id.id,
                'stock_request_id': active_request,
                # 'warehouse_id': self.branch_id.warehouse_id.id,
            }
            order_id = self.env['purchase.order'].create(order)
        for rec in self:
            self.env['purchase.order.line'].create({
                'product_id': line_object.product_id.id,
                'product_qty': self.qty,
                'order_id': order_id.id,
                'request_line_id': line_object.id,
            })
        line_object.transfer_status = 'purchase'