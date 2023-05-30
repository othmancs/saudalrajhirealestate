from odoo import models, fields, api, _


class SaleRentalSchedule(models.Model):
    _inherit = 'sale.rental.schedule'

    property_number = fields.Many2one(related="order_line_id.property_number")
    property_id = fields.Many2one("rent.property")
    property_address_area = fields.Many2one("operating.unit")
    property_address_build = fields.Many2one("rent.property.build")

    def _compute_is_available(self):

        quoted_rentals_with_product = self.filtered(
            lambda r: r.rental_status not in ['return', 'returned', 'cancel']
                and r.return_date > fields.Date.today()
                and r.product_id.type == 'product')
        for rental in quoted_rentals_with_product:
            sol = rental.order_line_id
            rental.is_available = sol.virtual_available_at_date - sol.product_uom_qty >= 0
        (self - quoted_rentals_with_product).is_available = True
    
    def _select(self):
        return super(SaleRentalSchedule, self)._select() + ", t.property_id as property_id, rp.property_address_area as property_address_area, rp.property_address_build as property_address_build"

    def _groupby(self):
        return super(SaleRentalSchedule, self)._groupby() + ", t.property_id,rp.property_address_area,rp.property_address_build"

    def _from(self):
        return """
            sale_order_line sol
                join sale_order s on (sol.order_id=s.id)
                join res_partner partner on s.partner_id = partner.id
                left join product_product p on (sol.product_id=p.id)
                left join product_template t on (p.product_tmpl_id=t.id)
                left join rent_property rp on (t.property_id=rp.id)
                left join uom_uom u on (u.id=sol.product_uom)
                left join uom_uom u2 on (u2.id=t.uom_id)
                LEFT OUTER JOIN ordered_lots lot_info ON sol.id=lot_info.sol_id,
                padding pdg
        """


class RentalProcessingLine(models.TransientModel):
    _inherit = 'rental.order.wizard.line'

    @api.model
    def _default_wizard_line_vals(self, line, status):
        delay_price = line.product_id._compute_delay_price(fields.Date.today() - line.return_date)
        return {
            'order_line_id': line.id,
            'product_id': line.product_id.id,
            'qty_reserved': line.product_uom_qty,
            'qty_delivered': line.qty_delivered if status == 'return' else line.product_uom_qty - line.qty_delivered,
            'qty_returned': line.qty_returned if status == 'pickup' else line.qty_delivered - line.qty_returned,
            'is_late': line.is_late and delay_price > 0
        }
    
    def _apply(self):
        """Apply the wizard modifications to the SaleOrderLine.

        :return: message to log on the Sales Order.
        :rtype: str
        """
        msg = self._generate_log_message()
        for wizard_line in self:
            order_line = wizard_line.order_line_id
            if wizard_line.status == 'pickup' and wizard_line.qty_delivered > 0:
                order_line.update({
                    'product_uom_qty': max(order_line.product_uom_qty, order_line.qty_delivered + wizard_line.qty_delivered),
                    'qty_delivered': order_line.qty_delivered + wizard_line.qty_delivered
                })
                if order_line.pickup_date > fields.Date.today():
                    order_line.pickup_date = fields.Date.today()

            elif wizard_line.status == 'return' and wizard_line.qty_returned > 0:
                if wizard_line.is_late:
                    # Delays facturation
                    order_line._generate_delay_line(wizard_line.qty_returned)

                order_line.update({
                    'qty_returned': order_line.qty_returned + wizard_line.qty_returned
                })
        return msg