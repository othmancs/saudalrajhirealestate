from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    unit_information_id = fields.Many2one('unit.information', string='Unit Information')

    sale_visible = fields.Boolean(string='Visible in Sales', compute='_compute_sale_visible')

    @api.depends('unit_information_id.unit_state')
    def _compute_sale_visible(self):
        for rec in self:
            # يعرض المنتج فقط إذا كانت قيمة unit_state هي "شاغرة"
            unit_state = rec.unit_information_id.unit_state if rec.unit_information_id else ''
            rec.sale_visible = (unit_state == 'شاغرة')