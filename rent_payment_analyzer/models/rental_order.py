import logging
import re
import os
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

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
        string='مرفقات التأجير',
        domain=[('res_model', '=', 'sale.order'), ('mimetype', '=', 'application/pdf')],
        auto_join=True
    )
    
    pending_payments_count = fields.Integer(
        string='عدد الدفعات المستحقة',
        compute='_compute_pending_payments_count',
        store=True,
        help='عدد الدفعات المتبقية بناءً على جدول الدفعات'
    )
    
    pdf_analysis_status = fields.Selection([
        ('not_analyzed', 'لم يتم التحليل'),
        ('analyzed', 'تم التحليل'),
        ('error', 'خطأ')],
        string='حالة تحليل PDF',
        compute='_compute_pending_payments_count',
        store=True
    )
    
    pdf_analysis_message = fields.Text(
        string='رسالة التحليل',
        compute='_compute_pending_payments_count'
    )

    @api.depends('order_line', 'rental_attachment_ids')
    def _compute_pending_payments_count(self):
        for order in self.with_context(prefetch_fields=False):
            order._analyze_pdf_attachments()

    def _analyze_pdf_attachments(self):
        """تحليل المرفقات PDF وحساب عدد الدفعات"""
        self.ensure_one()
        self.pending_payments_count = 0
        self.pdf_analysis_status = 'not_analyzed'
        self.pdf_analysis_message = 'لا يوجد مرفقات PDF'
        
        if not self.rental_attachment_ids:
            return
            
        try:
            pdf_attachment = self.rental_attachment_ids[0]
            pdf_data = self._safe_read_attachment(pdf_attachment)
            
            if not pdf_data:
                self.pdf_analysis_message = 'تعذر قراءة ملف PDF'
                self.pdf_analysis_status = 'error'
                return
                
            payment_count = self._analyze_pdf_content(pdf_data)
            
            if payment_count > 0:
                self.pending_payments_count = payment_count
                self.pdf_analysis_status = 'analyzed'
                self.pdf_analysis_message = f'تم العثور على {payment_count} دفعات في الجدول'
            elif payment_count == 0:
                self.pdf_analysis_status = 'analyzed'
                self.pdf_analysis_message = 'لم يتم العثور على دفعات في الجدول'
            else:
                self.pdf_analysis_status = 'error'
                self.pdf_analysis_message = 'خطأ في تحليل ملف PDF'
                
        except Exception as e:
            self.pdf_analysis_status = 'error'
            self.pdf_analysis_message = f'خطأ في التحليل: {str(e)}'
            _logger.error(f"Failed to analyze PDF for order {self.id}: {str(e)}", exc_info=True)

    def _safe_read_attachment(self, attachment):
        """قراءة آمنة لمحتوى المرفق"""
        try:
            if attachment.store_fname:
                file_path = attachment._full_path(attachment.store_fname)
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        return f.read()
                _logger.error(f"File not found: {file_path}")
            return attachment.raw
        except Exception as e:
            _logger.error(f"Error reading attachment: {str(e)}")
            return None

    def _analyze_pdf_content(self, pdf_data):
        """تحليل محتوى PDF واستخراج عدد الدفعات"""
        try:
            with fitz.open(stream=pdf_data, filetype="pdf") as pdf_document:
                if not pdf_document.is_pdf:
                    _logger.warning("Invalid PDF file")
                    return -1
                
                text = ""
                for page in pdf_document:
                    text += page.get_text("text").lower()
                
                # أنماط البحث عن جدول الدفعات
                patterns = [
                    r'rent\s*payments?\s*schedule(.*?)(?=\n\s*\n|\Z)',
                    r'جدول\s*دفعات?\s*الإيجار(.*?)(?=\n\s*\n|\Z)'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, text, re.DOTALL)
                    if match:
                        table_text = match.group(1)
                        rows = [row.strip() for row in table_text.split('\n') if row.strip()]
                        
                        if rows:
                            # استخراج الأرقام من العمود الأول
                            numbers = []
                            for row in rows:
                                cols = re.split(r'\s{2,}|\t', row)
                                if cols and cols[0].isdigit():
                                    numbers.append(int(cols[0]))
                            
                            if numbers:
                                return max(numbers)
                
                _logger.warning("No payment schedule found in PDF")
                return -1
                
        except Exception as e:
            _logger.error(f"PDF analysis error: {str(e)}", exc_info=True)
            return -1

    def action_analyze_pdf_attachments(self):
        """تحليل المرفقات يدوياً"""
        self._analyze_pdf_attachments()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('تحليل PDF'),
                'message': self.pdf_analysis_message,
                'sticky': False,
                'type': 'success' if self.pdf_analysis_status == 'analyzed' else 'danger',
            }
        }
