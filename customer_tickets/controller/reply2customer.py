# -*- coding: utf-8 -*-
import json

from odoo import models
from odoo import http
from odoo.http import request
import json

from odoo import models, fields, api, _
import xmlrpc.client
from odoo.exceptions import ValidationError, UserError, RedirectWarning
from dateutil.relativedelta import relativedelta
import requests
from odoo import http
from odoo.http import request
from datetime import datetime, date
import logging

_logger = logging.getLogger(__name__)


class Reply2Customer(http.Controller):

    @http.route('/reply/customer', type='json', auth='public', methods=['POST'], csrf=False)
    def reply2customer(self, **data):
        headers = request.httprequest.headers
        subscription_id = request.env['subscription.info'].sudo().search( [('authentication_code', '=', headers['authenticationcode'])], limit=1)
        print(">>>>>>>>>>>>>>>>>>>>>>>>", subscription_id)
        if subscription_id.authentication_code == headers['authenticationcode']:
            if 'state' in data:
                ticket_id = request.env['customer.tickets'].sudo().search([('ticket_id', '=', int(data['customer_ticket_id']))])
                ticket_id.sudo().write({'state': data['state']})
                if data['state'] == 'solved':
                    print("XXXXXXXXXXXXXXXXXXXXXwww ", fields.Datetime.now())
                    ticket_id.ticket_solve_date = fields.Datetime.now()
            if 'message' in data:
                ticket_id = request.env['customer.tickets'].sudo().search([('id', '=', int(data['customer_ticket_id']))])
                sub_type_id = request.env['mail.message.subtype'].sudo().search([('name', 'in', ['Discussions', 'المناقشات'])])
                plus_id = request.env.ref('customer_tickets.plustech_partner')
                # plus_id = request.env['res.partner'].search([('name', 'ilike', 'plus')], limit=1).id
                if len(data['message']) > 0:
                    new = request.env['mail.message'].sudo().with_context(no_reply=True).create({
                        'date': fields.Datetime.now(),
                        'email_from': '"' + request.env.user.name if request.env.user else "ANAANANAA" + '"' + "<" + request.env.user.partner_id.email if request.env.user.partner_id else 'ooooooooo' + '>',
                        # 'author_id' : "Plustech",
                        'author_id': plus_id.id if plus_id else '',
                        'message_type': "comment",
                        'subtype_id': sub_type_id.id if sub_type_id else False,
                        'model': 'customer.tickets',
                        'res_id': ticket_id.id,
                        'body': data['message'],
                    })

                    request.env['mail.activity'].sudo().create({
                        'activity_type_id': request.env.ref('customer_tickets.mail_activity_ticket_update').id,
                        'res_id': ticket_id.id,
                        'res_model_id': request.env['ir.model'].sudo().search([('model', '=', 'customer.tickets')],limit=1).id,
                        'icon': 'fa-pencil-square-o',
                        'date_deadline': fields.Date.today(),
                        'user_id': ticket_id.ticket_user_id.id,
                        'summary': 'Ticket Message',
                        'note': data['message'],
                    })
            if 'attach' in data:
                ticket_id = request.env['customer.tickets'].sudo().search(
                    [('id', '=', int(data['customer_ticket_id']))])
                attach = request.env['ir.attachment'].sudo().create({
                    'name': data['name'],
                    'type': 'binary',
                    'datas': data['attach'],
                    'res_model': 'customer.tickets',
                    'res_id': data['customer_ticket_id'],
                    'plus_ticket_id': data['plus_ticket_id'],
                    'plus_attachment_id': data['plus_attachment_id'],
                    # 'create_uid' : request.env.sudo().ref('customer_tickets.plustech_partner').user_id,
                })
            print("datadatadatadatadatadatadatadata", data)
            if 'delete_attach_id' in data:
                ir_attachment_id = request.env['ir.attachment'].sudo().search([
                    ('plus_ticket_id', '=', data['customer_ticket_id']),
                    ('plus_attachment_id', '=', data['delete_attach_id']),
                ])
                ir_attachment_id.unlink()
        else:
            return {'success': False}
