from odoo import fields, models, api
import requests


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model
    def create(self, vals):
        res = super(MailMessage, self).create(vals)
        if 'mail_post_autofollow' in self.env.context:
            if self.env.context['mail_post_autofollow'] == True  and res.model == 'customer.tickets' and res.message_type == 'comment' and not self.env.context.get("no_reply", False):
                customer_ticket_id = self.env['customer.tickets'].sudo().browse(vals['res_id'])
                if customer_ticket_id:
                    subscription_id = customer_ticket_id.subscription_id
                    headers = {'Content-Type': 'application/json', 'authenticationcode': subscription_id.authentication_code, }
                    url = customer_ticket_id.subscription_id.update_ticket
                    ticket_message = {
                        'message': vals['body'],
                        'ticket_id': customer_ticket_id.ticket_id,
                    }
                    payload = {"params": ticket_message}
                    response = requests.request("POST", url, json=payload, headers=headers)
        return res