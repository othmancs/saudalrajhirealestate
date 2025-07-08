from odoo import http
from odoo.http import request
import json


class PDFAnalysisController(http.Controller):
    @http.route('/rent_payment_analyzer/analyze', type='json', auth='user')
    def analyze_pdf(self, invoice_id, **kwargs):
        invoice = request.env['account.move'].browse(int(invoice_id))
        if not invoice.exists():
            return {'error': 'Invoice not found'}

        try:
            invoice._compute_pending_invoices_count()
            return {
                'success': True,
                'count': invoice.pending_invoices_count,
                'status': invoice.pdf_analysis_status
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }