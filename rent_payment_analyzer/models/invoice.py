import logging
import re
import io
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    import fitz  # PyMuPDF
except ImportError:
    _logger.error("PyMuPDF library is not installed. Please install it with: pip install pymupdf")


class AccountMove(models.Model):
    _inherit = 'account.move'

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

    @api.depends('invoice_line_ids', 'attachment_ids')
    def _compute_pending_invoices_count(self):
        for invoice in self:
            invoice.pending_invoices_count = 0
            invoice.pdf_analysis_status = 'not_analyzed'

            attachments = invoice.attachment_ids.filtered(
                lambda a: a.mimetype == 'application/pdf'
            )

            if not attachments:
                continue

            try:
                # Get the first PDF attachment
                pdf_attachment = attachments[0]
                pdf_data = pdf_attachment.raw

                # Analyze PDF using PyMuPDF
                with fitz.open(stream=pdf_data, filetype="pdf") as pdf_document:
                    if not pdf_document.is_pdf:
                        raise UserError(_("The attached file is not a valid PDF"))

                    text = ""
                    for page in pdf_document:
                        text += page.get_text()

                    _logger.debug(f"Extracted PDF text (first 500 chars): {text[:500]}...")

                    # Enhanced pattern matching for rent schedule
                    rent_schedule_pattern = r'(Rent\s*Payments?\s*Schedule|جدول\s*دفعات\s*الإيجار)(.*?)(?=\n\s*\n|\Z)'
                    match = re.search(rent_schedule_pattern, text, re.DOTALL | re.IGNORECASE)

                    if match:
                        schedule_text = match.group(2)
                        _logger.debug(f"Found schedule text: {schedule_text[:200]}...")

                        # Enhanced date pattern matching
                        date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|[\d]{4}-[\d]{2}-[\d]{2})'
                        dates = re.findall(date_pattern, schedule_text)

                        if dates:
                            unique_dates = set(dates)
                            invoice.pending_invoices_count = len(unique_dates)
                            invoice.pdf_analysis_status = 'analyzed'
                            _logger.info(f"Found {len(unique_dates)} unique payment dates in PDF")
                        else:
                            _logger.warning("No payment dates found in the schedule")
                    else:
                        _logger.warning("Rent Payments Schedule not found in PDF")

            except Exception as e:
                invoice.pdf_analysis_status = 'error'
                _logger.error(f"Error analyzing PDF for invoice {invoice.id}: {str(e)}", exc_info=True)
                # Don't raise error to avoid blocking invoice validation
                continue