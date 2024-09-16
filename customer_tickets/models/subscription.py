# -*- coding: utf-8 -*-
import json
from odoo import models, fields, api, _
import xmlrpc.client
from odoo.exceptions import ValidationError, UserError, RedirectWarning
from dateutil.relativedelta import relativedelta
import requests
from odoo import http
from odoo.http import request
from datetime import datetime, date


class SubscriptionInfo(models.Model):
    _name = 'subscription.info'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Customer Subscription Info'
    _rec_name = 'subscription_code'

    subscription_code = fields.Char(string='Subscription Code')
    db_name = fields.Char(string='Database Name')
    address = fields.Char(string='IP/Domain')
    user_name = fields.Char(string='User Name')
    password = fields.Char(string='Password')
    package_status = fields.Selection(string='Package Status',
                                      selection=[('draft', 'Draft'), ('to_approve', 'To Approve'),
                                                 ('running', 'Running'), ('expired', 'Expired'),
                                                 ('reject', 'Rejected'), ('cancel', 'Cancelled')],store=1, readonly=True)
    start_date = fields.Date(string='Start Date', tracking=True, readonly=True)
    exp_date = fields.Date(string='Expiry Date', tracking=True, readonly=True)
    consumed = fields.Integer(string='Consumed Tickets', readonly=True)
    remaining_tickets = fields.Integer(string='Remaining Tickets', readonly=True)
    customer_id = fields.Integer(string='Customer ID', readonly=True)
    customer_package_id = fields.Integer(string='Customer Package ID', store=1,readonly=True)
    team_id = fields.Integer(string='Team ID', readonly=True)
    team_name = fields.Char(string='Team Name', readonly=True)
    auto_close = fields.Integer(string='Auto Close Ticket After', readonly=True)
    package_name = fields.Char(string='Package')
    no_tickets = fields.Integer(string='Package No of Tickets', store=1)
    color = fields.Integer('Color Index', default=1)
    authentication_code = fields.Char(string='Authentication Code')
    support_url = fields.Char(string='Support URL', store=1)
    update_ticket = fields.Char(string='Update Ticket', store=1)
    plan_name = fields.Char(string='Plan', store=1)
    plan_ids = fields.One2many(comodel_name='sub.ticket.type', inverse_name='sub_id',store=1, ondelete="cascade")
    activity_state_ids= fields.One2many( comodel_name='activity.state', inverse_name='subscription_id')
    bg_color_hex = fields.Char("BG Color Hex", default="#000")
    font_color_hex = fields.Char("Font Color Hex", default="#fff")
    subscription_styling = fields.Char("Styling", compute="_compute_membership_style")  # Technical Field

    def _compute_membership_style(self):
        for rec in self:
            bhc = rec.bg_color_hex  # Background Hex Color
            fhc = rec.font_color_hex  # Font Hex Color
            rec.subscription_styling = f"border-radius: 5px; color: {fhc} !important; background: {bhc} !important;" + \
                                     f" padding: 2px; text-align: center; "
    tickets_count = fields.Integer(compute="compute_ticket_counts")
    ticket_ids = fields.One2many(comodel_name='customer.tickets', inverse_name='subscription_id', )
    @api.depends('ticket_ids', 'start_date', 'exp_date')
    def compute_ticket_counts(self):
        for rec in self:
            ticket_ids = self.env['customer.tickets'].search([
                ('subscription_id', '=', rec.id),
                ('create_date', '>=', rec.start_date),
                ('create_date', '<=', rec.exp_date),
            ])
            rec.tickets_count = len(ticket_ids.ids)
    def action_open_tickets(self):
        for rec in self:
            ticket_ids = self.env['customer.tickets'].search([
                ('subscription_id', '=', rec.id),
                ('create_date', '>=', rec.start_date),
                ('create_date', '<=', rec.exp_date),
            ])
            action = self.env.ref('customer_tickets.customer_tickets_action').sudo().read()[0]
            action['domain'] = [('id', 'in', ticket_ids.ids)]
            return action
    @api.model
    def create(self, vals):
        info_id = self.env['subscription.info'].search([('package_status', '=', 'running')], limit=1)
        if info_id:
            raise ValidationError(_("Can not create New One, there is an Other running Subscription"))
        return super(SubscriptionInfo, self).create(vals)
    # @api.model
    # def retrieve_quotes(self):
    #     """ This function returns the values to populate the custom dashboard in
    #         the sale order views.
    #     """
    #     subscription_id = self.env['subscription.info'].search([('package_status', '=', 'running')], limit=1)
    #     ticket_ids = self.env['customer.tickets'].search([('subscription_id', '=', subscription_id.id)])
    #     all_ticket = []
    #     my_ticket = []
    #     for line in subscription_id.plan_ids:
    #         all_ticket.append(len(ticket_ids.filtered(lambda l: l.ticket_type_id.id == line.id).ids))
    #         my_ticket.append(len(ticket_ids.filtered(lambda l: l.ticket_type_id.id == line.id and l.ticket_user_id == self.env.user).ids))
    #     print("XXXXXXXXXXXXXXXXself.subscription_styling ", self.subscription_styling)
    #     return {
    #         'ticket_type' : subscription_id.plan_ids.mapped('name'),
    #         'ticket_numbers' : subscription_id.plan_ids.mapped('numbers'),
    #         'ticket_consumed' : subscription_id.plan_ids.mapped('consumed'),
    #         'subscription_styling' : self.subscription_styling,
    #         'all_ticket' : all_ticket,
    #         'my_ticket' : my_ticket,
    #
    #     }

    @api.model
    def sale_action_dashboard_waiting_list(self):
        return self.search([])._action_view_quotes(period='waiting', only_my_closed=False)

    def _action_view_quotes(self, period=False, only_my_closed=False):
        domain = [('company_id', '=', self.env.company.id)]

        if period == 'today':
            domain += [('state', '=', 'draft'), ('date', '>=', fields.Datetime.to_string(datetime.date.today()))]

        if period == 'waiting':
            domain += [('state', '=', 'sent'), ('date', '>=', fields.Datetime.now())]

        if period == 'late':
            domain += [('state', 'in', ['draft', 'sent', 'to approve']), ('date', '<', fields.Datetime.now())]

        if only_my_closed and not period:
            domain += [('state', '=', 'draft'), ('user_id', '=', self._uid)]

        if only_my_closed and period:
            domain += [('user_id', '=', self._uid)]

        if not period and not only_my_closed:
            domain += [('state', '=', 'draft')]
        action = self.env['ir.actions.actions']._for_xml_id('customer_tickets.customer_tickets_action')
        # action = self.env.ref("customer_tickets.customer_tickets_action").sudo().read()[0]
        # action['domain'] = domain
        # action['view_mode'] = 'tree'
        # action['view_id'] = self.env.ref('customer_tickets.customer_tickets_tree').id


        view_id = self.env.ref('customer_tickets.customer_tickets_tree').id
        action = {
            'name': _('Ticket') ,
            'view_id': view_id,
            'view_mode': 'tree',
            'views': [(view_id, 'tree'),(False, 'form')],
            'res_model': 'customer.tickets',
            'type': 'ir.actions.act_window',
            'domain': domain,
        }
        return action
    def _get_search_customer_url(self):
        # customer = self.env['ir.config_parameter'].get_param('web.base.url')
        # customer = str(customer) + '/search/customer'
        customer = 'https://plus.inv-sa.com/search/customer'
        return customer

    search_customer_url = fields.Char(string='Search URL', default=_get_search_customer_url, store=1)
    # ticket_type_id = fields.Many2one('ticket.type')

    # active = fields.Boolean(string='Active')[]

    def connect(self, url, db, username, password):
        try:
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        except ValueError:
            raise ValidationError(_("Please check your connection parameter or"
                                    "contact us for configuration set up"))
        try:
            uid = common.authenticate(db, username, password, {})
        except ValueError:
            raise ValidationError(_("Please check database name,username and password or "
                                    "contact us for configuration set up."))
        try:
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        except ValueError:
            raise ValidationError(_("Please check your connection parameter or "
                                    "contact us for configuration set up."))

        return models, uid

    def get_plan_lines(self):
        headers = {'Content-Type': 'application/json', 'authenticationcode': self.authentication_code, }
        url = self.search_customer_url
        if not self.authentication_code:
            raise ValidationError(_("Enter Authentication Code in Subscription Configuration"))
        data = '{ "jsonrpc": "2.0", "params": {"subscription_code": "77812864325526400649"}}'
        response = requests.request("POST", url, data=data, headers=headers)
        matched = []

        if 'result' in response.json():
            if 'lines' in response.json()['result']:
                for line in response.json()['result']['lines']:
                    type_id = self.env['sub.ticket.type'].sudo().search([('plus_id', '=', line['line_id'])])
                    # type_id.unlink()
                    matched.append(line['line_id'])
                    if type_id:
                        type_id.sudo().write({
                            'numbers': line['numbers'],
                            'name': line['name'],
                            'consumed': line['consumed'],
                            'available': line['available'],
                        })
                    else:
                        self.env['sub.ticket.type'].sudo().create({
                            'sub_id': self.id,
                            'name': line['name'],
                            'numbers': line['numbers'],
                            'consumed': line['consumed'],
                            'available': line['available'],
                            'plus_id': line['line_id'],
                        })

        for p in self.plan_ids:
            if p.plus_id not in matched:
                p.sudo().write({'active' : False})

    def cron_subscription_info(self):
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX ")
        for rec in self.search([]):
            rec.get_subscription_info()

    def get_subscription_info(self):
        '''/search/customer'''
        headers = {'Content-Type': 'application/json', 'authenticationcode': self.authentication_code, }
        url = self.search_customer_url
        if not self.authentication_code:
            raise ValidationError(_("Enter Authentication Code in Subscription Configuration"))

        vals = {'customer_ticket_url': str(self.env['ir.config_parameter'].sudo().get_param('web.base.url') + "/reply/customer")}
        # data = '{ "jsonrpc": "2.0", "params": {"subscription_code": "77812864325526400649"}}'
        payload = {"params": vals}
        response = requests.request("POST", url, json=payload, headers=headers)
        self.get_plan_lines()
        print("XXXXXXXXXXXXXXXXXXXXXXX ",response)
        print("XXXXXXXXXXXXXXXXXXXXXXX ",response.json())
        print("XXXXXXXXXXXXXXXXXXXXXXX ",response.json()['result'])
        print("XXXXXXXXXXXXXXXXXXXXXXX ",response.json()['result']['success'])
        if str(response.json()['result']['success']) == 'True':
            res = response.json()
            response = res['result']
            self.package_status = response['state']
            self.plan_name = response['plan_name']
            self.exp_date = response['exp_date']
            # self.customer_id = response['partner_id'][0]
            self.customer_package_id = response['customer_package_id']
            self.start_date = response['start_date']
            self.support_url = response['support_url']
            self.update_ticket = response['update_ticket']
            self.font_color_hex = response['font_color_hex']
            self.bg_color_hex = response['bg_color_hex']
        else:
            raise ValidationError('Their is no valid Authentication Code check your Authentication code,'
                                  ' please contact support team')
    def action_view_tickets(self):
        action = self.env["ir.actions.actions"]._for_xml_id("customer_tickets.customer_tickets_action")
        action.update({
            'display_name': _("Tickets"),
            'domain': [('subscription_id', '=', self.id), ('state', 'not in', ['cancel', 'reject'])],
        })
        return action

    def action_view_consumed_tickets(self):
        action = self.env["ir.actions.actions"]._for_xml_id("customer_tickets.customer_tickets_action")
        action.update({
            'display_name': _("Tickets"),
            'domain': [('subscription_id', '=', self.id), ('state', 'not in', ['draft', 'cancel', 'reject'])],
        })
        return action

    def action_view_open_tickets(self):
        action = self.env["ir.actions.actions"]._for_xml_id("customer_tickets.customer_tickets_action")
        action.update({
            'display_name': _("Open Tickets"),
            'domain': [('subscription_id', '=', self.id), ('state', 'in', ('submit', 'in_progress'))],
        })
        return action

    def action_view_solved_tickets(self):
        action = self.env["ir.actions.actions"]._for_xml_id("customer_tickets.customer_tickets_action")
        action.update({
            'display_name': _("Solved Tickets"),
            'domain': [('subscription_id', '=', self.id), ('state', '=', 'solved')],
        })
        return action

    def action_create_new(self):
        ctx = self._context.copy()
        ctx['default_subscription_id'] = self.id
        return {
            'name': _('Create Ticket'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'customer.tickets',
            'view_id': self.env.ref('customer_tickets.customer_tickets_form').id,
            'context': ctx,
        }


class SubscriptionCode(models.TransientModel):
    _name = 'subscription.code'
    _description = 'Subscription Activation Wizard'

    subscription_code = fields.Char(string='Subscription Code', required=True)
    authentication_code = fields.Char(string='Authentication Code', required=True)

    def activate_subscription(self):
        subscription = self.env['subscription.info'].search([('subscription_code', '=', False)])
        if subscription:
            subscription.subscription_code = self.subscription_code
            subscription.authentication_code = self.authentication_code
            subscription.cron_subscription_info()
        else:
            connection_info = self.env.ref('customer_tickets.connection_info')
            if not connection_info:
                action = self.env.ref('customer_tickets.subscription_info_action')
                msg = _("You don't have active subscription please contact us \n"
                        "Or press on activate button to enter your subscription code.")
                raise RedirectWarning(msg, action.id, _('Activate Subscription'))
            if connection_info:
                connection_info['subscription_code'] = self.subscription_code
                # new_subscription = self.env['subscription.info'].create(connection_info)
                subscription.cron_subscription_info()


class ActivityState(models.Model):
    _name = 'activity.state'

    subscription_id = fields.Many2one('subscription.info')
    activity_type_id = fields.Many2one('mail.activity.type', readonly=False)
    user_ids = fields.Many2many(comodel_name='res.users', string='Users')
    send = fields.Boolean('Send ?')
    subject = fields.Char('Subject')
    body = fields.Char('Body')
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('submit', 'Submit'),
        ('in_progress', 'In Progress'),
        ('waiting', 'Waiting Fot Your feedback'),
        ('feedback', 'Feedback Sent'),
        ('solved', 'Solved'),
    ], string='Status', required=True, copy=False, tracking=True, default='draft')
