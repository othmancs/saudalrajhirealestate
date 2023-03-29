from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    agreement_no = fields.Integer(string='Agreements No.', required=True, default=3)


class PurachseConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    agreement_no = fields.Integer(string='Agreements No.', required=True,
                             default=lambda self: self.env.user.company_id.agreement_no)
    

    @api.model
    def create(self, vals):
        res = super(PurachseConfigSettings, self).create(vals)
        res.company_id.write({'agreement_no': vals['agreement_no']})
        return res
