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

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    renting_attachment_ids = fields.One2many(
        'ir.attachment',
        'res_id',
        string='Renting PDF Attachments',
        domain=[('res_model', '=', 'account.move'), ('mimetype', '=', 'application/pdf')],
        auto_join=True
    )
    
    pending_invoices_count = fields.Integer(
        string='عدد الفواتير المستحقة',
        compute='_compute_pending_invoices_count',
        store=True,
        help='Number of pending invoices based on Rent Payments Schedule'
    )
    
    pdf_analysis_status = fields.Selection([
        ('not_analyzed', 'Not Analyzed'),
        ('analyzed', 'Analyzed'),
        ('error', 'Error')],
        string='PDF Analysis Status',
        compute='_compute_pending_invoices_count',
        store=True
    )
    @api.depends('invoice_line_ids', 'renting_attachment_ids')
    def _compute_pending_invoices_count(self):
        for invoice in self.with_context(prefetch_fields=False):
            invoice.pending_invoices_count = 0
            invoice.pdf_analysis_status = 'not_analyzed'
            
            attachments = invoice.sudo().renting_attachment_ids.filtered(
                lambda a: a.mimetype == 'application/pdf'
            )
            
            if not attachments:
                continue
                
            try:
                pdf_attachment = attachments[0]
                pdf_data = self._safe_read_attachment(pdf_attachment)
                
                if not pdf_data:
                    _logger.warning(f"Empty PDF data for attachment {pdf_attachment.id}")
                    continue
                    
                payment_count = self._analyze_pdf_content(pdf_data)
                
                if payment_count > 0:
                    invoice.pending_invoices_count = payment_count
                    invoice.pdf_analysis_status = 'analyzed'
                elif payment_count == 0:
                    invoice.pdf_analysis_status = 'analyzed'
                else:
                    invoice.pdf_analysis_status = 'error'
                    
            except Exception as e:
                _logger.error(f"Failed to analyze PDF for invoice {invoice.id}: {str(e)}")
                invoice.pdf_analysis_status = 'error'

    # @api.depends('invoice_line_ids', 'renting_attachment_ids')
    # def _compute_pending_invoices_count(self):
    #     for invoice in self.with_context(prefetch_fields=False):
    #         invoice.pending_invoices_count = 0
    #         invoice.pdf_analysis_status = 'not_analyzed'
            
    #         try:
    #             # زيادة مهلة التنفيذ
    #             self.env.cr.execute("SET LOCAL statement_timeout = 30000;")
                
    #             # قراءة المرفقات مع تجنب مشاكل ال cache
    #             attachments = invoice.sudo().with_context(
    #                 bin_size=False,
    #                 bin_size_attachment=False
    #             ).renting_attachment_ids.filtered(
    #                 lambda a: a.mimetype == 'application/pdf'
    #             )
                
    #             _logger.info(f"Processing invoice ID {invoice.id}, found {len(attachments)} PDF attachments")
                
    #             if not attachments:
    #                 continue
                    
    #             # استخدام المرفق الأول فقط
    #             pdf_attachment = attachments[0]
                
    #             # طريقة آمنة لقراءة الملف
    #             pdf_data = self._safe_read_attachment(pdf_attachment)
    #             if not pdf_data:
    #                 continue
                
    #             # تحليل PDF
    #             payment_count = self._analyze_pdf_content(pdf_data)
    #             if payment_count >= 0:
    #                 invoice.pending_invoices_count = payment_count
    #                 invoice.pdf_analysis_status = 'analyzed'
    #                 _logger.info(f"Successfully analyzed invoice {invoice.id}, found {payment_count} payments")
                
    #         except Exception as e:
    #             invoice.pdf_analysis_status = 'error'
    #             _logger.error(f"Error analyzing PDF for invoice {invoice.id}: {str(e)}", exc_info=True)
    #             continue
    
    def _safe_read_attachment(self, attachment):
        """قراءة آمنة لمحتوى المرفق مع معالجة الأخطاء"""
        try:
            if attachment.store_fname:
                # القراءة من نظام الملفات
                file_path = attachment._full_path(attachment.store_fname)
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        return f.read()
                else:
                    _logger.error(f"Attachment file not found at {file_path}")
                    return None
            else:
                # القراءة من قاعدة البيانات
                return attachment.raw
        except IOError as e:
            _logger.error(f"Failed to read attachment {attachment.id}: {str(e)}")
            return None
        except Exception as e:
            _logger.error(f"Unexpected error reading attachment {attachment.id}: {str(e)}")
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
                
                # البحث عن جدول الدفعات
                schedule_pattern = r'rent\s*payments?\s*schedule(.*?)(?=\n\s*\n|\Z)'
                match = re.search(schedule_pattern, text, re.DOTALL)
                
                if not match:
                    _logger.warning("Rent Payments Schedule table not found")
                    return -1
                    
                table_text = match.group(1)
                
                # استخراج الصفوف من الجدول
                rows = [row.strip() for row in table_text.split('\n') if row.strip()]
                
                if not rows:
                    _logger.warning("No rows found in the schedule table")
                    return -1
                
                # العثور على العمود الأول (يحتوي على أرقام الدفعات)
                payment_numbers = []
                for row in rows:
                    # تقسيم كل صف إلى أعمدة (تفترض وجود فواصل مثل مسافات أو Tabs)
                    columns = re.split(r'\s{2,}|\t', row)
                    if columns and columns[0].isdigit():
                        payment_numbers.append(int(columns[0]))
                
                if not payment_numbers:
                    _logger.warning("No payment numbers found in first column")
                    return -1
                    
                max_payment = max(payment_numbers)
                _logger.info(f"Found {max_payment} payments in schedule table")
                return max_payment
                
        except Exception as e:
            _logger.error(f"Error analyzing PDF content: {str(e)}", exc_info=True)
            return -1
    # def _analyze_pdf_content(self, pdf_data):
    #     """تحليل محتوى PDF واستخراج عدد الدفعات"""
    #     try:
    #         with fitz.open(stream=pdf_data, filetype="pdf") as pdf_document:
    #             if not pdf_document.is_pdf:
    #                 _logger.warning("File is not a valid PDF")
    #                 return -1
                
    #             text = ""
    #             for page in pdf_document:
    #                 text += page.get_text()
                
    #             _logger.debug(f"Extracted PDF text (first 500 chars): {text[:500]}...")
                
    #             # البحث عن جدول الدفعات
    #             rent_schedule_pattern = r'(Rent\s*Payments?\s*Schedule|جدول\s*دفعات\s*الإيجار)(.*?)(?=\n\s*\n|\Z)'
    #             match = re.search(rent_schedule_pattern, text, re.DOTALL | re.IGNORECASE)
                
    #             if not match:
    #                 _logger.warning("Rent Payments Schedule not found in PDF")
    #                 return -1
                
    #             schedule_text = match.group(2)
    #             _logger.debug(f"Found schedule text: {schedule_text[:200]}...")
                
    #             # البحث عن تواريخ الدفعات
    #             date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|[\d]{4}-[\d]{2}-[\d]{2})'
    #             dates = re.findall(date_pattern, schedule_text)
                
    #             if not dates:
    #                 _logger.warning("No payment dates found in the schedule")
    #                 return 0
                
    #             unique_dates = set(dates)
    #             return len(unique_dates)
                
    #     except Exception as e:
    #         _logger.error(f"Error analyzing PDF content: {str(e)}")
    #         return -1
    
    def action_analyze_pdf_attachments(self):
        """Manual trigger for PDF analysis"""
        try:
            self._compute_pending_invoices_count()
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('PDF Analysis'),
                    'message': _('PDF analysis completed successfully.'),
                    'sticky': False,
                    'type': 'success',
                }
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('PDF Analysis Error'),
                    'message': _('Error during PDF analysis: %s') % str(e),
                    'sticky': False,
                    'type': 'danger',
                }
            }
