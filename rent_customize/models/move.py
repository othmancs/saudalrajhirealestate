# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date, timedelta
from odoo import models, fields, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from dateutil.relativedelta import relativedelta


class RentalOrder(models.Model):
    _inherit = 'account.move'

    is_invoice_notify = fields.Boolean(string="Send Invoice Notification", default=False)


    def action_view_renting_order(self):
        action = self.env.ref("sale_renting.rental_order_action").sudo().read()[0]
        sale_id = self.env['sale.order'].search([('name', '=', self.invoice_origin)])
        # action["domain"] = [("id", "in", [sale_id.id])]
        # action["target"] = 'new'
        # return action

        return {
            'name': _('Renting Order'),
            'view_mode': 'form',
            'view_id': self.env.ref('sale_renting.rental_order_primary_form_view').id,
            'res_model': 'sale.order',
            'create': False,
            'type': 'ir.actions.act_window',
            'res_id': sale_id.id,
        }
    
    @api.model
    def _cron_send_invoice_notifications(self):
        """ Cron job to send notifications for invoice """
        is_invoice_notify = self.env['ir.config_parameter'].get_param('rent_customize.is_invoice_notify')
        invoice_notify = self.env['ir.config_parameter'].get_param('rent_customize.invoice_notify')
        print(is_invoice_notify)
        if is_invoice_notify:
            print(datetime.today() + timedelta(days=int(invoice_notify)))
            invoice_renewals = self.env['account.move'].search([('state','=','posted'),('invoice_date_due', '=', datetime.today() + timedelta(days=int(invoice_notify)))])
        for invoice in invoice_renewals:
            invoice_user_id = invoice.invoice_user_id
            notification = {
                'activity_type_id': self.env.ref('rent_customize.invoice_expire_notification').id,
                'res_id': invoice.id,
                'res_model_id': self.env['ir.model'].search([('model', '=', 'account.move')], limit=1).id,
                'icon': 'fa-pencil-square-o',
                'date_deadline': fields.Date.today(),
                'user_id': invoice_user_id.id,
                'note': "A kind reminder to inform customer to pay the due payment"
            }
            xxxx = self.env['mail.activity'].create(notification)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_contract_notify = fields.Boolean(string="Send Contract Notification", default=False)

    def _cron_send_contract_notifications(self):
        """ Cron job to send notifications for contract """

        is_contract_notify = self.env['ir.config_parameter'].get_param('rent_customize.is_contract_notify')
        contract_notify = self.env['ir.config_parameter'].get_param('rent_customize.contract_notify')
        print(contract_notify)
        print(datetime.today() - timedelta(days=int(contract_notify)))
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXX ", is_contract_notify)
        if is_contract_notify == "True":
            contract_renewals = self.env['sale.order'].search([
                ('company_id', '=', self.env.user.company_id.id),
                ('todate', '=', datetime.today() + timedelta(days=int(contract_notify)))
            ])
            print("services_idsservices_idsservices_ids", contract_renewals)
            for contract in contract_renewals:
                    user_ids = contract.user_id
                    for user in user_ids:
                        notification = {
                            'activity_type_id': self.env.ref('rent_customize.contract_expire_notification').id,
                            'res_id': contract.id,
                            'res_model_id': self.env['ir.model'].search([('model', '=', 'sale.order')], limit=1).id,
                            'icon': 'fa-pencil-square-o',
                            'date_deadline': fields.Date.today(),
                            'user_id': user.id,
                            'note': "A kind reminder to renew the contract"
                        }
                        try:
                            self.env['mail.activity'].create(notification)
                        except:
                            pass