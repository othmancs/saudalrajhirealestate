# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date, timedelta, timedelta


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    notification_sent = fields.Boolean(default=False)


    def _cron_send_maintenance_activity_reminder_notifications(self):
        """ Cron job to send contract activity notifications """

        unresolved_contract_activities = self.env['mail.activity'].search([
          ('date_deadline', '<', fields.Date.today() - timedelta(days=1)),
            ('user_id', '!=', False),
            ('res_model_id.model', '=', 'maintenance.request'),
            ('res_id', '!=', False),
            ('activity_type_id', '=', self.env.ref('real_estate_maintenance.real_estate_maintenance_activity').id),
            ('notification_sent', '=', False)
        ])
        for activity in unresolved_contract_activities:
            document = self.env['maintenance.request'].browse(activity.res_id)
            if activity.user_id:
                notification = {
                    'activity_type_id': self.env.ref('real_estate_maintenance.real_estate_maintenance_activity').id,
                    'res_id': activity.res_id,
                    'res_model_id': self.env['ir.model'].search([('model', '=', 'maintenance.request')]).id,
                    'icon': 'fa-check-square-o',
                    'date_deadline': fields.Date.today(),
                    'user_id':activity.user_id.id,
                    'note': "طلب صيانة لم يتم عليه اجراء.تذكير",
                    'notification_sent': True
                }
                self.env['mail.activity'].create(notification)
            else:
                # activity.unlink()
                pass


    def _cron_send_maintenance_activity_notifications(self):
        """ Cron job to send contract activity notifications """

        unresolved_contract_activities = self.env['mail.activity'].search([
          ('date_deadline', '<', fields.Date.today() - timedelta(days=2)),
            ('user_id', '!=', False),
            ('res_model_id.model', '=', 'maintenance.request'),
            ('res_id', '!=', False),
            ('activity_type_id', '=', self.env.ref('real_estate_maintenance.real_estate_maintenance_activity').id),
            ('notification_sent', '=', False)
        ])
        for activity in unresolved_contract_activities:
            document = self.env['maintenance.request'].browse(activity.res_id)
            # user_ids = self.env.ref('hr.group_hr_manager').users.filtered(lambda u: document.company_id.id in u.company_ids.ids)
            manager_id = self.env['hr.employee'].search([('user_id', '=', activity.user_id.id)]).parent_id.user_id

            if manager_id:
                notification = {
                    'activity_type_id': self.env.ref('real_estate_maintenance.real_estate_maintenance_activity').id,
                    'res_id': activity.res_id,
                    'res_model_id': self.env['ir.model'].search([('model', '=', 'maintenance.request')]).id,
                    'icon': 'fa-check-square-o',
                    'date_deadline': fields.Date.today(),
                    'user_id': manager_id.id,
                    'note': "طلب صيانة لم يتم عليه اجراء.",
                    'notification_sent': True
                }
                self.env['mail.activity'].create(notification)
            else:
                # activity.unlink()
                pass



    def _cron_send_maintenance_ceo_activity_notifications(self):
        """ Cron job to send contract activity notifications """

        unresolved_contract_activities = self.env['mail.activity'].search([
       ('date_deadline', '<', fields.Date.today() - timedelta(days=3)),
            ('user_id', '!=', False),
            ('res_model_id.model', '=', 'maintenance.request'),
            ('res_id', '!=', False),
            ('activity_type_id', '=', self.env.ref('real_estate_maintenance.real_estate_maintenance_activity').id),
            ('notification_sent', '=', False)
        ])
        for activity in unresolved_contract_activities:
            document = self.env['maintenance.request'].browse(activity.res_id)
            # user_ids = self.env.ref('hr.group_hr_manager').users.filtered(lambda u: document.company_id.id in u.company_ids.ids)
            manager_id = self.env['hr.employee'].search([('user_id', '=', activity.user_id.id)]).parent_id.user_id

            ceo_user_ids = self.env.ref('real_estate_maintenance.group_maintenance_ceo').users
            if ceo_user_ids:
                for manager_id in ceo_user_ids :
                    notification = {
                        'activity_type_id': self.env.ref('real_estate_maintenance.real_estate_maintenance_activity').id,
                        'res_id': activity.res_id,
                        'res_model_id': self.env['ir.model'].search([('model', '=', 'maintenance.request')]).id,
                        'icon': 'fa-check-square-o',
                        'date_deadline': fields.Date.today(),
                        'user_id': manager_id.id,
                        'note': "طلب صيانة لم يتم عليه اجراء.",
                        'notification_sent': True
                    }
                    self.env['mail.activity'].create(notification)
            else:
                # activity.unlink()
                pass

