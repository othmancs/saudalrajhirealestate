from odoo import models, fields, api


class MaintenanceType(models.Model):
    _name = "maintenance.type.type"
    _description = "maintenance Type"


    name = fields.Char("Type")
