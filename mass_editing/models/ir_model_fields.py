# Copyright 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'

    mass_editing_domain = fields.Char("Mass Editing Domain", copy=False)

    @api.model
    def search(self, args, offset=0, limit=0, order=None, count=False):
        model_domain = []
        for domain in args:
            if (len(domain) > 2 and domain[0] == 'mass_editing_domain' and
                    isinstance(domain[2], str) and
                    list(domain[2][1:-1])):
                model_domain += [('model_id', 'in',
                                  [int(x) for x in domain[2][1:-1].split(',')]
                                  )]
            else:
                model_domain.append(domain)
        return super(IrModelFields, self).search(model_domain, offset=offset,
                                                 limit=limit, order=order,
                                                 count=count)
