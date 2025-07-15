# -*- coding: utf-8 -*-

from odoo import api, models, fields

class RentProduct(models.Model):
    _inherit = 'product.template'

    # Basic unit info
    unit_number = fields.Char(string='رقم الوحدة')
    unit_area = fields.Float(string='مساحة الوحدة')
    unit_floor_number = fields.Char(string='رقم الطابق')
    unit_rooms_number = fields.Char(string='عدد الغرف')
    unit_state = fields.Char(compute='_get_state', string='الحالة')
    rent_unit_area = fields.Float(string='المساحة')

    # Furniture info
    furniture_bedroom = fields.Boolean(string='غرفة نوم')
    furniture_bedroom_no = fields.Integer(string=' عدد غرف النوم')
    furniture_bathroom = fields.Boolean(string='حمام')
    furniture_bathroom_no = fields.Integer(string=' عدد الحمام')
    furniture_reception = fields.Boolean(string='ريسيبشن')
    furniture_reception_no = fields.Integer(string=' عدد الريسيبشن')
    furniture_kitchen = fields.Boolean(string='مطبخ')
    furniture_service_room = fields.Boolean(string='غرفة خدم')
    furniture_inventory = fields.Boolean(string='مخزن')
    furniture_inventory_no = fields.Integer(string=' عدد المخازن')
    furniture_setting_room = fields.Boolean(string='غرفة المعيشة')
    furniture_setting_room_no = fields.Integer(string=' عدد غرف المعيشة')
    furniture_central_air_conditioner = fields.Boolean(string='تكييف مركزي')
    furniture_split_air_conditioner = fields.Boolean(string='تكييف سبليت')
    furniture_split_air_conditioner_no = fields.Integer(string=' عدد تكييف سبليت')
    furniture_evaporator_cooler = fields.Boolean(string='مدخنة')
    furniture_evaporator_cooler_no = fields.Integer(string=' عدد المداخن')
    furniture_kitchen_installed = fields.Boolean(string='مطبخ مجهز')
    furniture_locker_installed = fields.Boolean(string='غرفة ملابس')
    furniture_locker_installed_no = fields.Integer(string=' عدد غرف الملابس')

    # Unit classification
    unit_construction_date = fields.Date(string='تاريخ الانشاء')
    rent_config_unit_overlook_id = fields.Many2one('rent.config.unit.overlooks', string='Unit Overlooking')
    rent_config_unit_type_id = fields.Many2one('rent.config.unit.types', string='Unit type')
    rent_config_unit_purpose_id = fields.Many2one('rent.config.unit.purposes', string='Unit Purpose')
    rent_config_unit_finish_id = fields.Many2one('rent.config.unit.finishes', string='Unit Finish')

    # Property linkage
    property_id = fields.Many2one('rent.property', string='عمارة')
    property_address_build = fields.Many2one('rent.property.build', string='المجمع', related='property_id.property_address_build', store=True, index=True)
    property_address_city = fields.Many2one('rent.property.city', string='المدينة', related='property_id.property_address_city', store=True)
    country = fields.Many2one('res.country', string='الدولة', related='property_id.country', store=True, index=True)
    operating_unit = fields.Many2many('operating.unit', string='الفرع ')
    
    # Utilities
    entry_number = fields.Char('عدد المداخل')
    entry_overlook = fields.Char('المداخل تطل علي')
    unit_gas = fields.Char(string='رقم عداد الغاز')
    unit_electricity = fields.Char(string='رقم عداد الكهرباء')
    unit_water = fields.Char(string='رقم عداد المياه')

    unit_expenses_count = fields.Integer(string='Total Expenses', compute='_unit_expenses_count', readonly=True)
    unit_sales_count = fields.Integer(string='Total Sales', compute='_unit_sales_count', readonly=True)
    unit_price = fields.Float(string='قيمة الوحدة', compute='_get_unit_price')
    unit_price_unit = fields.Char(string='مدة تأجير الوحدة')

    state_id = fields.Char(string="الحالة")
    analytic_account = fields.Many2one('account.analytic.account', string='الحساب التحليلي', readonly=True)
    ref_analytic_account = fields.Char(string='رقم اشارة الحساب التحليلي', readonly=True)
    property_analytic_account = fields.Many2one('account.analytic.account', string='الحساب التحليلي للعقار', related='property_id.analytic_account')
    property_analytic_account_parent = fields.Many2one('account.analytic.group', related='property_id.analytic_account.group_id')

    # Compute fields - no store
    partner_id = fields.Many2one('res.partner', compute="get_sale_data", string='العميل')
    amount_paid = fields.Float(compute="get_sale_data", string='المبلغ المدفوع')
    amount_due = fields.Float(compute="get_sale_data", string='المبلغ المستحق')
    contract_admin_fees = fields.Float(compute="get_sale_data", string='رسوم إدارية')
    contract_service_fees = fields.Float(compute="get_sale_data", string='رسوم الخدمات')
    insurance_value = fields.Float(compute="get_sale_data", string='قيمة التأمين')
    fromdate = fields.Date(compute="get_sale_data", string='تاريخ بداية العقد')
    todate = fields.Date(compute="get_sale_data", string='تاريخ نهاية العقد')
    contract_total = fields.Float(compute="get_sale_data", string='قيمة العقد')
    contract_service_sub_fees = fields.Float(string=' رسوم الخدمات الخاضعة ')
    contract_admin_sub_fees = fields.Float(string='رسوم ادارية خاضعة')
    operating_unit_id = fields.Many2one('operating.unit', string='الفرع ')

    # ✅ الحقل المخزن فقط
    last_sale_id = fields.Many2one('sale.order', string='رقم العقد', compute="_compute_last_sale", store=True)

    # @api.depends('id')
    def _compute_last_sale(self):
        for rec in self:
            pp = self.env['product.product'].search([('product_tmpl_id', '=', rec.id)])
            order_line_id = self.env['sale.order.line'].sudo().search([
                ('product_id', '=', pp.id),
                ('order_id.rental_status', 'in', ['return', 'pickup'])
            ], limit=1, order='id desc')
            rec.last_sale_id = order_line_id.order_id.id if order_line_id else False

    def get_sale_data(self):
        for rec in self:
            pp = self.env['product.product'].search([('product_tmpl_id', '=', rec.id)])
            order_line_id = rec.env['sale.order.line'].sudo().search([
                ('product_id', '=', pp.id), 
                ('order_id.rental_status','in',['return', 'pickup'])], 
                limit=1, order='id desc')

            rec.partner_id = order_line_id.order_id.partner_id.id if order_line_id else False
            rec.contract_admin_fees = order_line_id.contract_admin_fees if order_line_id else 0
            rec.insurance_value = order_line_id.insurance_value if order_line_id else 0
            rec.contract_service_fees = order_line_id.contract_service_fees if order_line_id else 0
            rec.fromdate = order_line_id.order_id.fromdate if order_line_id else False
            rec.todate = order_line_id.order_id.todate if order_line_id else False
            rec.operating_unit_id = order_line_id.order_id.operating_unit_id.id if order_line_id else False
            rec.amount_paid = sum(
                line.price_subtotal for line in order_line_id.order_id.invoice_ids.invoice_line_ids.filtered(
                    lambda l: l.move_id.payment_state == 'paid' and l.product_id == rec.product_variant_id)
            ) if order_line_id else 0
            rec.contract_total = order_line_id.order_id.amount_total if order_line_id else 0
            rec.amount_due = sum(
                order_line_id.order_id.order_line[0].price_unit / ll.sale_order_id.invoice_number
                for ll in order_line_id.order_id.order_contract_invoice.filtered(lambda l: l.status == 'uninvoiced')
            ) if order_line_id and order_line_id.order_id.order_line else 0
            rec.contract_service_sub_fees = order_line_id.contract_service_sub_fees if order_line_id else 0
            rec.contract_admin_sub_fees = order_line_id.contract_admin_sub_fees if order_line_id else 0

    # باقي الدوال بدون تعديل
    @api.depends('unit_state', 'state_id')
    def _get_state(self):
        for rec in self:
            rec.unit_state = 'شاغرة'
            rec.state_id = 'شاغرة'
            maintenance_id = self.env['maintenance.request'].sudo().search([
                ('property_id.product_tmpl_id', '=', rec.id),
                ('state', 'in', ('confirm', 'ongoing'))
            ])
            if maintenance_id:
                rec.state_id = 'تحت الصيانة'
                rec.unit_state = 'تحت الصيانة'
                return

            pp = self.env['product.product'].search([('product_tmpl_id', '=', rec.id)])
            order = self.env['sale.order.line'].sudo().search([
                ('product_id', '=', pp.id),
                ('property_number', '=', rec.property_id.property_name)
            ])
            if order:
                status = order[0].order_id.rental_status
                if status in ['pickup', 'return']:
                    rec.state_id = 'مؤجرة'
                    rec.unit_state = 'مؤجرة'
                else:
                    rec.state_id = 'شاغرة'
                    rec.unit_state = 'شاغرة'

    def _get_unit_price(self):
        for rec in self:
            prices = [p.price for p in rec.rental_pricing_ids]
            units = [p.unit for p in rec.rental_pricing_ids]
            rec.unit_price = prices[0] if prices else 0
            rec.unit_price_unit = units[0] if units else ''

    def _unit_sales_count(self):
        self.unit_sales_count = self.env['sale.order.line'].search_count([
            ('product_id', '=', self.id),
            ('property_number', '=', self.property_id.property_name)])

    def unit_sales(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'ايجارات',
            'view_mode': 'form',
            'view_id': self.env.ref('sale_renting.rental_order_primary_form_view').id,
            'res_model': 'sale.order',
            'context': {
                'default_is_rental_order': True,
                'default_property_name': self.property_id.id,
                'default_unit_number': self.id,
                'default_analytic_account_id': self.analytic_account.id
            },
        }

    @api.model
    def create(self, vals_list):
        res = super(RentProduct, self).create(vals_list)
        res.ref_analytic_account = str(res.property_id.ref_analytic_account) + '-' + str(res.unit_number)
        analytic_account = self.env['account.analytic.account'].sudo().create({
            'name': res.name,
            'group_id': res.property_analytic_account_parent.id,
            'code': res.ref_analytic_account
        })
        res.analytic_account = analytic_account
        return res
