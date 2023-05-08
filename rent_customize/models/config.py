
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_contract_notify = fields.Boolean("Send Contract Notification",
                                        config_parameter="rent_customize.is_contract_notify")
    contract_notify = fields.Integer("Contract Renewal Days", config_parameter="rent_customize.contract_notify")
    is_invoice_notify = fields.Boolean("Send Invoice Notification", config_parameter="rent_customize.is_invoice_notify")
    invoice_notify = fields.Integer("Invoice Renewal Days", config_parameter="rent_customize.invoice_notify")
