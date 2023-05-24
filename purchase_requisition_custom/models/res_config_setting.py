from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    recommender_ids = fields.Many2many('res.users', 'user_recommends_rel', 'x_id', 'user_id',string='Recommenders')


class PurchaseConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    recommender_ids = fields.Many2many('res.users', 'user_recommends_rel', 'x_id', 'user_id', string='Recommenders',
                                       related="company_id.recommender_ids", readonly=False)
