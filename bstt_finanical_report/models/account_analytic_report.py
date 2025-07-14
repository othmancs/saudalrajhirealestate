# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class analytic_report(models.AbstractModel):
    _inherit = 'account.analytic.report'

    def _get_columns_name(self, options):
        return [{'name': ''},
                {'name': _('Reference')},
                {'name': _('Partner')},
                {'name': _('Debit'), 'class': 'number'},
                {'name': _('Credit')},
                {'name': _('Balance'), 'class': 'number'}]

    def _generate_analytic_account_lines(self, analytic_accounts, parent_id=False):
        lines = []

        for account in analytic_accounts:
            lines.append({
                'id': 'analytic_account_%s' % account.id,
                'name': account.name,
                'columns': [{'name': account.code},
                            {'name': account.partner_id.display_name},
                            {'name': self.format_value(account.debit)},
                            {'name': self.format_value(account.credit)},
                            {'name': self.format_value(account.balance)}],
                'level': 4,  # todo check redesign financial reports, should be level + 1 but doesn't look good
                'unfoldable': False,
                'caret_options': 'account.analytic.account',
                'parent_id': parent_id,  # to make these fold when the original parent gets folded
            })

        return lines

    def _generate_analytic_group_line(self, group, analytic_line_domain, unfolded=False):
        LOWEST_LEVEL = 1
        balance = self._get_balance_for_group(group, analytic_line_domain)
        print(balance)

        accounts = self.env['account.analytic.account'].search([('group_id', 'child_of', group.id)])
        debits = sum([row['debit'] for row in accounts])
        credits = sum([row['credit'] for row in accounts])

        line = {
            'columns': [{'name': ''},
                        {'name': ''},
                        {'name': self.format_value(debits)},
                        {'name': self.format_value(credits)},
                        {'name': self.format_value(balance)},
                        ],
            'unfoldable': True,
            'unfolded': unfolded,
        }

        if group:
            line.update({
                'id': group.id,
                'name': group.name,
                'level': LOWEST_LEVEL + self._get_amount_of_parents(group),
                'parent_id': group.parent_id.id,  # to make these fold when the original parent gets folded
            })
        else:
            line.update({
                'id': self.DUMMY_GROUP_ID,
                'name': _('Accounts without a group'),
                'level': LOWEST_LEVEL + 1,
                'parent_id': False,
            })

        return line
