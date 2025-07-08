import logging
import re
import os
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    import fitz  # PyMuPDF
except ImportError:
    _logger.error("PyMuPDF library is not installed. Please install it with: pip install pymupdf")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    rental_attachment_ids = fields.One2many(
        'ir.attachment',
        'res_id',
        string='Rental PDF Attachments',
        domain=[('res_model', '=', 'sale.order'), ('mimetype', '=', 'application/pdf')],
        auto_join=True
    )

    pending_payments_count = fields.Integer(
        string='عدد الدفعات المستحقة',
        compute='_compute_pending_payments_count',
        store=True,
        help='Number of pending payments based on Rent Payments Schedule'
    )

    pdf_analysis_status = fields.Selection([
        ('not_analyzed', 'Not Analyzed'),
        ('analyzed', 'Analyzed'),
        ('error', 'Error')],
        string='PDF Analysis Status',
        compute='_compute_pending_payments_count',
        store=True
    )

    pdf_analysis_message = fields.Text(
        string='Analysis Message',
        compute='_compute_pending_payments_count'
    )

    @api.depends('order_line', 'rental_attachment_ids')
    def _compute_pending_payments_count(self):
        for order in self.with_context(prefetch_fields=False):
            order.pending_payments_count = 0
            order.pdf_analysis_status = 'not_analyzed'
            order.pdf_analysis_message = ''

            attachments = order.sudo().rental_attachment_ids.filtered(
                lambda a: a.mimetype == 'application/pdf'
            )

            if not attachments:
                order.pdf_analysis_message = 'No PDF attachments found'
                continue

            try:
                pdf_attachment = attachments[0]
                pdf_data = self._safe_read_attachment(pdf_attachment)

                if not pdf_data:
                    order.pdf_analysis_message = 'Could not read PDF file'
                    continue

                payment_count = self._analyze_pdf_content(pdf_data)

                if payment_count > 0:
                    order.pending_payments_count = payment_count
                    order.pdf_analysis_status = 'analyzed'
                    order.pdf_analysis_message = f'Found {payment_count} payments in schedule'
                elif payment_count == 0:
                    order.pdf_analysis_status = 'analyzed'
                    order.pdf_analysis_message = 'No payments found in schedule'
                else:
                    order.pdf_analysis_status = 'error'
                    order.pdf_analysis_message = 'Error analyzing PDF content'

            except Exception as e:
                order.pdf_analysis_status = 'error'
                order.pdf_analysis_message = f'Analysis error: {str(e)}'
                _logger.error(f"Failed to analyze PDF for order {order.id}: {str(e)}")

    def _safe_read_attachment(self, attachment):
        """قراءة آمنة لمحتوى المرفق"""
        try:
            if attachment.store_fname:
                file_path = attachment._full_path(attachment.store_fname)
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        return f.read()
                else:
                    _logger.error(f"Attachment file not found at {file_path}")
                    return None
            else:
                return attachment.raw
        except Exception as e:
            _logger.error(f"Error reading attachment {attachment.id}: {str(e)}")
            return None

    def _analyze_pdf_content(self, pdf_data):
        """تحليل محتوى PDF واستخراج عدد الدفعات من العمود الأول في الجدول"""
        try:
            with fitz.open(stream=pdf_data, filetype="pdf") as pdf_document:
                if not pdf_document.is_pdf:
                    _logger.warning("File is not a valid PDF")
                    return -1

                text = ""
                for page in pdf_document:
                    text += page.get_text("text").lower()

                _logger.debug(f"Extracted PDF text (first 1000 chars): {text[:1000]}...")

                # أنماط البحث عن جدول الدفعات
                schedule_patterns = [
                    r'rent\s*payments?\s*schedule.*?(\d.*?)(?=\n\s*\n|\Z)',
                    r'جدول\s*دفعات?\s*الإيجار.*?(\d.*?)(?=\n\s*\n|\Z)',
                    r'payment\s*schedule.*?(\d.*?)(?=\n\s*\n|\Z)'
                ]

                for pattern in schedule_patterns:
                    match = re.search(pattern, text, re.DOTALL)
                    if match:
                        table_text = match.group(1)
                        rows = [row.strip() for row in table_text.split('\n') if row.strip()]

                        if rows:
                            # استخراج الأرقام من العمود الأول
                            numbers = []
                            for row in rows:
                                first_col = re.split(r'\s{2,}|\t', row)[0]
                                if first_col.isdigit():
                                    numbers.append(int(first_col))

                            if numbers:
                                return max(numbers)

                _logger.warning("No payment numbers found in first column of any schedule table")
                return -1

        except Exception as e:
            _logger.error(f"Error analyzing PDF content: {str(e)}", exc_info=True)
            return -1

    def action_analyze_pdf_attachments(self):
        """Trigger PDF analysis manually"""
        self._compute_pending_payments_count()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('PDF Analysis'),
                'message': self.pdf_analysis_message,
                'sticky': False,
                'type': 'success' if self.pdf_analysis_status == 'analyzed' else 'danger',
            }
        }