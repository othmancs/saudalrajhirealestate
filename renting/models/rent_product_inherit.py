# -*- coding: utf-8 -*-

from odoo import api, models, fields


class RentProduct(models.Model):
    _inherit = 'product.template'

    unit_number = fields.Char(string='رقم الوحدة')
    unit_area = fields.Float(string='مساحة الوحدة')
    unit_floor_number = fields.Char(string='رقم الطابق')
    unit_rooms_number = fields.Char(string='عدد الغرف')
    unit_state = fields.Char(compute='_get_state', string='الحالة')

    rent_unit_area = fields.Float(string='المساحة')

    # unit_contain_two_scales = fields.Boolean(string='Contain Two Scales')
    # unit_furniture = fields.Boolean(string='Furniture?')
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

    unit_construction_date = fields.Date(string='تاريخ الانشاء')

    rent_config_unit_overlook_id = fields.Many2one('rent.config.unit.overlooks', string='Unit Overlooking',
                                                   copy=True)  # Related field to menu item "Unit Views"
    rent_config_unit_type_id = fields.Many2one('rent.config.unit.types', string='Unit type',
                                               copy=True)  # Related field to menu item "Unit Types"
    rent_config_unit_purpose_id = fields.Many2one('rent.config.unit.purposes', string='Unit Purpose',
                                                  copy=True)  # Related field to menu item "Unit Purpose"
    rent_config_unit_finish_id = fields.Many2one('rent.config.unit.finishes', string='Unit Finish',
                                                 copy=True)  # Related field to menu item "Unit Finishes"

    property_id = fields.Many2one('rent.property', string='عمارة', copy=True)  # Related field to Properties
    property_address_build = fields.Many2one('rent.property.build', string='المجمع',
                                             related='property_id.property_address_build', store=True, index=True)
    property_address_city = fields.Many2one('rent.property.city', string='المدينة',
                                            related='property_id.property_address_city', store=True)
    country = fields.Many2one('res.country', string='الدولة', related='property_id.country', store=True, index=True)
    operating_unit = fields.Many2many('operating.unit', string='الفرع ')

    entry_number = fields.Char('عدد المداخل')
    entry_overlook = fields.Char('المداخل تطل علي')

    unit_gas = fields.Char(string='رقم عداد الغاز')
    unit_electricity = fields.Char(string='رقم عداد الكهرباء')
    unit_water = fields.Char(string='رقم عداد المياه')

    # unit_maintenance_count = fields.Integer(string='Total Maintenance', compute='_get_count', readonly=True)
    unit_expenses_count = fields.Integer(string='Total Expenses', compute='_unit_expenses_count', readonly=True)
    unit_sales_count = fields.Integer(string='Total Sales', compute='_unit_sales_count', readonly=True)
    unit_price = fields.Float(string='قيمة الوحدة', compute='_get_unit_price')
    unit_price_unit = fields.Char(string='مدة تأجير الوحدة')
    state_id = fields.Char(string="الحالة", store=True)
    analytic_account = fields.Many2one('account.analytic.account', string='الحساب التحليلي', readonly=True)
    ref_analytic_account = fields.Char(string='رقم اشارة الحساب التحليلي', readonly=True)
    property_analytic_account = fields.Many2one('account.analytic.account', string='الحساب التحليلي للعقار',
                                                related='property_id.analytic_account')
    property_analytic_account_parent = fields.Many2one('account.analytic.group',
                                                       related='property_id.analytic_account.group_id')

    @api.model_create_multi
    def create(self, vals_list):

        res = super(RentProduct, self).create(vals_list)
        res.ref_analytic_account = str(res.property_id.ref_analytic_account) + '-' + str(res.unit_number)
        analytic_account = self.env['account.analytic.account'].sudo().create(
            {'name': res.name, 'group_id': res.property_analytic_account_parent.id, 'code': res.ref_analytic_account})
        res.analytic_account = analytic_account
        return res

    def _get_unit_price(self):
        for rec in self:
            prices = []
            units = []
            for price in rec.rental_pricing_ids:
                prices.append(price.price)
                units.append(price.unit)
            if len(prices) > 0:
                rec.unit_price = prices[0]
            if len(units) > 0:
                rec.unit_price_unit = units[0]
            else:
                rec.unit_price = 0
                rec.unit_price_unit = ''

    partner_id = fields.Many2one('res.partner', compute="get_sale_data", string='العميل')
    amount_paid = fields.Float(compute="get_sale_data", string='المبلغ المدفوع')
    amount_due = fields.Float(compute="get_sale_data", string='المبلغ المستحق')
    contract_admin_fees = fields.Float(compute="get_sale_data", string='رسوم إدارية')
    contract_service_fees = fields.Float(compute="get_sale_data", string='رسوم الخدمات')
    insurance_value = fields.Float(compute="get_sale_data", string='قيمة التأمين')
    fromdate = fields.Date(compute="get_sale_data", string='تاريخ بداية العقد')
    todate = fields.Date(compute="get_sale_data", string='تاريخ نهاية العقد')
    last_sale_id = fields.Many2one('sale.order', string='رقم العقد', compute="get_sale_data", store=True)
    operating_unit_id = fields.Many2one('operating.unit', string='الفرع ')
    contract_total = fields.Float(compute="get_sale_data", string='قيمة العقد')
    contract_service_sub_fees = fields.Float(string=' رسوم الخدمات الخاضعة ')
    contract_admin_sub_fees = fields.Float(string='رسوم ادارية خاضعة')
    def get_sale_data(self):
        for rec in self:
            order_line_id = rec.env['sale.order.line'].sudo().search([('product_id', '=', rec.id), ('state','=','occupied')],limit=1, order='id desc')
            rec.partner_id = order_line_id.order_id.partner_id.id if order_line_id else False
            rec.last_sale_id = order_line_id.order_id.id if order_line_id else False
            rec.contract_admin_fees = order_line_id.contract_admin_fees if order_line_id else False
            rec.insurance_value = order_line_id.insurance_value if order_line_id else False
            rec.contract_service_fees = order_line_id.contract_service_fees if order_line_id else False
            rec.fromdate = order_line_id.order_id.fromdate if order_line_id else False
            rec.operating_unit_id = order_line_id.order_id.operating_unit_id.id if order_line_id else False
            rec.todate = order_line_id.order_id.todate if order_line_id else False

            rec.amount_paid = (sum(ll.price_subtotal for ll in order_line_id.order_id.invoice_ids.invoice_line_ids.filtered(lambda line: line.move_id.payment_state == 'paid' and line.product_id == rec.product_variant_id))) if order_line_id else 0
            rec.contract_total = order_line_id.order_id.amount_total
            rec.contract_service_sub_fees = order_line_id.contract_service_sub_fees
            rec.contract_admin_sub_fees = order_line_id.contract_admin_sub_fees

            rec.amount_due = (sum(order_line_id.order_id.order_line[0].price_unit / ll.sale_order_id.invoice_number for ll in
                                 order_line_id.order_id.order_contract_invoice.filtered(lambda line: line.status == 'uninvoiced')
                                 )if order_line_id.order_id.order_line else 0.0) if order_line_id else 0.0

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super(RentProduct, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby,
                                                 lazy=lazy)
        print(fields)
        if 'amount_paid' in fields:
            for line in res:
                if '__domain' in line:
                    lines = self.search(line['__domain'])
                    total_amount_paid = 0.0
                    for record in lines:
                        total_amount_paid += record.amount_paid
                    line['amount_paid'] = total_amount_paid
        if 'amount_due' in fields:
            for line in res:
                if '__domain' in line:
                    lines = self.search(line['__domain'])
                    total_amount_due = 0.0
                    for record in lines:
                        total_amount_due += record.amount_due
                    line['amount_due'] = total_amount_due
        if 'contract_admin_fees' in fields:
            for line in res:
                if '__domain' in line:
                    lines = self.search(line['__domain'])
                    total_contract_admin_fees = 0.0
                    for record in lines:
                        total_contract_admin_fees += record.contract_admin_fees
                    line['contract_admin_fees'] = total_contract_admin_fees
        if 'contract_service_fees' in fields:
            for line in res:
                if '__domain' in line:
                    lines = self.search(line['__domain'])
                    total_contract_service_fees = 0.0
                    for record in lines:
                        total_contract_service_fees += record.contract_service_fees
                    line['contract_service_fees'] = total_contract_service_fees
        if 'insurance_value' in fields:
            for line in res:
                if '__domain' in line:
                    lines = self.search(line['__domain'])
                    total_insurance_value = 0.0
                    for record in lines:
                        total_insurance_value += record.insurance_value
                    line['insurance_value'] = total_insurance_value
        return res
    
    @api.depends('unit_state','state_id')
    def _get_state(self):
        for rec in self:
            rec.unit_state = 'شاغرة'
            rec.state_id = 'شاغرة'
            maintenance_id = rec.env['maintenance.request'].sudo().search([
                ('property_id.product_tmpl_id', '=', rec.id),
                ('state', 'in',('confirm','ongoing'))
            ])
            if maintenance_id :
                rec.state_id = 'تحت الصيانة'
                rec.unit_state = 'تحت الصيانة'
                return
            order = rec.env['sale.order.line'].sudo().search([
                ('product_id', '=', rec.id),
                ('property_number', '=', rec.property_id.property_name)
            ])
            if order:
                if order[0].order_id.rental_status == 'pickup':
                    rec.state_id = 'مؤجرة'
                    rec.unit_state = 'مؤجرة'
                elif order[0].order_id.rental_status == 'return':
                    rec.state_id = 'مؤجرة'
                    rec.unit_state = 'مؤجرة'
                elif order[0].order_id.rental_status == 'returned':
                    rec.state_id = 'شاغرة'
                    rec.unit_state = 'شاغرة'
                elif order[0].order_id.rental_status == 'cancel':
                    rec.state_id = 'شاغرة'
                    rec.unit_state = 'شاغرة'
            else:
                rec.state_id = 'شاغرة'
                rec.unit_state = 'شاغرة'

    # def _get_count(self):
    #     self.unit_maintenance_count = self.env['account.move'].search_count(
    #         [('unit_number', '=', self.id), ('property_name', '=', self.property_id.property_name),
    #          ('move_type', '=', 'in_invoice')])

    # For Unit Maintenance Button in rent_product_inherit_form in "vw_rent_product_inherit.xml"
    def get_unit_maintenance(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'صيانات',
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_model': 'account.move',
            'context': {'default_move_type': 'in_invoice', 'default_journal_id': 2,
                        'default_property_name': self.property_id.id,
                        'default_unit_number': self.id, 'default_analytic_account': self.analytic_account.id},
        }

    def _unit_sales_count(self):
        self.unit_sales_count = self.env['sale.order.line'].search_count([
            ('product_id', '=', self.id),
            ('property_number', '=', self.property_id.property_name)])

    # For Unit Maintenance Button in rent_product_inherit_form in "vw_rent_product_inherit.xml"
    def unit_sales(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'ايجارات',
            'view_mode': 'form',
            'view_id': self.env.ref('sale_renting.rental_order_primary_form_view').id,
            'res_model': 'sale.order',
            'context': {'default_is_rental_order': True, 'default_property_name': self.property_id.id,
                        'default_unit_number': self.id, 'default_analytic_account_id': self.analytic_account.id},
        }
