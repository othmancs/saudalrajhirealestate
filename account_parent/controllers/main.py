# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2016 - 2020 Steigend IT Solutions (Omal Bastin)
#    Copyright (C) 2020 - Today O4ODOO (Omal Bastin)
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################
from odoo import http, _
from odoo.http import request, serialize_exception
from odoo.tools import html_escape
from odoo.addons.web.controllers.export import SpreadsheetExport
from odoo.exceptions import UserError

import json
import re
import io
import datetime
try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class CoAReportController(http.Controller):

    @http.route('/account_parent/<string:output_format>/<string:report_name>/<int:report_id>', type='http', auth='user')
    def coa_pdf_report(self, output_format, report_name, report_id=False, **kw):
        uid = request.session.uid
        coa = request.env['account.open.chart'].with_user(uid).browse(report_id)
        try:
            if output_format == 'pdf':
                response = request.make_response(
                    coa.with_context(active_id=report_id).get_pdf(report_id),
                    headers=[
                        ('Content-Type', 'application/pdf'),
                        ('Content-Disposition', 'attachment; filename=coa_report.pdf;')
                    ]
                )
                return response
        except Exception as e:
            se = serialize_exception(e)
            error = {
                'code': 200,
                'message': 'Odoo Server Error',
                'data': se
            }
            return request.make_response(html_escape(json.dumps(error)))

    @http.route('/account_parent/export/xls', type='http', auth='user')
    def coa_xls_report(self, data, **kw):
        coa_data = json.loads(data)
        report_id = coa_data.get('wiz_id', [])
        report_obj = request.env['account.open.chart'].browse(report_id)
        user_context = report_obj._build_contexts()

        lines = request.env['account.open.chart'].with_context(print_mode=True,
                                                               output_format='xls'
                                                               ).get_pdf_lines(report_id)
        user_context.update(report_obj.generate_report_context(user_context))
        show_initial_balance = user_context.get('show_initial_balance')
        row_data = report_obj.get_xls_title(user_context)

        if show_initial_balance:
            row_data.append(
                ['Code', 'Name', 'Type', 'Initial Balance', 'Debit', 'Credit', 'Ending Balance', 'Unfoldable'])
        else:
            row_data.append(['Code', 'Name', 'Type', 'Debit', 'Credit', 'Balance', 'Unfoldable'])
        for line in lines:
            level = line.get('level')
            unfoldable = line.get('unfoldable')
            code = line.get('code').rjust(2 * (int(level) + len(line.get('code'))))
            name = line.get('name')
            ac_type = line.get('ac_type')
            initial_balance = line.get('initial_balance')
            debit = line.get('debit')
            credit = line.get('credit')
            balance = line.get('balance')
            if show_initial_balance:
                balance = line.get('ending_balance')
                row_data.append([code, name, ac_type, initial_balance, debit, credit,
                                 balance, unfoldable])
            else:
                row_data.append([code, name, ac_type, debit, credit,
                                 balance, unfoldable])
        columns_headers = ['', '', 'Chart Of Accounts', '', '']
        rows = row_data
        return request.make_response(
            self.coa_format_data(columns_headers, rows),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', 'attachment; filename=coa_report.xlsx;')
            ],
        )

    def coa_format_data(self, fields, rows):
        if not xlsxwriter:
            raise UserError(_("The Python library 'xlsxwriter' is required to export XLSX files."))

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Sheet 1')
        
        # Header Style
        header_style = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'bg_color': '#FFFF00'
        })
        
        # Data Style
        data_style = workbook.add_format({
            'text_wrap': True,
            'border': 1
        })
        
        bold_style = workbook.add_format({
            'bold': True,
            'border': 1
        })

        # Write Headers
        for col, field in enumerate(fields):
            worksheet.write(0, col, field, header_style)
            worksheet.set_column(col, col, 20)  # Adjust column width

        # Write Data Rows
        for row_idx, row in enumerate(rows):
            unfoldable = row[-1]
            row.pop(-1)
            
            for col_idx, cell_value in enumerate(row):
                style = bold_style if unfoldable or row_idx + 1 in [2, 5] else data_style
                
                if isinstance(cell_value, str):
                    cell_value = re.sub("\r", " ", cell_value)
                    cell_value = cell_value[:32767]  # Excel cell limit
                
                worksheet.write(row_idx + 1, col_idx, cell_value, style)

        workbook.close()
        output.seek(0)
        return output.read()
