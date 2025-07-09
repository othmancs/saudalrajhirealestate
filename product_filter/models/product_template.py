from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    unit_state = fields.Char(string='Unit State', related='product_variant_ids.unit_state')