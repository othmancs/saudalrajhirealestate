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
import logging

_logger = logging.getLogger(__name__)
import urllib.request


class CustomerTickets(models.Model):
    _name = 'customer.tickets'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Customer Tickets'
    _check_company_auto = True
    _rec_name = 'ticket_subject'
    _order = "id desc"

    name = fields.Char(string='Ticket No', default='/', readonly=True, required=True, tracking=True)
    date = fields.Date(string='Ticket Date', required=True, tracking=True, default=fields.Date.today(), readonly=True)
    package_id = fields.Integer(string='Package', tracking=True)
    package_status = fields.Selection(string='Package Status', selection=[('draft', 'Draft'),
                                                                          ('to_approve', 'To Approve'),
                                                                          ('running', 'Running'),
                                                                          ('expired', 'Expired'),
                                                                          ('reject', 'Rejected'),
                                                                          ('cancel', 'Cancelled')])
    ticket_subject = fields.Char(string='Subject', required=True)
    attachment = fields.Binary(string='Attachment')
    tick_description = fields.Html(string='Ticket Description', required=True)
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('submit', 'Submit'),
        ('in_progress', 'In Progress'),
        ('waiting', 'Waiting Fot Your feedback'),
        ('feedback', 'Feedback Sent'),
        ('solved', 'Solved'),
    ], string='Status', required=True, copy=False, tracking=True,store=1, default='draft')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    subscription_code = fields.Char(string='Subscription Code', readonly=True)
    subscription_id = fields.Many2one('subscription.info', string='Subscription Info')
    # subscription_ticket_type_id = fields.Many2one(related='subscription_id.ticket_type_id')
    # ticket_type = fields.Many2one('ticket.type', required=True)
    # ticket_stage_id = fields.Many2one('ticket.stage')
    priority = fields.Selection([('0', 'Low priority'),
                                 ('1', 'Medium priority'),
                                 ('2', 'High priority'),
                                 ('3', 'Urgent'),
                                 ], string='Priority',
                                default='1', required=True)
    ticket_id = fields.Integer(string='Ticket ID', store=1, readonly=1)
    ticket_solve_date = fields.Datetime(string='Solve Date')
    # feedback = fields.Html(string='Your Feedback')
    submit_date = fields.Date(string='Submit Date')
    created_days = fields.Integer(compute="get_days")
    ticket_type_id = fields.Many2one('sub.ticket.type')
    ticket_user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    model_id = fields.Many2one('ir.model', string='Model', required=True, index=True, ondelete='cascade')
    escalation = fields.Boolean()
    stage_state_date = fields.Datetime(required=False)
    subscription_styling = fields.Char("Styling", compute="_compute_membership_style")  # Technical Field

    def _compute_membership_style(self):
        for rec in self:
            bhc = rec.subscription_id.bg_color_hex  # Background Hex Color
            fhc = rec.subscription_id.font_color_hex  # Font Hex Color
            rec.subscription_styling = bhc

    def open_feedback(self):
        return {
            'name': _('Send Feedback'),
            'view_mode': 'form',
            'res_model': 'feedback',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'view_id': self.env.ref('customer_tickets.feedback_view_form').id,
            'context': {'default_customer_ticket_id': self.id},
        }

    @api.model
    def retrieve_quotes(self):
        """ This function returns the values to populate the custom dashboard in
            the sale order views.
        """
        subscription_id = self.env['subscription.info'].search([('package_status', '=', 'running')], limit=1)
        ticket_ids = self.env['customer.tickets'].search([('subscription_id', '=', subscription_id.id)])
        all_ticket = []
        my_ticket = []
        for line in subscription_id.plan_ids.filtered(lambda x: x.available == True):
            all_ticket.append(len(ticket_ids.filtered(lambda l: l.ticket_type_id.id == line.id).ids))
            my_ticket.append(len(ticket_ids.filtered(
                lambda l: l.ticket_type_id.id == line.id and l.ticket_user_id == self.env.user).ids))
        return {
            'ticket_type': subscription_id.plan_ids.filtered(lambda x: x.available == True).mapped('name'),
            'ticket_numbers': subscription_id.plan_ids.filtered(lambda x: x.available == True).mapped('numbers'),
            'ticket_consumed': subscription_id.plan_ids.filtered(lambda x: x.available == True).mapped('consumed'),
            'all_ticket': all_ticket,
            'my_ticket': my_ticket,
            'subscription_styling': subscription_id.subscription_styling,
        }

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
            'name': _('Ticket'),
            'view_id': view_id,
            'view_mode': 'tree',
            'views': [(view_id, 'tree')],
            'res_model': 'customer.tickets',
            'type': 'ir.actions.act_window',
            'domain': domain,
        }
        return action

    @api.onchange('ticket_type_id', 'subscription_id')
    def change_ticket_type_id(self):
        for rec in self:
            records = []
            return {'domain': {'ticket_type_id': [
                ('id', 'in', rec.subscription_id.plan_ids.filtered(lambda l: l.available == True).ids)]}}

    @api.depends('create_date')
    def get_days(self):
        for rec in self:
            rec.created_days = (datetime.today() - rec.create_date).days

    def action_reset_to_progess(self):
        self.state = 'in_progress'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                company_id = vals.get('company_id', self.env.company.id)
                vals['name'] = self.env['ir.sequence'].with_company(company_id).next_by_code('customer.ticket') or '/'
        return super().create(vals_list)

    @api.model
    def default_get(self, default_fields):
        """set user default analytic account.  """
        defaults = super(CustomerTickets, self).default_get(default_fields)
        subscription_id = self.env['subscription.info'].search([
            ('package_status', '=', 'running'),
        ])
        if subscription_id:
            defaults['subscription_id'] = subscription_id[0].id
        else:
            action = self.env.ref('customer_tickets.subscription_activation')
            msg = _("You don't have active subscription please contact us \n"
                    "Or press on activate button to enter your subscription code.")
            raise RedirectWarning(msg, action.id, _('Activate Subscription'))
        return defaults

    @api.constrains('subscription_id')
    def subscription_info(self):
        for rec in self:
            if not rec.subscription_id:
                action = self.env.ref('customer_tickets.subscription_activation')
                msg = _("You don't have active subscription please contact us. \n"
                        "Or press on activate button to enter your subscription code.")
                raise RedirectWarning(msg, action.id, _('Activate Subscription'))
            if rec.subscription_id.package_status != 'running':
                action = self.env.ref('customer_tickets.subscription_activation')
                msg = _("Your subscription was expired if you have a new subscription code please\n"
                        " press on add new subscription code button.")
                raise RedirectWarning(msg, action.id, _('Add New Subscription Code'))

    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(_('You can not delete tickets which are not on draft state'))
        super(CustomerTickets, self).unlink()

    def action_submit(self):
        """ this is for create ticket /create/ticket"""
        for rec in self:
            for line in rec.subscription_id.plan_ids:
                if line.consumed >= line.numbers:
                    if line.id == rec.ticket_type_id.id:
                        raise UserError(_('You have run out of tickets for [ %s ]' % (line.name)))
        subscription_id = self.subscription_id
        headers = {'Content-Type': 'application/json', 'authenticationcode': subscription_id.authentication_code, }
        url = self.subscription_id.support_url
        if not url:
            raise ValidationError(' Please call us to add Support URLs')
        # data = '{ "jsonrpc": "2.0", "params": {  "subscription_code": "77812864325526400649"  } }'
        ticket = {'name': self.ticket_subject,
                  'description': self.tick_description,
                  'customer_package_id': subscription_id.customer_package_id,
                  'team_id': subscription_id.team_id,
                  'ticket_no': self.name,
                #   'ticket_type_id': self.ticket_type_id.plus_id,
                  'new_ticket_type_id': self.ticket_type_id.plus_id,
                  'attachment': self.attachment,
                  'priority': self.priority,
                  'partner_id': subscription_id.customer_id,
                  'partner_name': self.create_uid.name,
                  'partner_email': self.create_uid.login,
                  'partner_phone': self.create_uid.partner_id.phone,
                  'ticket_date': str(fields.Date.today()),
                  'subscription_id': subscription_id.id,
                  'customer_ticket_id': self.id,
                  'ticket_user': self.ticket_user_id.name,
                  'ticket_model': self.model_id.name,
                  'authentication_code': subscription_id.authentication_code,
                  # 'customer_ticket_url': self.env['ir.config_parameter'].sudo().get_param('web.base.url') + "/reply/customer",
                  }

        payload = {"params": ticket}
        if '404' in str(requests.get(url)):
            return

        response = requests.request("POST", url, json=payload, headers=headers)
        print(">>>>>>>>>>>>>>>>>>", response)
        _logger.error("222222222222222222222222222222222222222222222 %r" % (response))
        _logger.error("222222222222222222222222222222222222222222222 %r" % (response.json()))
        self.ticket_id = response.json()['result']
        if models:
            pass
            # self.ticket_id = models.execute_kw(db, uid, password, 'helpdesk.ticket', 'create', [ticket])
            # ticket_obj = models.execute_kw(db, uid, password, 'helpdesk.ticket', 'read', [self.ticket_id])
            # ticket_stage = ticket_obj[0]['stage_id'][0]
            # self.ticket_stage_id = self.env['ticket.stage'].search([('stage_id', '=', ticket_stage)]).id
        else:
            raise UserError(_('You cannot submit the ticket right now as of '
                              'technical issue Please Contact company for help '))
        if str(response.json()['result']).isdigit():
            self.state = 'submit'
            self.submit_date = fields.Date.today()
            self.sudo().subscription_id.cron_subscription_info()

    def send_feedback(self, customer_state, feedback=False):
        # /update/ticket
        subscription_id = self.subscription_id
        headers = {'Content-Type': 'application/json', 'authenticationcode': subscription_id.authentication_code, }
        url = self.subscription_id.update_ticket
        # data = '{ "jsonrpc": "2.0", "params": {  "subscription_code": "77812864325526400649"  } }'
        # closed = self.env['ticket.stage'].search([('is_close', '=', True)], limit=1).stage_id
        ticket = {
            # 'feedback': feedback if feedback else self.feedback,
            'stage_id': customer_state,
            'ticket_id': self.ticket_id,
        }
        payload = {"params": ticket}
        response = requests.request("POST", url, json=payload, headers=headers)

    def action_in_progress(self):
        self.send_feedback(customer_state='in_progress')
        self.state = 'in_progress'

    def action_reset_to_progess(self):
        self.send_feedback(customer_state='in_progress')
        self.state = 'in_progress'

    def action_reopen(self):
        self.send_feedback(customer_state='reopen')
        self.state = 'reopen'

    def action_escalation(self):
        for rec in self:
            x = self.send_feedback(customer_state='escalation')
            self.message_post(body="Task Escalation Sent")
            self.escalation = True
        # self.state = 'escalation'

    def action_solve(self):
        """ This is for update ticket after click solved /update/ticket"""
        self.send_feedback(customer_state='solved')
        self.state = 'solved'

    def write(self, vals):
        for rec in self:
            if rec.subscription_id and 'state' in vals:
                state_ids = rec.subscription_id.activity_state_ids.filtered(lambda l: l.send == True and l.state == vals['state'])
                if state_ids:
                    state_id = state_ids[0]
                    user_ids = rec.create_uid.ids
                    user_ids += rec.ticket_user_id.ids
                    user_ids += state_id.user_ids.ids
                    print(">>>>>>>>>>>> ",user_ids)
                    for user in set(user_ids):
                        self.env['mail.activity'].sudo().create({
                            'activity_type_id': state_id.activity_type_id.id,
                            'res_id': self.id,
                            'res_model_id': self.env['ir.model'].sudo().search([('model', '=', 'customer.tickets')],limit=1).id,
                            'icon': 'fa-pencil-square-o',
                            'date_deadline': fields.Date.today(),
                            'user_id': user,
                            'summary': state_id.subject if state_id.subject else False,
                            'note': state_id.body,
                        })


        res = super(CustomerTickets, self).write(vals)
        return res

    def cron_close_ticket(self):
        customer_ticket_ids = self.env['customer.tickets'].search([('state', '=', 'waiting') ])
        for ticket in customer_ticket_ids:
            today = fields.Datetime.now()
            delta = today - ticket.stage_state_date
            if ticket.stage_state_date and int(delta.seconds/60/60) > int(ticket.subscription_id.auto_close):
                ticket.state = 'solved'

 

    # def cron_update_ticket(self):
    #     for rec in self.search([('state', '=', 'submit')]):
    #         subscription_id = rec.subscription_id
    #         auto_close = subscription_id.auto_close
    #         url = subscription_id.address
    #         db = subscription_id.db_name
    #         username = subscription_id.user_name
    #         password = subscription_id.password
    #         models, uid = subscription_id.connect(url, db, username, password)
    #         ticket_obj = models.execute_kw(db, uid, password, 'helpdesk.ticket', 'read', [rec.ticket_id])
    #         solve_date = ticket_obj[0]['solve_date']
    #         rec.ticket_solve_date = solve_date
    #         rec.ticket_stage_id = self.env['ticket.stage'].search([('stage_id', '=', ticket_obj[0]['stage_id'][0])],
    #                                                               limit=1).stage_id
    #         if solve_date or rec.ticket_stage_id.is_close:
    #             date_to_close = solve_date + relativedelta(days=+auto_close)
    #             if date_to_close <= fields.Datetime.now:
    #                 rec.state = 'solved'
    #                 closed = self.evn['ticket.stage'].search([('is_close', '=', True)], limit=1).stage_id
    #                 push_ticket_update = models.execute_kw(db, uid, password, 'helpdesk.ticket', 'write',
    #                                                        [rec.ticket_id, {
    #                                                            # 'feedback': rec.feedback,
    #                                                            'stage_id': closed.id}])


class TicketStage(models.Model):
    _name = 'ticket.stage'

    name = fields.Char(string='Stage', required=True)
    stage_id = fields.Integer(string='Stage ID')
    is_close = fields.Boolean(string='Is Final')
