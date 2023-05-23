# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class IRAttachment(models.Model):
    _inherit = "ir.attachment"
    #Todo: Abdulrhman: Remove IT
    rental_type = fields.Selection( string='Rental Type', selection=[('receipt', 'receipt'), ('delivery', 'delivery')])


class RentSaleState(models.Model):
    _inherit = "rent.sale.state"
    _rec_name = 'sale_order_line_id'

    supported_attachment_ids = fields.Many2many(comodel_name='ir.attachment', relation="supported_attachment_rel",
                                                string='Attachments')
    receipt_attachment_ids = fields.Many2many(comodel_name='ir.attachment', relation="receipt_attachment_rel",
                                              string='Attachments')
    delivery_attachment_ids = fields.Many2many(comodel_name='ir.attachment', relation="delivery_attachment_rel",
                                               string='Attachments')
