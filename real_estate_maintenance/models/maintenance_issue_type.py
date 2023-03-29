from odoo import models, fields, api


class MaintenanceIssueType(models.Model):
    _name = "maintenance.issue.type"
    _description = "Issue Type"

    INVOICING_STATES = [('on-company', 'On The Company'), ('on-partner', 'On The Requester')]

    name = fields.Char("Issue Type")
    invoice_status = fields.Selection(INVOICING_STATES, "Invoicing Status", default="on-partner")
