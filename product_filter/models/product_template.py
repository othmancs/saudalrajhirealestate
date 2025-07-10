from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    unit_state = fields.Boolean(string="Unit State")
