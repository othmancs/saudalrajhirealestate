# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class WizMaintenanceRequestAssign(models.TransientModel):
    _name = 'wiz.maintenance.request.assign'

    assigned_to = fields.Many2one("hr.employee", required=True)
    visit_date = fields.Date("Visit Planned Date", required=True)

    def action_confirm(self):
        active_id = self.env.context.get('active_id')
        maintenance_request = self.env["maintenance.request"].browse(active_id)
        maintenance_request.write({
            "maintenance_responsible_id": self.assigned_to.id,
            "visit_date": self.visit_date,
            "state": "confirm"
        })
