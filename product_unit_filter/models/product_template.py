from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sale_visible = fields.Boolean(
        string='Visible in Sales',
        compute='_compute_sale_visible',
        store=True
    )

    @api.depends('unit_state')
    def _compute_sale_visible(self):
        for rec in self:
            rec.sale_visible = rec.unit_state == 'شاغرة'
