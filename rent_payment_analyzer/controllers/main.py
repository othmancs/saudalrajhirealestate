from odoo import http
from odoo.http import request


class PDFAnalysisController(http.Controller):
    @http.route('/rent_payment_analyzer/analyze_rental', type='json', auth='user')
    def analyze_pdf(self, order_id, **kwargs):
        order = request.env['sale.order'].browse(int(order_id))
        if not order.exists():
            return {'error': 'Rental order not found', 'success': False}

        try:
            order._compute_pending_payments_count()
            return {
                'success': True,
                'count': order.pending_payments_count,
                'status': order.pdf_analysis_status,
                'message': order.pdf_analysis_message
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }