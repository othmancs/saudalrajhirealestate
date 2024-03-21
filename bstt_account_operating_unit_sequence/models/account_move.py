# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date
_logger = logging.getLogger(__name__)
from odoo import api, fields, models, Command, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

from datetime import date, timedelta

import re
import warnings



class AccountMove(models.Model):
    _inherit = "account.move"

    seq_created = fields.Boolean("Sequence Created")
    last_seq = fields.Char("Last Sequence")

    # @api.onchange('journal_id')
    # def change_journals(self):
    #     for rec in self:
    #         rec.name = "/"
    #         self.create_names()
    def create_names(self):
        for rec in self:
            if rec.seq_created != True:
                if rec.operating_unit_id.journal_sequence_id and rec.move_type == 'entry':
                    branch = str(rec.operating_unit_id.code)
                    type = str(rec.journal_id.code)
                    journal = str(rec.journal_id.name).split()[0]
                    # year = str(date.today().year)
                    year =  str(rec.date.year)
                    if rec.operating_unit_id.journal_sequence_id.use_date_range == True:
                        sub_seq_line = rec.operating_unit_id.journal_sequence_id.date_range_ids.filtered(lambda l: l.date_from<= rec.date and l.date_to >= rec.date)
                        next = str(sub_seq_line.number_next_actual)
                        sub_seq_line.number_next_actual += 1
                    else:
                        next = str(rec.operating_unit_id.journal_sequence_id.number_next_actual)
                    rec.operating_unit_id.journal_sequence_id.number_next_actual += 1
                    seq_name = branch + '/' + type + '/' + journal + '/' + year + '/' + next
                    rec.name = seq_name
                    rec.last_seq = seq_name
                    rec.seq_created = True
                if rec.operating_unit_id.invoice_sequence_id and rec.move_type != 'entry':
                    rec.name = ''
                    branch = str(rec.operating_unit_id.code)
                    type = str(rec.journal_id.code)
                    journal = str(rec.journal_id.name).split()[0]
                    year = str(date.today().year)
                    next = str(rec.operating_unit_id.invoice_sequence_id.number_next_actual)
                    rec.operating_unit_id.invoice_sequence_id.number_next_actual += 1
                    seq_name = branch + '/' + type + '/' + journal + '/' + year + '/' + next
                    rec.name= seq_name
                    rec.last_seq= seq_name
                    rec.seq_created = True
    def _post(self, soft=True):
        # This code for solve problem creating duplicate names
        # for rec in self:
        #     if rec.state == 'draft' and rec.name and rec.name != '/':
        #         move = rec.env["account.move"].search_count([("id", "!=", rec.id), ("name", "=", rec.name)])
        #         if move > 0:
        #             rec.name = False
        #############################################

        result = super(AccountMove, self)._post()
        for rec in self:
            pass
            # if rec.operating_unit_id.journal_sequence_id and rec.move_type == 'entry':
            #     seq = self.env['ir.sequence'].browse(rec.operating_unit_id.journal_sequence_id.id).next_by_id()
            #     rec.name = seq
            # if rec.operating_unit_id.invoice_sequence_id and rec.move_type != 'entry':
            #     print("ppppppppppppppppppppppp ",(self.env['ir.sequence'].browse(rec.operating_unit_id.invoice_sequence_id.id).next_by_id()))
            #     seq = self.env['ir.sequence'].browse(rec.operating_unit_id.invoice_sequence_id.id).next_by_id()
            #     rec.name = seq
            #ToDo: Abdulrhman Code
            # rec.create_names()
            # else:
            #     raise UserError(_("لابد من انشاء مسلسل للفواتير والقيود في اعدادات الفروع"))
        return result

    def button_cancel(self):
        res = super(AccountMove, self).button_cancel()
        for rec in self:
            rec.name = rec.last_seq
        return res
    #def action_review(self):
        #res = super(AccountMove, self).action_review()
        #for rec in self:
            #print("reviiiiiiiiiiiiiiiiiiiew",rec.name)
         #   rec.name = rec.last_seq
            #print("reviiiiiiiiiiiiiiiiiiiew",rec.name)
        #return res
    #def button_draft(self):
     #   res = super(AccountMove, self).button_draft()
      #  for rec in self:
       #     rec.name = rec.last_seq
        #return res

    # @api.onchange('journal_id')
    # def _onchange_journal(self):
    #     if self.journal_id and self.journal_id.currency_id:
    #         new_currency = self.journal_id.currency_id
    #         if new_currency != self.currency_id:
    #             self.currency_id = new_currency
    #             self._onchange_currency()
    #     if self.state == 'draft' and self._get_last_sequence(lock=False) and self.name and self.name != '/':
    #         self.name = '/'
