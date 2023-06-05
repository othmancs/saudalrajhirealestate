from odoo import api, models, fields, _
from hijri_converter import Hijri, Gregorian
import ast


ReportActions = {
    'transfer': 'action_report_transfer',
    'eviction': 'action_report_vacating',
    'commercial': 'action_report_commercial',
    'personal': 'action_report_personal',
    'value_update': 'action_report_value_update',
    'payment_claim': 'action_report_payment_claim',
    'termination': 'action_report_contract_termination',
    'return': 'action_report_return',
    'pickup': 'action_report_pickup'
}


class RentalLetterTemplate(models.Model):
    _name = 'rental.letter.template'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Rental Letter Templates'
    _rec_name = 'ref'

    ref = fields.Char(string='Reference')
    subject = fields.Selection([('eviction', 'اخلاء عقار'),
                                ('return', 'تسليم العين المؤجرة من المستأجر'),
                                ('pickup', 'استلام العين المؤجرة من المستأجر'),
                                ('transfer', 'تنازل عن عقد ايجار'),
                                ('commercial', 'طلب تأجير تجاري'),
                                ('personal', 'طلب تأجير فردي'),
                                ('value_update', 'تحديث القيمة الإيجارية'),
                                ('payment_claim', 'مطالبة بسداد متأخرات'),
                                ('termination', 'إشعار بإنهاء التعاقد'),
                                ], string='Subject', required=True)

    today_date = fields.Date(string='Request Date', default=fields.Date.context_today)
    assigner_identity = fields.Char(related='assigner_id.partner_id.national_id_number', string='Assigner ID',
                                    readonly=False)
    assigner_identity_date = fields.Date(string='Assigner ID Issue Date')
    unit_id = fields.Many2one('sale.order.line', string='Unit Number', domain="[('order_id', '=', assigner_id)]")
    property_id = fields.Many2one('rent.property', related="unit_id.property_number", string="Property")
    state_unit_id = fields.Many2one('rent.sale.state', string='Unit Number',
                                    domain="[('sale_order_id', '=', assigner_id)]")
    city = fields.Char(string='City')
    neighborhood = fields.Char(string='Neighborhood')
    cash_receipts = fields.Char(string='Cash Receipts No.')
    cash_receipts_date = fields.Date(string='Cash Receipts Date')
    cash_receipts_value = fields.Char(string='Cash Receipts Value')
    user_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user)
    eviction_state = fields.Selection([('done', 'Termination Done'), ('refused', 'Termination Refused')])
    e_invoice = fields.Char(string='e-invoice No.')
    e_invoice_date = fields.Date(string='e-invoice Date')
    insurance_value = fields.Float(related="unit_id.insurance_value", readonly=False, string='Insurance Value')
    delay_date = fields.Date(string='Delay Date')
    company_id = fields.Many2one('res.company', store=True, copy=False,
                                 string="Company",
                                 default=lambda self: self.env.company)
    company_partner_id = fields.Many2one('res.partner', related='company_id.partner_id')
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  related='company_id.currency_id',
                                  default=lambda
                                      self: self.env.user.company_id.currency_id.id)
    fee = fields.Char(string="Charges day's rental")
    partner_id = fields.Many2one('res.partner', string='Customer' , related="assigner_id.partner_id", readonly=False,
                                 store=True)
    beginning_contract = fields.Date(related='assigner_id.fromdate', String='Contract Date')
    contract_number = fields.Char(related='assigner_id.contract_number', String='Contract Number', readonly=False)
    end_contract = fields.Date(related='assigner_id.todate')
    number = fields.Char(string='Letter No.')
    rental_value = fields.Float(string='Rental Value')
    new_rental_value = fields.Float(string='New Rental Value')
    location = fields.Char(string='Location')
    property_type_id = fields.Many2one('rent.config.property.types', string='Property Type')
    change_reason = fields.Text(string='Change Reason')
    bank_id = fields.Many2one('res.partner.bank', string='Bank', domain="[('partner_id', '=', company_partner_id)]")
    bank_account = fields.Char(related="bank_id.acc_number", string='Bank Account')
    iban = fields.Char(related="bank_id.iban_number", string='IBAN')
    payment_period = fields.Char(string='Payment Period')
    contract_date = fields.Date(string='Contract Date')
    new_contract_date = fields.Date(string='New Contract Date')
    transfer_date = fields.Date(related="new_rental_id.fromdate", string='Transfer Date')
    eviction_period = fields.Char(string='Eviction Period')
    daily_rent_value = fields.Float(string='Daily Rent Value')
    insurance_officer = fields.Char(string='Insurance Officer')
    insurance_officer_opinion = fields.Text(string='Opinion')
    property_manager = fields.Char(string='Property manager')
    property_manager_opinion = fields.Text(string='Property manager Opinion')
    assigner_id = fields.Many2one('sale.order', string='Customer')
    new_rental_id = fields.Many2one('sale.order', domain="[('transferred_id','=', assigner_id)]", copy=False)
    crn = fields.Char(string='Commercial Registration Number')
    national_address_main_center = fields.Char(string='National Address Of The Main Center')
    contact_number = fields.Char(string='Contact Number')
    renting_purpose = fields.Char(string='Renting Purpose')
    nature_of_commerce = fields.Char(string='Nature of commerce')
    authorized_manager_id = fields.Char(string='Authorized Manager')
    authorized_identity = fields.Char(string='Authorized Manager Identity')
    targeted_group = fields.Char(string='Targeted Group')
    invoice_ids = fields.One2many('rent.due.invoice', 'letter_template_id', string='Due Invoices')
    door_good = fields.Boolean(string='جيد')
    door_bad = fields.Boolean(string='سئ')
    door_comment = fields.Char(string='حدد')
    door_note = fields.Text(string='ملاحظات')
    wall_good = fields.Boolean('جيد')
    wall_bad = fields.Boolean('سئ')
    wall_comment = fields.Char('حدد')
    wall_note = fields.Text(string='ملاحظات')
    window_good = fields.Boolean('جيد')
    window_bad = fields.Boolean('سئ')
    window_comment = fields.Char('حدد')
    window_note = fields.Text(string='ملاحظات')
    water_good = fields.Boolean('جيد')
    water_bad = fields.Boolean('سئ')
    water_comment = fields.Char('حدد')
    water_note = fields.Text(string='ملاحظات')
    elec_good = fields.Boolean('جيد')
    elec_bad = fields.Boolean('سئ')
    elec_comment = fields.Char('حدد')
    elec_note = fields.Text(string='ملاحظات')
    customer_accept = fields.Boolean('نعم')
    customer_refused = fields.Boolean('لا')
    rental_payments_yes = fields.Boolean('نعم')
    rental_payments_no = fields.Boolean('لا')
    rental_payments = fields.Monetary(string='المبلغ')
    remaining_amount_yes = fields.Boolean('نعم')
    remaining_amount_no = fields.Boolean('لا')
    remaining_amount = fields.Monetary(string='المبلغ')
    elec_yes = fields.Boolean('نعم')
    elec_no = fields.Boolean('لا')
    elec_amount = fields.Monetary(string='المبلغ')
    electricity_meter_no = fields.Char('رقم عداد الكهرباء')
    electricity_amount_due = fields.Char('المبلغ المستحق')
    elec_found = fields.Boolean('يوجد')
    elec_not_found = fields.Boolean('لا يوجد')
    elec_payment = fields.Boolean('تم السداد')
    elec_not_payment = fields.Boolean('لم يتم السداد ')
    water_meter_no = fields.Char('رقم عداد المياه')
    water_amount_due = fields.Char('المبلغ المستحق')
    water_found = fields.Boolean('يوجد')
    water_not_found = fields.Boolean('لا يوجد')
    water_payment = fields.Boolean('تم السداد')
    water_not_payment = fields.Boolean('لم يتم السداد ')
    contract_value = fields.Monetary(string="Contract Value", related="assigner_id.amount_total")
    due_amount = fields.Float(string="Contract Due Value", related="assigner_id.amount_remain")
    deposits_paid = fields.Monetary(string="التأمين المدفوع")
    mangement_accept = fields.Boolean('نعم')
    mangement_refused = fields.Boolean('لا')
    note = fields.Text(string='ملاحظة')
    employer = fields.Char(string='Employer')
    job = fields.Char(string='Job')
    salary_definition = fields.Char(string='Salary Definition')
    martial_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], string='Marital Status', default='single', tracking=True)
    family_members = fields.Integer(string='Family Members')
    simah_report = fields.Char(string='Simah Report')
    chief_executive = fields.Boolean('موافق')
    chief_executive_no = fields.Boolean('غير موافق')
    assignee = fields.Char(string='Assignee')
    termination_notice_period = fields.Char(string='Termination Notice Period')
    end_contractual_relationship = fields.Date(string='Date end of the contractual relationship')
    leased_property = fields.Date(string='Date of leased property')
    vacating_the_property = fields.Char(string='Days vacating the property')
    new_rental_year = fields.Date(string='New Rental Year')
    assignee_identity = fields.Char(related='new_rental_id.partner_id.national_id_number', string='Assignee ID',
                                    readonly=False)
    assignee_identity_date = fields.Date(string='Assignee ID Issue Date')
    rental_value_old = fields.Monetary(string="Rental Value")
    rental_value_new = fields.Monetary(string="Rental Value new")
    evacuated = fields.Boolean(string='Evacuated')

    def action_open_rental_contract(self):
        action = self.env.ref("sale_renting.rental_order_action").sudo().read()[0]
        action["domain"] = [("id", "in", self.assigner_id.id)]
        view_id = self.env.ref('sale_renting.rental_order_primary_form_view').id
        action['views'] = [(view_id, 'form')]
        action['res_id'] = self.assigner_id.id
        ctx = ast.literal_eval(action['context'])
        ctx.update({'create':  False, 'delete': False})
        action['context'] = str(ctx)
        return action

    def action_evacuation(self):
        for record in self:
            invoice_ids = record.sudo().assigner_id.invoice_ids
            asset_ids = invoice_ids.mapped('asset_ids')
            for asset in asset_ids.filtered(lambda line: line.asset_type == 'sale'):
                asset.depreciation_move_ids.filtered(lambda mov: mov.state == 'draft').button_cancel()
                asset.write({'state': 'close'})
            invoice_ids.filtered(lambda inv: inv.state == 'draft').button_cancel()
            record.assigner_id.state = 'termination'
            record.evacuated = True

    def print_letter(self):
        action = self.env.ref('rent_customize.%s' % ReportActions[self.subject])
        return action.sudo().report_action(self, config=False)

    @api.model
    def create(self, vals):
        vals['ref'] = self.env["ir.sequence"].next_by_code('letters.sequence')
        return super(RentalLetterTemplate, self).create(vals)

    def get_date_hijri(self, gregorian_date):
        hijri_date = ''
        if gregorian_date:
            day = gregorian_date.day
            month = gregorian_date.month
            year = gregorian_date.year
            hijri_date = Gregorian(year, month, day).to_hijri()
        return hijri_date

    def _get_weekday_name(self, date):
        days_name = {
            '0': 'الاثنين',
            '1': 'الثلاثاء',
            '2': 'الأربعاء',
            '3': 'الخميس',
            '4': 'الجمعة',
            '5': 'السبت',
            '6': 'ألأخد',
        }
        day_name = date.weekday()
        return days_name[str(day_name)]


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def name_get(self):
        if not self._context.get('letter'):
            return super(SaleOrder, self).name_get()
        res = []
        for record in self:
            name = str(record.partner_id.name) + "[" + record.name + "]"
            res.append((record.id, name))
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def name_get(self):

        if not self._context.get('letter_unit'):
            return super(SaleOrderLine, self).name_get()
        res = []
        for line in self:
            name = str(line.product_id.name) + "[" + line.product_id.unit_number + "]"
            res.append((line.id, name))
        return res


class RentDueInvoice(models.Model):
    _name = 'rent.due.invoice'

    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    amount = fields.Float(string='Due Amount')
    tax_amount = fields.Float(string='Tax Amount')
    total = fields.Float(string='Total')
    tax_ids = fields.Many2many('account.tax', string="Taxes")
    letter_template_id = fields.Many2one('rental.letter.template')

    # @api.depends('amount','tax_amount')
    # def _compute_price(self):
    #     for line in self:
