from odoo import fields, models, api


class SubTicketType(models.Model):
    _name = 'sub.ticket.type'
    _description = 'Description'

    sub_id = fields.Many2one(comodel_name='subscription.info', ondelete='cascade')
    name = fields.Char()
    numbers = fields.Integer(string="No/Year")
    consumed = fields.Integer(string="consumed")
    available = fields.Boolean(string='Available', default=False)
    active = fields.Boolean(string='Active', default=True)
    plus_id = fields.Integer('Plus ID')

    def name_get(self):
        result = []
        for rec in self: result.append((rec.id, '%s - [ Total %s -  Consumed %s -  Remaining %s ]' % (rec.name, rec.numbers, rec.consumed, ( rec.numbers - rec.consumed) )))
        return result