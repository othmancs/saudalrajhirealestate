# -*- coding: utf-8 -*-

from odoo import models, fields


class TenderRecommendationWizard(models.TransientModel):
    _name = 'tender.recommendation.wizard'
    _description = 'Tender  Recommendation Wizard'

    recommendation = fields.Text(string='Recommendation', required=True)
    recommendation_state = fields.Selection([('recommend', 'Recommended'), ('not_recommend', 'Not Recommend')],
                                            string='Action', required=True)

    def action_recommendation(self):
        model = self._context.get('active_model')
        record_id = self._context.get('active_id')
        requisition_id = self.env[model].browse(record_id)
        if requisition_id:
            vals = {
                'user_id': self.env.user.id,
                'recommendation': self.recommendation,
                'recommendation_state': self.recommendation_state,
                'recommendation_date': fields.Date.today(),
                'requisition_id': requisition_id.id
            }
            self.env['purchase.requisition.recommendation'].create(vals)
        return
