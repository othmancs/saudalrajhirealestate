# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    locked = fields.Boolean(string='Locked')

    def action_open(self):
        for rec in self.env['purchase.requisition'].search([('id', 'not in', self.ids),('request_id', '=', self.request_id.id)]):
            rec.action_cancel()
        self.request_id.button_done()
        self.write({'state': 'open'})

    def action_cancel(self):
        for rec in self:
            if rec.locked == True:
                raise  ValidationError(_("You Can not Do this Action Which Request Had been Confirmed "))
        return super().action_cancel()

    def action_draft(self):
        for rec in self:
            if rec.locked == True:
                raise  ValidationError(_("You Can not Do this Action Which Request Had been Confirmed "))
        return super(self, PurchaseRequisition).action_draft()