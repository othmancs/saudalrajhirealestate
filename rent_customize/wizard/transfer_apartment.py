from odoo import fields, models, api


class TransferApartmentWizard(models.Model):
    _name = 'transfer.apartment.wizard'
    _description = 'Apartment Transfering'

    transfer_date = fields.Date()
    transfer_from_id = fields.Many2one('res.partner')
    identification_id = fields.Char()
    identification_id_date = fields.Date()

    def action_print_report(self):
        self.ensure_one()
        data = {
            'active_model': 'sale.order',
        }
        report_action = self.env.ref('rent_customize.report_transfer_apratment').report_action(None, data=data)
        report_action.update({'close_on_report_download': True})
        return report_action
