# -*- coding: utf-8 -*-
from odoo import api, fields, models
import secrets


class ResCompany(models.Model):
    _inherit = 'res.company'
    notify_user_ids = fields.Many2many('res.users', 'notify_user_rel', string='Notify Users')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    upcoming_days = fields.Integer(config_parameter='notify_upcoming_and_overdue.upcoming_days')
    over_days = fields.Integer(config_parameter='notify_upcoming_and_overdue.over_days')
    send_email = fields.Boolean(config_parameter='notify_upcoming_and_overdue.send_email')
    send_user_notify = fields.Boolean(config_parameter='notify_upcoming_and_overdue.send_user_notify')
    notify_user_ids = fields.Many2many('res.users', 'notify_user_rel',string="Notify Users",related='company_id.notify_user_ids', readonly=False)
