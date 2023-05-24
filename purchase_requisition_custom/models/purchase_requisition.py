# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    locked = fields.Boolean(string='Locked')
    recommendation_line_ids = fields.One2many('purchase.requisition.recommendation', 'requisition_id')
    can_recommend = fields.Boolean(compute="_can_recommend")

    @api.depends('recommendation_line_ids', 'recommendation_line_ids.user_id')
    def _can_recommend(self):
        for record in self:
            user_ids = record.company_id.recommender_ids.ids
            recommended_user_ids = record.recommendation_line_ids.mapped('user_id').ids
            if self.env.user.id in user_ids and self.env.user.id not in recommended_user_ids:
                record.can_recommend = True
            else:
                record.can_recommend = False

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