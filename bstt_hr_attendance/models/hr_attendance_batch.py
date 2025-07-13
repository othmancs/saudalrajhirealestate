# -*- coding: utf-8 -*-
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from pytz import timezone, UTC, utc
from odoo.tools import format_datetime
from odoo.tools import format_time
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression

# تعريف ثابت للساعات في اليوم حسب سياسات الشركة
HOURS_PER_DAY = 8.0

# دالة لتحويل الرقم العشري إلى صيغة وقت (ساعة:دقيقة)
def float_to_time(value):
    hours = int(value)
    minutes = int(round((value - hours) * 60))
    return "%02d:%02d" % (hours, minutes)


class HrAttendanceBatch(models.Model):
    _name = 'hr.attendance.batch'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Attendance Batches'
    _order = 'check_in desc, id desc'

    name = fields.Char(required=True, readonly=True, states={'draft': [('readonly', False)]})
    attendance_ids = fields.One2many('hr.attendance.batch.line', 'attendance_batch_id', string='Attendances',
                                     readonly=True,
                                     states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'New'),
        ('verify', 'Confirmed'),
        ('close', 'Done'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft')
    check_in = fields.Date(string="Check In From", default=lambda self: date.today(), required=True)
    check_in_to = fields.Date(string="Check In To", default=lambda self: date.today(), required=True)
    worked_hours = fields.Float(string='Worked Hours')
    attendance_count = fields.Integer(compute='_compute_attendance_count')
    company_id = fields.Many2one('res.company', string='Company', readonly=True, required=True,
                                 default=lambda self: self.env.company)
    country_id = fields.Many2one(
        'res.country', string='Country',
        related='company_id.country_id', readonly=True
    )
    department_id = fields.Many2one('hr.department', string="Department")
    dept_check = fields.Boolean(string="All Departments Under this Dep.")
    category_ids = fields.Many2many('hr.employee.category', string='Tags')
    date_range = fields.Selection([
        ('today', 'Today'),
        ('yesterday', 'Yesterday')
    ], string='Attendance Date', default='today')

    def _is_hr_manager_check(self):
       if self.env.user.has_group('hr.group_hr_manager'):
           return True
       else:
           return False

    is_hr_manager = fields.Boolean(default=lambda self: self._is_hr_manager_check())

    @api.onchange('date_range')
    def onchange_date_range(self):
        for rec in self:
            if rec.date_range == 'today':
                rec.check_in = date.today()
            elif rec.date_range == 'yesterday':
                rec.check_in = date.today() - relativedelta(days=1)

    @api.onchange('check_in', 'check_out', 'worked_hours')
    def onchange_data(self):
        for rec in self:
            rec.attendance_ids = False

    def diff_dates(self):
        fmt = '%Y-%m-%d'
        check_from = self.check_in
        check_to = self.check_in_to
        d1 = datetime.strptime(str(check_from), fmt)
        d2 = datetime.strptime(str(check_to), fmt)
        date_difference = d2 - d1
        return date_difference

    @api.onchange('department_id', 'category_ids', 'check_in', 'dept_check', 'date_range')
    def onchange_department_id(self):
        for rec in self:
            if rec.check_in and (rec.department_id or rec.category_ids):
                if rec.category_ids or rec.department_id:
                    if not rec.check_in and rec.worked_hours == 0.0:
                        raise UserError(_("You must select Check IN Date and write worked hours."))

                rec.attendance_ids = False
                domain = [('contract_ids.state', 'in', ('open', 'close')), ('company_id', '=', self.env.company.id)]
                if rec.category_ids:
                    domain = expression.AND([domain, [('category_ids', 'in', self.category_ids.ids)]])
                if rec.department_id and rec.dept_check:
                    domain = expression.AND([domain, [('department_id', 'child_of', self.department_id.id)]])
                if rec.department_id and not rec.dept_check:
                    domain = expression.AND([domain, [('department_id', '=', self.department_id.id)]])
                if not self.env.user.has_group('hr_attendance.group_hr_attendance_manager'):
                    domain = expression.AND([domain, ['|', ('parent_id.user_id', '=', self.env.user.id),
                                                      ('user_id', '=', self.env.user.id)]])

                employee_ids = self.env['hr.employee'].search(domain)
                for employee in employee_ids:
                    check_in_date = rec.check_in
                    if rec.check_in_to and rec.diff_dates().days + 1 > 0:
                        for i in range(rec.diff_dates().days + 1):
                            line = self.env['hr.attendance.batch.line'].new({
                                'employee_id': employee.id,
                                'check_in_date': check_in_date,
                            })
                            line.onchange_employee_id()
                            if line.check_in:
                                rec.attendance_ids |= line
                            check_in_date = check_in_date + relativedelta(days=1)
                            i += i
                    else:
                        line = self.env['hr.attendance.batch.line'].new({
                            'employee_id': employee.id,
                            'check_in_date': check_in_date,
                        })
                        line.onchange_employee_id()
                        rec.attendance_ids |= line

    def action_validate(self):
        for rec in self:
            for line in rec.attendance_ids:
                attendance_id = self.env['hr.attendance'].create({
                    'employee_id': line.employee_id.id,
                    'check_in': line.check_in,
                    'check_out': line.check_out,
                    'notes': line.notes,
                    'batch_id': rec.id,
                })
                line.attendance_id = attendance_id.id

        self.write({'state': 'close'})

    def action_send(self):
        self.write({'state': 'verify'})

    def action_draft(self):
        self.write({'state': 'draft'})
