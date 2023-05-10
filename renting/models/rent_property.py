# -*- coding: utf-8 -*-

from odoo import models, fields, api


class RentPropertyModel(models.Model):
    _name = 'rent.property'
    _rec_name = 'property_name'
    _inherit = ['mail.thread']

    property_name = fields.Char(string='Property Name')
    property_number = fields.Char(string='Property Number')
    property_address_street = fields.Char(string='Street Name')
    property_address_area = fields.Many2one('operating.unit', string='الفرع ', required=True)
    property_address_build = fields.Many2one('rent.property.build', string='المجمع ')
    property_address_city = fields.Many2one('rent.property.city', string='City')
    country = fields.Many2one('res.country', string='الدولة')
    property_address_Postal_code = fields.Char(string=' العنوان الوطني')
    property_extra_number = fields.Char(string='Extra Number')
    unit_ids = fields.One2many('product.template', 'property_id', string='Unit ID',
                               copy=True)  # Related field to products

    company_id = fields.Many2one('res.company', string='company', related='property_address_area.company_id')
    # General Info Tab Fields
    property_construction_date = fields.Date(string='Construction Date')
    rent_config_property_type_id = fields.Many2one('rent.config.property.types', string='Property Type',
                                                   copy=True)  # Related field to menu item "Property Types"
    rent_config_property_purpose_id = fields.Many2one('rent.config.property.purposes', string='Property Purpose',
                                                      copy=True)  # Related field to menu item "Property Purposes"
    property_land_contract = fields.Char(string='رقم الصك')
    property_land_contract_date = fields.Char(string='تاريخ الصك')
    property_land_contract_image = fields.Binary(string='صورة الصك')
    property_land_contract_electronic = fields.Boolean(string='صك الكتروني')
    property_gas = fields.Char(string='Gas Meter Number')
    property_electricity = fields.Char(string='Electricity Meter Number')
    property_water = fields.Char(string='Water Meter Number')
    property_has_elevator = fields.Boolean(string='Elevator/s')
    property_elevators = fields.Char(string='Number of Elevators')
    elevator_contract = fields.Binary(string='Elevator Contract')
    property_has_parking = fields.Boolean(string='Car Parking')
    property_garages = fields.Char(string='Number of Parking Garages')
    property_units_number = fields.Char(string='Number of Units')
    property_floors_number = fields.Char(string='Number of Floors')

    # Property Units Tab Fields ~> is Inherited from "rent_product_inherit.py"

    # Security Tab Fields
    security_tab = fields.One2many('security.rent.property', 'property')

    # Buttons Fields Counted
    elevator_maintenance_count = fields.Integer(string='Total Maintenance', compute='_get_count', readonly=True)
    property_maintenance_count = fields.Integer(string='Total Property Maintenance', compute='_get_count',
                                                readonly=True)

    # التصاريخ
    national_permit_number = fields.Char('رقم التصريح')
    national_permit_image = fields.Many2many('ir.attachment', 'class_ir_attachments_rel', 'class_id', 'attachment_id',
                                             string='صورة التصريح')
    national_permit_shop_in = fields.Date('تاريخ اصدار تصريح المحل')
    national_permit_shop_out = fields.Date('تاريخ انتهاء تصريح المحل')
    national_permit_build = fields.Date('تاريخ اصدار شهادة اتمام البناء')

    defense_permit_number = fields.Char('رقم التصريح')
    defense_permit_image = fields.Many2many('ir.attachment', 'class_ir_attachments_rel', 'class_id', 'attachment_id',
                                            string='صورة التصريح')
    defense_permit_in = fields.Date('تاريخ اصدار التصريح')
    defense_permit_out = fields.Date('تاريخ انتهاء التصريح')

    tour_permit_number = fields.Char('رقم التصريح')
    tour_permit_image = fields.Many2many('ir.attachment', 'class_ir_attachments_rel', 'class_id', 'attachment_id',
                                         string='صورة التصريح')
    tour_permit_in = fields.Date('تاريخ اصدار التصريح')
    tour_permit_out = fields.Date('تاريخ انتهاء التصريح')

    pepole_permit_number = fields.Char('رقم التصريح')
    pepole_permit_image = fields.Many2many('ir.attachment', 'class_ir_attachments_rel', 'class_id', 'attachment_id',
                                           string='صورة التصريح')
    pepole_permit_in = fields.Date('تاريخ اصدار التصريح')
    pepole_permit_out = fields.Date('تاريخ انتهاء التصريح')

    trade_permit_number = fields.Char('رقم التصريح')
    trade_permit_image = fields.Many2many('ir.attachment', 'class_ir_attachments_rel', 'class_id', 'attachment_id',
                                          string='صورة التصريح')
    trade_permit_in = fields.Date('تاريخ اصدار التصريح')
    trade_permit_out = fields.Date('تاريخ انتهاء التصريح')

    maintain_contract = fields.Boolean('عقد الصيانة')
    maintain_company = fields.Char('شركة الصيانة')
    maintain_contract_image = fields.Binary('عقد الصيانة')

    security_contract = fields.Boolean('عقد الأمن')
    security_company = fields.Char('شركة الأمن')
    security_contract_image = fields.Binary('عقد الأمن')

    cleaning_contract = fields.Boolean('عقد النظافة')
    cleaning_company = fields.Char('شركة النظافة')
    cleaning_contract_image = fields.Binary('عقد النظافة')
    analytic_account = fields.Many2one('account.analytic.account', string='الحساب التحليلي', readonly=True)
    ref_analytic_account = fields.Integer(string='رقم اشارة الحساب التحليلي', readonly=True)

    busy_units = fields.Float(compute='_get_busy', string='الوحدات المؤجرة')
    free_units = fields.Float(compute='_get_free', string='الوحدات الشاغرة')
    busy_ids = fields.Float()
    free_ids = fields.Float()

    def get_ref_analytic_account(self):
        ref = ''
        if self.property_address_area.id:
            ref += str(self.property_address_area.ref_analytic_account)
        if self.property_address_build.id:
            ref += str(self.property_address_build.ref_analytic_account)
        if not self.property_address_build.id:
            ref += '0'
        ref_analytic_account = ref + str(self.property_number)
        return ref_analytic_account

    @api.model
    def create(self, values):
        # your logic goes here
        ref = ''
        res = super(RentPropertyModel, self).create(values)
        exist_area = self.env['account.analytic.group']
        search_group = exist_area.sudo().search([('name', '=', res.property_address_area.name)])

        # if res.country.id:
        #     ref += str(res.country.ref_analytic_account)
        # if res.property_address_city.id:
        #     ref += str(res.property_address_city.ref_analytic_account)
        # if res.property_address_area.id:
        #     ref += str(res.property_address_area.ref_analytic_account)
        # if res.property_address_build.id:
        #     ref += str(res.property_address_build.ref_analytic_account)
        # if not res.property_address_build.id:
        #     ref += '0'
        res.ref_analytic_account = res.get_ref_analytic_account()

        if search_group:
            area_group_analytic_account = search_group[-1]
        else:
            area_group_analytic_account = exist_area.sudo().create({'name': res.property_address_area.name, })

        if res.property_address_build.id:
            search_build = exist_area.sudo().search([('name', '=', res.property_address_build.name)])
            if not search_build.id:
                build_group_analytic_account = exist_area.sudo().create(
                    {'name': res.property_address_build.name, 'parent_id': area_group_analytic_account.id})
            else:
                build_group_analytic_account = search_build

            group_analytic_account = self.env['account.analytic.group'].sudo().create(
                {'name': res.property_name, 'parent_id': build_group_analytic_account.id})
            analytic_account = self.env['account.analytic.account'].sudo().create(
                {'name': res.property_name, 'group_id': group_analytic_account.id, 'code': res.ref_analytic_account})
            res.analytic_account = analytic_account
        else:
            group_analytic_account = self.env['account.analytic.group'].sudo().create(
                {'name': res.property_name, 'parent_id': area_group_analytic_account.id})
            analytic_account = self.env['account.analytic.account'].sudo().create(
                {'name': res.property_name, 'group_id': group_analytic_account.id, 'code': res.ref_analytic_account})
            res.analytic_account = analytic_account
        return res

    def _get_busy(self):
        for rec in self:
            no_units = 0
            for unit in rec.unit_ids:
                if unit.state_id == 'مؤجرة':
                    no_units += 1
            rec.busy_units = no_units
            rec.busy_ids = no_units

    def _get_free(self):
        for rec in self:
            no_units = 0
            for unit in rec.unit_ids:
                if unit.state_id == 'شاغرة':
                    no_units += 1
            rec.free_units = no_units
            rec.free_ids = no_units

    def _get_count(self):
        # self.elevator_maintenance_count = self.env['rent.property.elevator'].search_count(
        #     [('property_id', '=', self.id)])
        self.property_maintenance_count = self.env['rent.property.maintain'].search_count(
            [('property', '=', self.property_name)])

    # # For Elevator Maintenance Button in property_form in "vw_rent_property.xml"
    # def get_elevator_maintenance(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Properties - Maintenance',
    #         'view_mode': 'tree,form',
    #         'res_model': 'rent.property.elevator',
    #         'domain': [('property_id', '=', self.id)],
    #         'context': {'default_property_id': self.id},
    #     }

    # For Property Maintenance Button in property_form in "vw_rent_property.xml"
    def get_property_maintenance(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'صيانات',
            'view_mode': 'tree,form',
            # 'view_id': self.env.ref('account.view_move_form').id,
            'res_model': 'rent.property.maintain',
            'domain': [('property', '=', self.id)],
            'context': {'default_move_type': 'in_invoice', 'default_journal_id': 2,
                        'default_property': self.id,
                        'default_analytic_account': self.analytic_account.id},
        }


class RentPropertysecurity(models.Model):
    _name = 'security.rent.property'

    security_name = fields.Char(string='اسم  حارس العقار')
    security_salary = fields.Char(string='الراتب')
    security_address = fields.Char(string='العنوان')
    security_national_id = fields.Char(string='رقم الهوية')
    security_id_image = fields.Binary(string='بطاقة الهوية')
    property = fields.Many2one('rent.property')


class RentPropertycity(models.Model):
    _name = 'rent.property.state'
    _rec_name = 'name'

    name = fields.Char('المنطقة')
    property_address_city = fields.Many2one('rent.property.city', string='City')
    ref_analytic_account = fields.Integer(string='رقم اشارة الحساب التحليلي')


class RentPropertybuilding(models.Model):
    _name = 'rent.property.build'
    _rec_name = 'name'

    name = fields.Char('المجمع')
    property_address_area = fields.Many2one('rent.property.state', string='الفرع ')
    property_address_city = fields.Many2one('rent.property.city', string='City')
    ref_analytic_account = fields.Integer(string='رقم اشارة الحساب التحليلي')
    company_id = fields.Many2one('res.company', string='company', readonly=True, default=lambda self: self.env.company)



class RentPropertystate(models.Model):
    _name = 'rent.property.city'
    _rec_name = 'name'

    name = fields.Char('الدولة')
    ref_analytic_account = fields.Integer(string='رقم اشارة الحساب التحليلي', required=True)


class RentCountrystate(models.Model):
    _inherit = 'res.country'

    ref_analytic_account = fields.Integer(string='رقم اشارة الحساب التحليلي')


class RentPropertymain(models.Model):
    _name = 'rent.property.maintain'
    _rec_name = 'maintain_name'

    maintain_name = fields.Char(string='نوع الصيانة')
    maintain_desc = fields.Text(string='وصف الصيانة')
    maintain_provider = fields.Char(string='مسؤول الصيانة')
    maintain_cost = fields.Char(string='مبلغ الصيانة')
    maintain_date_from = fields.Date(string='تاريخ بداية الصيانة')
    maintain_date_to = fields.Date(string='تاريخ انتهاء الصيانة')
    property = fields.Many2one('rent.property', string='العقار')
    apartment = fields.Many2one('product.template', string='الوحدة', domain="[('property_id', '=', property)]")
    state = fields.Selection(
        [('draft', 'جديد'), ('confirm', 'تم الطلب'), ('invoice', 'مفوتر'), ('start', 'تحت الصبانة'),
         ('done', 'تمت الصبانة')], string='State',
        default='draft')

    def set_confirm(self):
        self.write({'state': 'confirm'})

    def set_start(self):
        self.write({'state': 'start'})

    def set_finish(self):
        self.write({'state': 'done'})

    def set_invoice(self):
        # self.write({'state': 'start'})
        return {
            'type': 'ir.actions.act_window',
            'name': 'القيود',
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_model': 'account.move',
            # 'domain': [('property', '=', self.id)],
            'context': {'default_move_type': 'entry', 'default_journal_id': 3, 'default_is_maintain': True,
                        'default_property_name': self.property.id, 'default_unit_number': self.apartment.id, },
        }
