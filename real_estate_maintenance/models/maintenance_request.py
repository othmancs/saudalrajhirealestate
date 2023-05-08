from odoo import fields, models, api, _
from odoo.exceptions import UserError


class MaintenanceRequest(models.Model):
    _name = 'maintenance.request'
    _inherit = ['portal.mixin', 'mail.thread.cc', 'mail.thread', 'mail.activity.mixin', 'rating.mixin']
    _mail_post_access = 'read'
    _description = 'Property Maintenance Request'

    @api.model
    def _default_operating_unit(self):
        return self.env.user.default_operating_unit_id

    MAINTENANCE_REQUEST_STATES = [('new', 'New'), ('confirm', 'Confirmed'), ('ongoing', 'In Progress'),
                                  ('closed', 'Closed'), ('refused', 'Refused')]
    INVOICING_STATES = [('on-company', 'On The Company'), ('on-partner', 'On The Requester')]
    name = fields.Char()
    maintenance_responsible_id = fields.Many2one("hr.employee", "Maintenance Responsible")
    property_id = fields.Many2one("product.product", string="Property")
    requester_id = fields.Many2one("res.partner")
    maintenance_request_expense_line_ids = fields.One2many("maintenance.request.expense", "maintenance_request_id")
    maintenance_request_product_line_ids = fields.One2many("maintenance.request.product", "maintenance_request_id")
    request_date = fields.Date(string="Request Date", default=fields.Date.today())
    visit_date = fields.Date(string="Visit Date")
    issue_type = fields.Many2one("maintenance.issue.type", "Issue Type")
    issue_description = fields.Text("Issue Description")
    refuse_reason = fields.Text("Refuse Reason")
    invoice_status = fields.Selection(INVOICING_STATES, "Invoicing Status")
    attachment_ids = fields.One2many('ir.attachment', compute='_compute_attachment_ids', string="Main Attachments",
                                     help="Attachments that don't come from a message.")
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company)
    account_move_ids = fields.One2many("account.move", "maintenance_request_id")
    customer_invoice_id = fields.Many2one("account.move")
    stock_picking_ids = fields.One2many("stock.picking", "maintenance_request_id")
    stock_pickings_count = fields.Integer("Stock Pickings Count",
                                          compute="_compute_stock_pickings_count")
    account_moves_count = fields.Integer("Account Moves Count",
                                         compute="_compute_account_moves_count")
    state = fields.Selection(MAINTENANCE_REQUEST_STATES, "Status", default="new")
    active = fields.Boolean(default=True)
    purchase_requisition_ids = fields.One2many("stock.request", "maintenance_request_id")
    purchase_requisition_count = fields.Integer("Purchase Requisition Count",
                                                compute="_compute_purchase_requisition_count")
    operating_unit_id = fields.Many2one(
        comodel_name='operating.unit',
        string='Operating Unit',
        default=_default_operating_unit,
        readonly=True,
        states={'draft': [('readonly', False)],
                'sent': [('readonly', False)]}
    )

    property_rent_id = fields.Many2one(
        comodel_name='rent.property',
        string='Property',
        readonly=True,
    )

    def action_view_stock_pickings(self):
        action = self.env['ir.actions.act_window']._for_xml_id('stock.action_picking_tree_all')
        action['domain'] = [('maintenance_request_id', '=', self.id)]
        return action

    def _compute_stock_pickings_count(self):
        for rec in self:
            rec.stock_pickings_count = len(rec.stock_picking_ids)

    def _compute_purchase_requisition_count(self):
        for rec in self:
            rec.purchase_requisition_count = len(rec.purchase_requisition_ids)

    def action_view_purchase_requisition(self):
        action = self.env['ir.actions.act_window']._for_xml_id('stock_request.action_request_quantities_form')
        action['domain'] = [('maintenance_request_id', '=', self.id)]
        return action

    def _compute_account_moves_count(self):
        for rec in self:
            rec.account_moves_count = len(rec.account_move_ids)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].sudo().get('sequence.maintenance.request')
        if 'issue_type' in vals:
            vals.update({'invoice_status':
                             self.env["maintenance.issue.type"].browse(vals['issue_type']).invoice_status})
        res = super(MaintenanceRequest, self).create(vals)
        res._send_notification_email()
        return res

    def _send_notification_email(self):
        for rec in self.company_id.maintenance_request_to_notify_user_id:
            if rec.email:
                mail_content = " Hello " + rec.name + \
                               " <br/> " + "<br/> " + \
                               " A new Maintenance Request Has Been Submitted. Reference (" + rec.name + ")" + \
                               " <br/> " + \
                               " Operating Unit: " + self.operating_unit_id.name + \
                               " <br/> " + \
                               " Property: " + self.property_rent_id.property_name + \
                               " <br/> " + \
                               " Unit: " + self.property_id.name + \
                               " <br/> " + \
                               " <br/> " + \
                               " Thank you,"

                self.env['mail.mail'].create({
                    'subject': _('Maintenance Request -  (Ref %s)') % (self.name),
                    'author_id': self.env.user.partner_id.id,
                    'body_html': mail_content,
                    'email_to': rec.email,
                }).send()

    def _compute_attachment_ids(self):
        for maintenance_request in self:
            attachment_ids = self.env['ir.attachment'].sudo().search([('res_id', '=', maintenance_request.id),
                                                                      ('res_model', '=', 'maintenance.request')]).ids
            message_attachment_ids = maintenance_request.mapped('message_ids.attachment_ids').ids
            maintenance_request.attachment_ids = [(6, 0, list(set(attachment_ids) - set(message_attachment_ids)))]

    def action_confirm(self):
        ctx = self.env.context
        return {
            'type': 'ir.actions.act_window',
            'name': _('Schedule Maintenance'),
            'res_model': 'wiz.maintenance.request.assign',
            'target': 'new',
            'view_mode': 'form',
            'context': ctx
        }

    def action_create_pr(self):
        for record in self:
            if len(record.maintenance_request_product_line_ids) == 0:
                raise UserError(_("Please add consumed products in order to create purchase requisition"))

            pr_obj = self.env['stock.request']
            lines = []
            pr_vals = {
                'user_id': record.maintenance_responsible_id.user_id.id or self.env.user.id,
                'maintenance_request_id': self.id,

            }
            for line in record.maintenance_request_product_line_ids:
                lines.append((0, 0, {'product_id': line.product_id.id,
                                     'request_qty': line.quantity}))
            pr_vals['lines'] = lines
            pr_obj.with_context(maintenance=True).create(pr_vals)

    def action_ongoing(self):
        self.write({"state": "ongoing"})

    def action_close(self):
        self.create_bills()
        # self.action_create_picking_new()
        self.write({"state": "closed"})

    def action_refuse(self):
        ctx = self.env.context
        return {
            'type': 'ir.actions.act_window',
            'name': _('Schedule Maintenance'),
            'res_model': 'wiz.maintenance.request.refuse',
            'target': 'new',
            'view_mode': 'form',
            'context': ctx
        }

    def create_bills(self):
        bill_vals = self._prepare_bill()
        for partner in self.maintenance_request_expense_line_ids.mapped('partner_id'):
            bill_vals.update({"partner_id": partner.id})
            bill_lines = []
            for line in self.maintenance_request_expense_line_ids.filtered(lambda exl: exl.partner_id.id == partner.id):
                bill_lines.append([0, 0, line._prepare_invoice_line()])
            bill_vals.update({"invoice_line_ids": bill_lines})
            self.env["account.move"].create(bill_vals)

    def get_delivery_picking_type(self):
        self.ensure_one()
        delivery_operation = self.env['stock.picking.type'].search([('code', '=', 'outgoing')], limit=1)

        return delivery_operation

    def get_picking_vals(self, location_src_id):
        self.ensure_one()
        picking_type = self.get_delivery_picking_type()
        if not picking_type:
            raise UserError(_("No picking type found!"))

        picking_vals = {
            'picking_type_id': picking_type.id,
            'maintenance_request_id': self.id,
            'partner_id': self.requester_id.id,
            'origin': self.name,
            'move_type': "one",
            'location_id': location_src_id.id,
            'location_dest_id': picking_type.default_location_dest_id.id or
                                self.env.ref("stock.stock_location_customers").id,
        }
        return picking_vals

    def action_create_picking_new(self):
        for rec in self:
            location_ids = rec.maintenance_request_product_line_ids.mapped('location_id')
            for location_src_id in location_ids:
                location_lines = rec.maintenance_request_product_line_ids.filtered(
                    lambda pl: pl.location_id.id == location_src_id.id)
                if len(location_lines) > 0:
                    picking_vals = rec.get_picking_vals(location_src_id)
                    picking = self.env["stock.picking"].create(picking_vals)
                    pc_group = rec._get_procurement_group()
                    stock_move_obj = self.env['stock.move']
                    for line in rec.maintenance_request_product_line_ids.filtered(
                            lambda pl: pl.location_id.id == location_src_id.id):
                        move_vals = line.get_move_vals(picking, pc_group)
                        move_vals.update({
                            'location_id': picking.location_id.id,
                            'location_dest_id': picking.location_dest_id.id,
                        })
                        stock_move_obj.with_context(maintenance=True).create(move_vals)
                    picking.action_confirm()
                    picking.action_assign()

    @api.model
    def _prepare_procurement_group(self):
        return {'name': self.name}

    @api.model
    def _get_procurement_group(self):
        pc_groups = self.env['procurement.group'].search([('name', '=', self.name)])
        if pc_groups:
            pc_group = pc_groups[0]
        else:
            pc_vals = self._prepare_procurement_group()
            pc_group = self.env['procurement.group'].create(pc_vals)
        return pc_group or False

    def _prepare_bill(self):
        bill_vals = {
            'ref': self.name or '',
            'move_type': 'in_invoice',
            'maintenance_request_id': self.id,
            'narration': self.name,
            'invoice_origin': self.name,
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
        }
        return bill_vals

    def action_create_invoice(self):
        invoice_vals = self._prepare_invoice()
        invoice_line_vals = self._prepare_maintenance_invoice_line()
        invoice_vals['invoice_line_ids'] = [[0, 0, invoice_line_vals]]
        invoice_id = self.env["account.move"].create(invoice_vals)
        self.customer_invoice_id = invoice_id.id
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        form_view = [(self.env.ref('account.view_move_form').id, 'form')]
        action['views'] = form_view
        action['res_id'] = invoice_id.id
        return action

    def action_view_invoices(self):
        invoices = self.mapped('account_move_ids')
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def _prepare_maintenance_invoice_line(self):
        self.ensure_one()
        if self.env.company.invoice_product_id:
            res = {
                'name': self.env.company.invoice_product_id.name,
                'product_id': self.env.company.invoice_product_id.id,
                'analytic_account_id': self.property_id.analytic_account.id,
                'quantity': 1,
                'price_unit': 1,
            }
            return res
        else:
            raise UserError(_("Please define maintenance invoicing product in settings!"))

    def _prepare_invoice(self):
        invoice_vals = {
            'ref': self.name or '',
            'move_type': 'out_invoice',
            'maintenance_request_id': self.id,
            'narration': self.name,
            'invoice_origin': self.name,
            'partner_id': self.requester_id.id,
            'invoice_line_ids': [],
        }
        return invoice_vals
