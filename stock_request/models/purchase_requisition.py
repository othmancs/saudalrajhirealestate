# -*- coding: utf-8 -*-

from odoo import models, fields, _


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    request_id = fields.Many2one(comodel_name='stock.request', string='Request')