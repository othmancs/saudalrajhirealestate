# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, tools


class RentalReport(models.Model):
    _inherit = "sale.rental.report"
 

    def _price(self):
        return """
            sol.price_subtotal / (date_part('day',sol.return_date::timestamp - sol.pickup_date::timestamp) + 1)
        """