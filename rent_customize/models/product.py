# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import config


class ProductTemplate(models.Model):
    _inherit = "product.template"
    partner_latitude = fields.Float(string='Geo Latitude', digits=(10, 7))
    partner_longitude = fields.Float(string='Geo Longitude', digits=(10, 7))
    date_localization = fields.Date()
    furnished_apartment = fields.Boolean(string='Furnished apartment')
    unit_rented = fields.Boolean( )
    rent_unit_price = fields.Float("Rent Unit Price")

    @api.onchange('rent_unit_price', 'unit_area')
    def change_rent_unit_price(self):
        for rec in self:
            rec.list_price = rec.rent_unit_price * float(rec.unit_area)

    def _get_unit_rented_state(self):
        for rec in self:
            rec.unit_rented = False
            order = rec.env['sale.order.line'].sudo().search([
                ('order_id.state', '=', 'occupied'),
                ('product_id.product_tmpl_id', '=', rec.id),
                ('property_number', '=', rec.property_id.id)
                 ], limit=1)
            if order:
                if order[0].order_id.rental_status == 'pickup':
                    rec.unit_rented = True
                elif order[0].order_id.rental_status == 'return':
                    rec.unit_rented = True
                elif order[0].order_id.rental_status == 'returned':
                    rec.unit_rented = False
                elif order[0].order_id.rental_status == 'cancel':
                    rec.unit_rented = False
            else:
                rec.unit_rented = False

    def update_product_rent_cron(self):
        for rec in self.env['product.template'].search([]):
            rec._get_unit_rented_state()

    def geo_localize(self):
        # We need country names in English below
        if not self._context.get('force_geo_localize') \
                and (self._context.get('import_file') \
                     or any(config[key] for key in ['test_enable', 'test_file', 'init', 'update'])):
            return False
        for partner in self.env.user.partner_id.with_context(lang='en_US'):
            if partner.street and partner.zip and partner.city and partner.street and partner.country_id:
                result = partner._geo_localize(partner.street,
                                               partner.zip,
                                               partner.city,
                                               partner.state_id.name,
                                               partner.country_id.name)
                print("resultresultresultresultresult", result)

                if result:
                    self.write({
                        'partner_latitude': result[0],
                        'partner_longitude': result[1],
                        'date_localization': fields.Date.context_today(partner)
                    })
        return True
