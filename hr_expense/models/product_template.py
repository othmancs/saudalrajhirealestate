# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.tools.sql import column_exists, create_column


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def default_get(self, fields):
        result = super(ProductTemplate, self).default_get(fields)
        if self.env.context.get('default_can_be_expensed'):
            result['supplier_taxes_id'] = False
        return result

    can_be_expensed = fields.Boolean(
        string="Can be Expensed",
        compute='_compute_can_be_expensed',
        store=True,
        readonly=False,
        help="Specify whether the product can be selected in an expense."
    )

    def _auto_init(self):
        # إنشاء العمود إذا لم يكن موجوداً
        if not column_exists(self.env.cr, "product_template", "can_be_expensed"):
            create_column(self.env.cr, "product_template", "can_be_expensed", "boolean")
            self.env.cr.execute("""
                UPDATE product_template
                SET can_be_expensed = false
                WHERE type NOT IN ('consu', 'service')
            """)

        # تنظيف الأعمدة الرقمية من القيم غير الصالحة
        cleanup_columns = [
            'list_price',
            'volume',
            'weight',
            'rent_unit_area',
            'service_upsell_threshold',
            'partner_latitude',
            'partner_longitude',
            'rent_unit_price'
        ]

        for col in cleanup_columns:
            # استبعاد القيم غير الرقمية تماماً
            self.env.cr.execute(f"""
                UPDATE product_template
                SET {col} = NULL
                WHERE trim({col}::text) !~ '^[-+]?[0-9]*\\.?[0-9]+$'
            """)

            # إزالة الفراغات وتحويل القيم إلى double precision
            self.env.cr.execute(f"""
                UPDATE product_template
                SET {col} = trim({col}::text)::double precision
                WHERE {col}::text LIKE ' %' OR {col}::text LIKE '% '
            """)

        return super()._auto_init()

    @api.depends('type')
    def _compute_can_be_expensed(self):
        self.filtered(lambda p: p.type not in ['consu', 'service']).update({'can_be_expensed': False})
