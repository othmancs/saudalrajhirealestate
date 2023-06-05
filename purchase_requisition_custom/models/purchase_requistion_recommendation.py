from odoo import fields, models, api


class PurchaseRequisitionRecommendations(models.Model):
    _name = 'purchase.requisition.recommendation'
    _description = 'Purchase Requisition Recommendation'
    _rec_name = 'user_id'

    user_id = fields.Many2one('res.users')
    recommendation = fields.Text(string='Recommendation', required=True)
    recommendation_state = fields.Selection([('recommend', 'Recommended'), ('not_recommend', 'Not Recommend')],
                                            string='Action')
    requisition_id = fields.Many2one('purchase.requisition')
    recommendation_date = fields.Date(string="Recommendation Date")
