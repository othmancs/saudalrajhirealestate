from odoo import fields, models, api
import requests


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'


    plus_ticket_id = fields.Char()
    plus_attachment_id = fields.Char()


    # def unlink(self):
    #     for rec in self:
    #         if not rec.plus_ticket_id and not rec.plus_attachment_id:
    #             customer_ticket_id = self.env['customer.tickets'].sudo().browse(rec.res_id)
    #             if customer_ticket_id and customer_ticket_id.ticket_id and customer_ticket_id.subscription_id.package_status == 'running':
    #                 headers = {'Content-Type': 'application/json', 'authenticationcode': customer_ticket_id.subscription_id.authentication_code, }
    #                 url = customer_ticket_id.subscription_id.update_ticket
    #                 ticket_message = {
    #                     'ticket_id': customer_ticket_id.ticket_id,
    #                     'customer_ticket_id': customer_ticket_id.id,
    #                     'delete_attach_id': rec.id,
    #                 }
    #                 payload = {"params": ticket_message}
    #                 response = requests.request("POST", url, json=payload, headers=headers)
    #     return super(IrAttachment, self).unlink()

    def write(self, vals):
        res = super(IrAttachment, self).write(vals)
        for record in self:
            if record.res_model == 'customer.tickets' and record.datas:
                customer_ticket_id = self.env['customer.tickets'].sudo().browse(record.res_id)
                if customer_ticket_id and customer_ticket_id.ticket_id and customer_ticket_id.subscription_id.package_status == 'running':
                    headers = {'Content-Type': 'application/json', 'authenticationcode': customer_ticket_id.subscription_id.authentication_code, }
                    url = customer_ticket_id.subscription_id.update_ticket
                    ticket_message = {
                        'name': record.name,
                        'attach': record.datas,
                        'ticket_id': customer_ticket_id.ticket_id,
                        'customer_ticket_id': customer_ticket_id.id,
                        'customer_attachment_id': record.id,
                    }
                    payload = {"params": ticket_message}
                    response = requests.request("POST", url, json=payload, headers=headers)
        return res
