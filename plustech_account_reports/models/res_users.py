from odoo import fields, models


class Users(models.Model):
    _inherit = 'res.users'

    allowed_see_other_assets = fields.Boolean('See Other Assets', default=False)
