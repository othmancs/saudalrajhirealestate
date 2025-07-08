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
        """إصدار محسن لتحليل جدول الدفعات مع دعم متقدم للجداول"""
        try:
            with fitz.open(stream=pdf_data, filetype="pdf") as pdf_document:
                if not pdf_document.is_pdf:
                    _logger.warning("ملف PDF غير صالح")
                    return -1
                
                # قراءة النص مع الحفاظ على الهيكل
                full_text = ""
                for page in pdf_document:
                    full_text += page.get_text("text", flags=fitz.TEXT_PRESERVE_LIGATURES | fitz.TEXT_PRESERVE_WHITESPACE)
                
                _logger.debug(f"النص الكامل المستخرج:\n{full_text[:2000]}...")
                
                # أنماط متعددة للبحث عن الجدول
                table_patterns = [
                    r'(Rent Payments Schedule)(.*?)(?=\n\s*\n)',
                    r'(Amount|مقدار).*?(Due Date|تاريخ الاستحقاق)(.*?)(?=\n\s*\n)',
                    r'(\d+[/\.]\d+\.\d{2}).*?(\d{4}-\d{2}-\d{2})(.*?)(?=\n\s*\n)'
                ]
                
                table_text = ""
                for pattern in table_patterns:
                    match = re.search(pattern, full_text, re.DOTALL | re.IGNORECASE)
                    if match:
                        table_text = match.group(0)
                        _logger.debug(f"تم العثور على الجدول باستخدام النمط: {pattern}")
                        break
                
                if not table_text:
                    _logger.warning("تعذر العثور على جدول الدفعات في المستند")
                    return -1
                
                _logger.debug(f"محتوى الجدول المستخرج:\n{table_text}")
                
                # تحسين استخراج الصفوف
                payment_rows = []
                for line in table_text.split('\n'):
                    line = line.strip()
                    # شروط أكثر مرونة للتعرف على الدفعات
                    has_amount = re.search(r'(\d+[/\.]\d+\.\d{2}|\d+\.\d{2})', line)
                    has_date = re.search(r'(\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{2})', line)
                    
                    if has_amount and has_date:
                        payment_rows.append(line)
                        _logger.debug(f"تم تحديد صف الدفعة: {line}")
                
                if not payment_rows:
                    _logger.warning("لا توجد صفوف دفعات في الجدول")
                    return -1
                
                payment_count = len(payment_rows)
                _logger.info(f"عدد الدفعات المحددة: {payment_count}")
                return payment_count
                
        except Exception as e:
            _logger.error(f"خطأ فني في تحليل PDF: {str(e)}", exc_info=True)
            return -1

    def get_pdf_debug_info(self, pdf_attachment_id):
        """طريقة مساعدة للحصول على معلومات التصحيح"""
        attachment = self.env['ir.attachment'].browse(pdf_attachment_id)
        if not attachment.exists():
            return {"error": "الملف المرفق غير موجود"}
        
        try:
            pdf_data = self._safe_read_attachment(attachment)
            with fitz.open(stream=pdf_data, filetype="pdf") as doc:
                text = ""
                for page in doc:
                    text += page.get_text("text", flags=fitz.TEXT_PRESERVE_LIGATURES | fitz.TEXT_PRESERVE_WHITESPACE)
                
                return {
                    "text_sample": text[:2000],
                    "page_count": len(doc),
                    "analysis_result": self._analyze_pdf_content(pdf_data),
                    "table_pattern_matches": [
                        (pattern, bool(re.search(pattern, text, re.DOTALL | re.IGNORECASE)))
                        for pattern in [
                            r'(Rent Payments Schedule|جدول سداد الدفعات)',
                            r'(Amount|مقدار).*?(Due Date|تاريخ الاستحقاق)',
                            r'(\d+[/\.]\d+\.\d{2}).*?(\d{4}-\d{2}-\d{2})'
                        ]
                    ]
                }
        except Exception as e:
            return {"error": str(e)}

    def debug_pdf_content(self):
        """وظيفة إضافية لتصحيح مشاكل PDF"""
        if not self.rental_attachment_ids:
            return {"error": "لا يوجد مرفقات PDF"}
        
        try:
            pdf_attachment = self.rental_attachment_ids[0]
            return self.get_pdf_debug_info(pdf_attachment.id)
        except Exception as e:
            return {"error": str(e)}

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

    @api.constrains('pending_payments_count')
    def _check_payment_count(self):
        """التحقق من صحة عدد الدفعات"""
        for order in self:
            if order.pending_payments_count < 0:
                raise ValidationError(_("عدد الدفعات لا يمكن أن يكون سالباً"))

    def action_show_pdf_text(self):
        """عرض محتوى PDF للتحقق"""
        self.ensure_one()
        if not self.rental_attachment_ids:
            raise UserError(_("لا يوجد مرفقات PDF"))
        
        try:
            pdf_attachment = self.rental_attachment_ids[0]
            pdf_data = self._safe_read_attachment(pdf_attachment)
            
            with fitz.open(stream=pdf_data, filetype="pdf") as pdf_document:
                text = ""
                for page in pdf_document:
                    text += page.get_text("text")
                
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('محتوى PDF'),
                    'res_model': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_text': text[:5000]  # عرض أول 5000 حرف
                    }
                }
                
        except Exception as e:
            raise UserError(_("تعذر قراءة محتوى PDF: %s") % str(e))
