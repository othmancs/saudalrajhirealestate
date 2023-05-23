# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class EmployeeCustody(models.Model):
    _name = 'employee.custody'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Employee Custody'

    name = fields.Char(string='Number#', default='New')
    employee_id = fields.Many2one(
        comodel_name='hr.employee', string='Employee', default=lambda self: self.env.user.employee_id)
    employee_number = fields.Char(related='employee_id.employee_number', string='Employee Number')
    department_id = fields.Many2one(
        comodel_name='hr.department', string='Department', related="employee_id.department_id")
    job_id = fields.Many2one(comodel_name='hr.job', string='Job Title',
                             related="employee_id.job_id", )
    request_date = fields.Date(string='Request Date', default=fields.Date.today())
    receive_date = fields.Date(string='Receive Date', default=fields.Date.today())
    return_date = fields.Date(string='Return Date', default=fields.Date.today())
    request_for = fields.Char(string='Request For')
    note = fields.Text(string='Notice')
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.user.company_id.id)
    item_ids = fields.One2many(comodel_name='custody.line', inverse_name='custody_id', string='Items', tracking=True, )

    state = fields.Selection(string='Status', selection=[
        ('draft', 'Draft'), ('submit', 'Submit'),
        ('l_m_approve', 'Line Manager'), ('hrm', 'Hr'),
        ('delivered', 'Delivered'), ('returned', 'Returned')
    ], default='draft', tracking=True)
    line_manager_id = fields.Many2one('res.users', string='Line Manager')
    hr_responsible_id = fields.Many2one('res.users', string='Hr Responsible')
    delivered_by = fields.Many2one('res.users', string='Delivered By')
    returned_by = fields.Many2one('res.users', 'Returned By')
    line_manager_approval_date = fields.Date(string='Line Manager Approval Date')
    hr_approval_date = fields.Date(string='Hr Approval Date')
    delivered_date = fields.Date(string='Delivered Date')
    returned_date = fields.Date(string='Returned Date')
    manager_id = fields.Many2one('res.users', related='employee_id.parent_id.user_id', store=True)
    is_manager = fields.Boolean(compute='get_current_uid')

    @api.depends('manager_id')
    def get_current_uid(self):
        """

        :param self:
        :return:
        """
        if self.manager_id.id == self.env.user.id:
            self.is_manager = True
        else:
            self.is_manager = False

    def action_submit(self):
        self.state = 'submit'

    def action_l_m_approve(self):
        self.write({
            'line_manager_id': self.env.user.id,
            'state': 'l_m_approve',
            'line_manager_approval_date': fields.Date.today()
        })

    def action_hrm(self):
        self.write({
            'hr_responsible_id': self.env.user.id,
            'state': 'hrm',
            'hr_approval_date': fields.Date.today()
        })

    def action_delivered(self):
        item_ids = self.item_ids.filtered(lambda l: not l.rejected)
        for line in item_ids:
            line.product_id.status = 'allocate'
            if line.product_id.asset_id:
                line.product_id.asset_id.write({
                    'status': 'allocate',
                    'owner_id': self.employee_id.id,
                    'allocation_date': fields.Date.today()
                })
        self.write({
            'delivered_by': self.env.user.id,
            'state': 'delivered',
            'delivered_date': fields.Date.today()
        })

    def action_returned(self):
        self.write({
            'returned_by': self.env.user.id,
            'state': 'returned',
            'returned_date': fields.Date.today()
        })
        for line in self.item_ids.filtered(lambda l: not l.rejected):
            line.product_id.status = 'free'
            if line.product_id.asset_id:
                line.product_id.asset_id.write({'status': 'free',
                                                'allocation_date': False,
                                                'owner_id': False
                                                })

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq_date = None
            if 'request_date' in vals:
                seq_date = fields.Datetime.context_timestamp(
                    self, fields.Datetime.to_datetime(vals['request_date']))
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'custody.request', sequence_date=seq_date) or _('New')
        result = super(EmployeeCustody, self).create(vals)
        for l in result.item_ids:
            display_msg = """%s Must returned  on %s    """ % (l.product_id.name, l.return_date)
            l.custody_id.message_post(body=display_msg)
        return result

    def check_date(self):
        objs = self.env['custody.line'].search([])
        template = self.env.ref('plustech_hr_employee_custody.return_custody_mail')
        for rec in objs:
            delta = 0
            today = fields.Date.today()
            if rec.return_date:
                delta = rec.return_date - today
            if delta == 1:
                template.sudo().send_mail(rec.id, force_send=True)


class CustodyLine(models.Model):
    _name = 'custody.line'
    _description = 'Custody Lines'

    custody_id = fields.Many2one(comodel_name='employee.custody', string='')
    product_id = fields.Many2one('product.product', string='Item', readonly=False,
                                 domain="[('can_be_custody', '=', True), ('status', '=', 'free')]", ondelete='restrict')
    rejected = fields.Boolean(string='Reject')
    request_for = fields.Char(string='Request For')
    return_date = fields.Date(string='Renew Date')
    state = fields.Selection(related="custody_id.state", string='Status', store=True)
    serial = fields.Char(related='product_id.default_code', string='Serial')
    employee_id = fields.Many2one('hr.employee', related="custody_id.employee_id", string='Employee', store=True)
    request_date = fields.Date(string='Request Date', related="custody_id.request_date", store=True)
    receive_date = fields.Date(string='Receive Date', related="custody_id.receive_date", store=True)
    name = fields.Char(related="custody_id.name", string='Request No')

    def action_renew(self):
        return {
            'name': 'Renew Custody',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'renew.renew',
            'target': 'new',
        }


class Renew(models.TransientModel):
    _name = 'renew.renew'
    _description = 'Custody Renew'

    return_date = fields.Date(string='Renew Date')
    reason = fields.Char(string='Renew Reason')

    def action_submit(self):
        obj = self.env['custody.line'].browse(self.env.context.get('active_id'))
        obj.return_date = self.return_date
        display_msg = """%s Renewed to %s for : %s   """ % (obj.product_id.name, obj.return_date, self.reason)
        obj.custody_id.message_post(body=display_msg)
