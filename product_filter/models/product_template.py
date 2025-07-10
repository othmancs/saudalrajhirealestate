from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    unit_state = fields.Boolean(related='product_id.unit_state', store=True, readonly=True)
