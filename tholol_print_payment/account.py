# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

from odoo.addons.tholol_print_payment.num_to_text_ar import amount_to_text_arabic


class AccountPayment(models.Model):
    _inherit = 'account.payment'


    def _convert_num_to_text(self, amount):
        return amount_to_text_arabic(abs(amount), 'SAR')