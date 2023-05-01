from odoo import fields, models, api, _


class BranchBranch(models.Model):
    _inherit = "branch.branch"

    account_asset_count = fields.Integer('Asset Count', compute="_get_asset_count")
    asset_sequence_id = fields.Many2one('ir.sequence', string='Asset Sequence', copy=False)

    def _get_asset_count(self):
        self.account_asset_count = self.env['account.asset'].search_count([('branch_id', '=', self.id)])

    def action_view_assets(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Branch Moves'),
            'res_model': 'account.asset',
            'view_mode': 'tree,form',
            'context': {},
            'domain': [('branch_id', '=', self.id)],
        }

    @api.model
    def create(self, vals):
        res = super(BranchBranch, self).create(vals)
        if res.branch_auto_sequence and not res.asset_sequence_id:
            sequence_id = self.env['ir.sequence'].create({
                'name': '{} Asset'.format(res.name),
                'prefix': 'ASST/{}/'.format(res.short_code),
                'padding': 4
            })
            res.asset_sequence_id = sequence_id
        return res
