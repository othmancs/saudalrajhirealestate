# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class WizMaintenanceRequestRefuse(models.TransientModel):
    _name = 'wiz.maintenance.request.refuse'

    refuse_reason = fields.Text('Refuse Reason', required=True)

    def action_refuse(self):
        active_id = self.env.context.get('active_id')
        maintenance_request = self.env["maintenance.request"].browse(active_id)
        maintenance_request.write({
            "refuse_reason": self.refuse_reason,
            "state": "refused"
        })
