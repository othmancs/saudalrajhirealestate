import logging
import io
from odoo import models, fields, api, tools
from odoo.exceptions import UserError
import PyPDF2
import re

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    pending_invoices_count = fields.Integer(
        string='عدد الفواتير المستحقة',
        compute='_compute_pending_invoices_count',
        store=True,
        help='Number of pending invoices based on Rent Payments Schedule'
    )
    
    @api.depends('invoice_line_ids', 'attachment_ids')
    def _compute_pending_invoices_count(self):
        for invoice in self:
            invoice.pending_invoices_count = 0
            attachments = invoice.attachment_ids.filtered(
                lambda a: a.mimetype == 'application/pdf'
            )
            
            if attachments:
                try:
                    # Get the first PDF attachment
                    pdf_attachment = attachments[0]
                    pdf_data = pdf_attachment.raw
                    
                    # Create a PDF file reader object
                    pdf_file = io.BytesIO(pdf_data)
                    pdf_reader = PyPDF2.PdfFileReader(pdf_file)
                    
                    # Extract text from all pages
                    text = ""
                    for page_num in range(pdf_reader.numPages):
                        page = pdf_reader.getPage(page_num)
                        text += page.extractText()
                    
                    # Find Rent Payments Schedule table
                    rent_schedule_pattern = r'Rent Payments Schedule(.*?)(?=\n\n|\Z)'
                    match = re.search(rent_schedule_pattern, text, re.DOTALL | re.IGNORECASE)
                    
                    if match:
                        schedule_text = match.group(1)
                        # Count number of columns (assuming each payment is a column)
                        # This is a simple approach - you may need to adjust based on your PDF structure
                        columns = re.findall(r'\d{1,2}/\d{1,2}/\d{2,4}', schedule_text)
                        invoice.pending_invoices_count = len(set(columns)) if columns else 0
                    else:
                        _logger.warning("Rent Payments Schedule not found in PDF")
                        
                except Exception as e:
                    _logger.error(f"Error analyzing PDF: {str(e)}")
                    raise UserError(f"Error analyzing PDF: {str(e)}")