# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class RentalReport(models.Model):
    _inherit = "sale.rental.report"

    property_id = fields.Many2one('rent.property', string='عقارات', readonly=True)
    state_id = fields.Char(string='حالة العقار')
    property_address_build = fields.Many2one('rent.property.build', string='المجمع')
    property_address_city = fields.Many2one('rent.property.city',string='المدينة')
    country = fields.Many2one('res.country', string='الدولة')
    fromdate = fields.Date()
    todate = fields.Date()

    def _select(self):
        return super(RentalReport, self)._select() + """,
            pt.state_id,
            pt.property_id,
            pt.property_address_build,
            pt.property_address_city,
            pt.country,
            sol.fromdate,
            sol.todate
        """
