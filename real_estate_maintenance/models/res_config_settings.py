from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'
    maintenance_request_to_notify_user_id = fields.Many2many("res.users")
    invoice_product_id = fields.Many2one("product.product")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    maintenance_request_to_notify_user_id = fields.Many2many(related="company_id.maintenance_request_to_notify_user_id",
                                                            readonly=False)
    invoice_product_id = fields.Many2one(related="company_id.invoice_product_id",
                                         readonly=False)
