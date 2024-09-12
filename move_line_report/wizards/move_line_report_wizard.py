# -*- coding: utf-8 -*-

import base64
import tempfile
from itertools import groupby
from operator import itemgetter

import xlsxwriter

from odoo import fields, models, _
from odoo.exceptions import UserError


class MoveLineReportWizard(models.TransientModel):
    _name = "move.line.report.wizard"
    _description = "Move Line Report Wizard"

    company_id = fields.Many2one('res.company', readonly=False, default=lambda self: self.env.company)
    customer_id = fields.Many2one('res.partner', 'Customer')
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    operating_unit_id = fields.Many2one('operating.unit')

    def open_view(self):
        self.ensure_one()
        self.env['account.payment'].flush(fnames=['move_id', 'outstanding_account_id'])
        self.env['account.move'].flush(fnames=['move_type', 'payment_id', 'statement_line_id'])
        self.env['account.move.line'].flush(fnames=['move_id', 'account_id', 'statement_line_id'])
        self.env['account.partial.reconcile'].flush(fnames=['debit_move_id', 'credit_move_id'])

        # Initialize the SQL query with the basic selection
        sql_query = """
            SELECT id as move_id, name, amount_total as amount_total, amount_residual as amount_residual
            FROM account_move
            WHERE state = 'posted'
            AND move_type = 'out_invoice'
        """

        # Initialize parameters list
        params = []

        # Add conditions to the SQL query based on the fields values
        if self.company_id:
            sql_query += " AND company_id = %s"
            params.append(self.company_id.id)
        if self.customer_id:
            sql_query += " AND partner_id = %s"
            params.append(self.customer_id.id)
        if self.operating_unit_id:
            sql_query += " AND operating_unit_id = %s"
            params.append(self.operating_unit_id.id)
        if self.date_from and self.date_to:
            sql_query += " AND invoice_date >= %s AND invoice_date <= %s"
            params.extend((self.date_from, self.date_to))

        # Execute the SQL query with parameters
        self._cr.execute(sql_query, tuple(params))
        data = []
        for res in self._cr.dictfetchall():
            move_id = res['move_id']
            payment = res['amount_total'] - res['amount_residual']

            # Retrieve account move lines for the current invoice
            self._cr.execute("""
                    SELECT id as aml_id, price_total as price_total, rent_fees as rent_fees
                    FROM account_move_line
                    WHERE move_id = %s
                        AND exclude_from_invoice_tab = False
                        AND display_type IS NULL
                """, (move_id,))
            account_move_lines = self._cr.dictfetchall()

            # Calculate total fees price for the invoice
            fees_price = sum(line['price_total'] for line in account_move_lines if line['rent_fees'])

            # Calculate remaining payment after deducting fees
            remaining_payment = payment - fees_price if payment > 0.0 else 0.0

            # Count the number of lines without rent fees
            num_lines_no_fees = len([line for line in account_move_lines if not line['rent_fees']])

            if num_lines_no_fees > 0:
                # Calculate the new price per line
                new_price_per_line = remaining_payment / num_lines_no_fees

                # Update data with new price total for lines without rent fees
                for line in account_move_lines:
                    if not line['rent_fees']:
                        data.append({
                            'aml_id': line['aml_id'],
                            'subtotal': line['price_total'],
                            'paid': new_price_per_line,
                            'remaining': line['price_total'] - new_price_per_line,
                            'move_id': move_id,

                        })
                    elif line['rent_fees']:
                        data.append({
                            'aml_id': line['aml_id'],
                            'subtotal': line['price_total'],
                            'paid': line['price_total'] if remaining_payment > 0.0 else 0.0,
                            'remaining': 0.0 if remaining_payment > 0.0 else line['price_total'],
                            'move_id': move_id,
                        })


        # Delete existing records in the report tree model
        self.env['move.line.report.tree'].search([]).unlink()

        # Create new records in the report tree model
        self.env['move.line.report.tree'].create(data)

        # Return action to display the report
        return {
            'type': 'ir.actions.act_window',
            'views': [(False, 'tree'), (False, 'pivot')],
            'view_mode': 'tree,pivot',
            'name': _('Report'),
            'res_model': 'move.line.report.tree',
            'context': {'create': False, 'search_default_group_customer': 1},
        }