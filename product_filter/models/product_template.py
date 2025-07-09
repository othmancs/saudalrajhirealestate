from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    unit_state = fields.Char(string='Unit State', help="State of the product unit")
