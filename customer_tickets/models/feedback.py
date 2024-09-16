from odoo import models, fields, api, _
import requests


class Feedback(models.Model):
    _name = 'feedback'
    name = fields.Text()
    customer_ticket_id = fields.Many2one('customer.tickets')

    def send2plus(self):
        # /update/ticket
        subscription_id = self.customer_ticket_id.subscription_id
        headers = {'Content-Type': 'application/json', 'authenticationcode': subscription_id.authentication_code, }
        url = self.customer_ticket_id.subscription_id.update_ticket
        ticket = {
            # 'feedback': feedback if feedback else self.feedback,
            'is_feedback': True,
            'feedback': self.name,
            'stage_id': 'feedback',
            'ticket_id': self.customer_ticket_id.ticket_id,
        }
        payload = {"params": ticket}
        response = requests.request("POST", url, json=payload, headers=headers)
        self.customer_ticket_id.message_post(body=self.name)
