# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date, timedelta, timedelta


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    notification_sent = fields.Boolean(default=False)

    def _cron_send_contract_activity_notifications(self):
        """ Cron job to send contract activity notifications """

        unresolved_contract_activities = self.env['mail.activity'].search([
            ('date_deadline', '<', fields.Date.today() - timedelta(days=1)),
            ('user_id', '!=', False),
            ('res_model_id.model', '=', 'sale.order'),
            ('res_id', '!=', False),
            ('activity_type_id', '=', self.env.ref('rent_customize.contract_expire_notification').id),
            ('notification_sent', '=', False)
        ])

        for activity in unresolved_contract_activities:
            document = self.env['sale.order'].browse(activity.res_id)
            # user_ids = self.env.ref('hr.group_hr_manager').users.filtered(lambda u: document.company_id.id in u.company_ids.ids)
            manager_id = self.env['hr.employee'].search([('user_id', '=', activity.user_id.id)]).parent_id.user_id

            if manager_id:
                if user.has_group('base.group_user'):
                    notification = {
                        'activity_type_id': self.env.ref(
                            'rent_customize.unresolved_contract_activity_notification').id,
                        'res_id': activity.res_id,
                        'res_model_id': self.env['ir.model'].search([('model', '=', 'sale.order')]).id,
                        'icon': 'fa-check-square-o',
                        'date_deadline': fields.Date.today(),
                        'user_id': manager_id.id,
                        'note': "Activity unresolved due payment contract.",
                        'notification_sent': True
                    }
                    self.env['mail.activity'].create(notification)
            else:
                activity.unlink()

    @api.model
    def _cron_send_invoice_activity_notifications(self):
        """ Cron job to send invoice activity notifications """

        unresolved_invoice_activities = self.env['mail.activity'].search([
            ('date_deadline', '<', fields.Date.today() - timedelta(days=1)),
            ('user_id', '!=', False),
            ('res_model_id', '=', 'account.move'),
            ('res_id', '!=', False),
            ('activity_type_id', '=', self.env.ref('rent_customize.invoice_expire_notification').id),
            ('notification_sent', '=', False)
        ])
        print("888888888888888888888", unresolved_invoice_activities, "********************")
        for activity in unresolved_invoice_activities:
            document = self.env['account.move'].browse(activity.res_id)
            manager_id = self.env['hr.employee'].search([('user_id', '=', activity.user_id.id)]).parent_id.user_id
            user_ids = self.env.ref('hr.group_hr_manager').users.filtered(lambda u: document.company_id.id in u.company_ids.ids)
            if manager_id:
                notification = {
                    'activity_type_id': self.env.ref('rent_customize.unresolved_invoice_activity_notification').id,
                    'res_id': activity.res_id,
                    'res_model_id': self.env['ir.model'].search([('model', '=', 'account.move')]).id,
                    'icon': 'fa-check-square-o',
                    'date_deadline': fields.Date.today(),
                    'user_id': manager_id.id,
                    'note': f"Activity unresolved due payment {activity.res_id} for partner {document.partner_id.name}.",
                    'notification_sent': True
                }
                self.env['mail.activity'].create(notification)
            else:
                activity.unlink()
