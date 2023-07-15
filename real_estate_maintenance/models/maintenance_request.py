from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, date


class MaintenanceRequest(models.Model):
    _name = 'maintenance.request'
    _inherit = ['portal.mixin', 'mail.thread.cc',
                'mail.thread', 'mail.activity.mixin', 'rating.mixin']
    _mail_post_access = 'read'
    _description = 'Property Maintenance Request'

    @api.model
    def _default_operating_unit(self):
        return self.env.user.default_operating_unit_id

    MAINTENANCE_REQUEST_STATES = [
        ('new', 'New'),
        ('to_review', 'to Review'),
        ('review', 'Waiting Property Manager'),
        ('prop_manager', 'Waiting CEO'),
        ('ceo', 'CEO Approved'),
        ('confirm', 'Confirmed'),
        ('ongoing', 'In Progress'),
        ('closed', 'Closed'),
        ('refused', 'Refused')]
    INVOICING_STATES = [('on-company', 'On The Company'),
                        ('on-partner', 'On The Requester')]
    MAINTENANCE_TYPE = [('electric', 'Electric'), ('plumbing', 'Plumbing'),
                        ('wall', 'Wall'), ('ac', 'Air conditioning')]
    name = fields.Char()
    maintenance_responsible_id = fields.Many2one(
        "hr.employee", "Maintenance Responsible")
    property_id = fields.Many2one("product.product", string="Property")
    requester_id = fields.Many2one("res.partner")
    maintenance_request_expense_line_ids = fields.One2many(
        "maintenance.request.expense", "maintenance_request_id")
    maintenance_request_product_line_ids = fields.One2many(
        "maintenance.request.product", "maintenance_request_id")
    request_date = fields.Date(string="Request Date", default=fields.Date.today())
    visit_date = fields.Date(string="Visit Date")
    end_date = fields.Date(string="End Date", readonly=True)
    issue_type = fields.Many2one("maintenance.issue.type", "Issue Type")
    issue_description = fields.Text("Issue Description")
    refuse_reason = fields.Text("Refuse Reason")
    invoice_status = fields.Selection(INVOICING_STATES, "Invoicing Status")
    maintenance_type = fields.Selection(MAINTENANCE_TYPE, "Maintenace Type")
    maintenance_type_type = fields.Many2one('maintenance.type.type', "Maintenance Type")
    attachment_ids = fields.One2many('ir.attachment', compute='_compute_attachment_ids', string="Main Attachments",
                                     help="Attachments that don't come from a message.")
    company_id = fields.Many2one(
        'res.company', string="Company", required=True, default=lambda self: self.env.company)
    account_move_ids = fields.One2many("account.move", "maintenance_request_id")
    customer_invoice_id = fields.Many2one("account.move")
    rent_property_build_id = fields.Many2one("rent.property.build", string="Compound")
    stock_picking_ids = fields.One2many("stock.picking", "maintenance_request_id")
    stock_pickings_count = fields.Integer("Stock Pickings Count",
                                          compute="_compute_stock_pickings_count")
    account_moves_count = fields.Integer("Account Moves Count",compute="_compute_account_moves_count")
    maintenance_exp_invoice_count = fields.Integer("Expense Moves Count",compute="_compute_account_moves_count")
    maintenance_cus_invoice_count = fields.Integer("Customer Moves Count",compute="_compute_account_moves_count")
    state = fields.Selection(MAINTENANCE_REQUEST_STATES, "Status", default="new")
    active = fields.Boolean(default=True)
    purchase_requisition_ids = fields.One2many(
        "stock.request", "maintenance_request_id")
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
        string='Building',
        readonly=True,
    )
    unit_type = fields.Selection(
        [('commercial', 'Commercial'), ('residential', 'Residential')], 'Unit type')
    maintenance_categ = fields.Selection([
        ('preventive', 'Preventive Maintenance'),
        ('emergency', 'Emergency Maintenance'),
        ('periodic', 'Periodic Maintenance'),
        ('corrective', 'Corrective Maintenance'),
    ], 'Maintenance Category')
    invoicing_state = fields.Selection([
        ('no_invoice', 'Not Paid'),
        ('partially', 'Partially Invoicing'),
        ('fully', 'Fully Invoicing'),
    ], 'Invoicing State', compute="_invoicing_state_calculate")

    maintain_property_type = fields.Selection([
        ('unit', 'Unit'),
        ('property', 'Property'),
        ('building', 'Compound'),
    ], 'Maintained Property Type', default="unit")
    deadline = fields.Date('Deadline')
    pay_with_custody = fields.Boolean('Pay With Custody')
    journal_id = fields.Many2one('account.journal', string='Journal')
    exp_total = fields.Float('Items Total' ,compute="compute_exp_total")
    inv_total = fields.Float('Expense Total',compute="compute_inv_total")
    add_total = fields.Float('Additional Total')
    
    purchase_count = fields.Integer(
        string="Purchases count", compute="_compute_purchase_count", readonly=True
    )
    picking_count = fields.Integer(
        string="Pickings count", compute="_compute_picking_count", readonly=True
    )
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')

        
    def action_view_sale_order(self):
        return{
            'name': _('Sale Order'),
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain':[('id','=',self.sale_order_id.id)],
            # 'target': 'new',
            'type': 'ir.actions.act_window',

        }

    @api.depends('purchase_requisition_ids')
    def _compute_picking_count(self):
        for rec in self:
            picking_ids= rec.purchase_requisition_ids.mapped('picking_ids')
            rec.picking_count = len(picking_ids)



    @api.depends('purchase_requisition_ids')
    def _compute_purchase_count(self):
        for rec in self:
            purchase_order_ids= rec.purchase_requisition_ids.mapped('purchase_order_ids')
            agreement_ids_purchase_order_ids= rec.purchase_requisition_ids.agreement_ids.mapped('purchase_ids')
            rec.purchase_count = len(purchase_order_ids) + len(agreement_ids_purchase_order_ids) 

    @api.depends('purchase_requisition_ids')
    def compute_exp_total(self):
        for rec in self:
            purchase_order= rec.purchase_requisition_ids.mapped('purchase_order_ids')
            purchase_order = purchase_order.filtered(lambda po: po.state in ('done','purchase'))
            purchase_order_total= purchase_order.invoice_ids.mapped('amount_total')
            agreement_ids_purchase_order_ids= rec.purchase_requisition_ids.agreement_ids.purchase_ids.filtered(lambda po: po.state in ('done','purchase')).invoice_ids.mapped('amount_total')
            rec.exp_total = sum(purchase_order_total) + sum (agreement_ids_purchase_order_ids)

    @api.depends('maintenance_request_expense_line_ids')
    def compute_inv_total(self):
        for rec in self:
            total = 0
            inv_total = 0
            for line in rec.maintenance_request_expense_line_ids :
                tax_amount = 0
                total = line.price_unit * line.quantity
                for tax in line.tax_ids :
                    tax_amount += total * tax.amount /100
                total += tax_amount
                inv_total += total
            rec.inv_total = inv_total

    def action_view_purchase_order(self):
        action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_rfq")
        purchase_order_ids= self.purchase_requisition_ids.mapped('purchase_order_ids').filtered(lambda po: po.state in ('done','purchase')).ids
        agreement_ids_purchase_order_ids= self.purchase_requisition_ids.agreement_ids.mapped('purchase_ids').filtered(lambda po: po.state in ('done','purchase')).ids

        action["domain"] = ['|',("id", "in", purchase_order_ids),("id", "in", agreement_ids_purchase_order_ids)]
        return action

    def _invoicing_state_calculate(self):
        for rec in self:
            invoices = self.mapped('account_move_ids')
            due_amount = self.mapped('account_move_ids.amount_residual')
            total_amount = self.mapped('account_move_ids.amount_total')
            rec.invoicing_state = 'no_invoice'
            if due_amount == 0 :
                rec.invoicing_state = 'fully'
            if due_amount != 0 and total_amount > due_amount:
                rec.invoicing_state = 'partially'

    @api.onchange('property_rent_id')
    def _onchange_property_rent_id(self):
        domain = []
        if self.property_rent_id:
            domain = [('property_id', '=', self.property_rent_id.id)]
        return {'domain': {'property_id': domain}}
    
   

    @api.onchange('property_id')
    def _onchange_property_id(self):
        if self.property_id:
            self.property_rent_id = self.property_id.property_id
            self.operating_unit_id = self.property_id.property_id.property_address_area
            if self.property_id.unit_state == 'مؤجرة' :
                order = self.env['sale.order.line'].sudo().search([
                    ('product_id', '=', self.property_id.id)])
                order.mapped('order_id').filtered(lambda so: so.rental_status not in ('returned','cancel','draft'))
                if order :
                    self.requester_id = order[0].partner_id
                    self.sale_order_id = order[0].order_id

    def action_view_stock_pickings(self):
        action = self.env['ir.actions.act_window']._for_xml_id(
            'stock.action_picking_tree_all')
        picking_ids = self.purchase_requisition_ids.mapped('picking_ids')
        action['domain'] = [('id', 'in', picking_ids.ids)]
        return action

    def _compute_stock_pickings_count(self):
        for rec in self:
            rec.stock_pickings_count = len(rec.stock_picking_ids)

    def _compute_purchase_requisition_count(self):
        for rec in self:
            rec.purchase_requisition_count = len(rec.purchase_requisition_ids)

    def action_view_purchase_requisition(self):
        action = self.env['ir.actions.act_window']._for_xml_id(
            'stock_request.action_request_quantities_form')
        action['domain'] = [('maintenance_request_id', '=', self.id)]
        return action

    def _compute_account_moves_count(self):
        for rec in self:
            rec.account_moves_count = len(rec.account_move_ids)
            rec.maintenance_cus_invoice_count = len(rec.account_move_ids.filtered(lambda exl: exl.maintenance_cus_invoice == True))
            rec.maintenance_exp_invoice_count = len(rec.account_move_ids.filtered(lambda exl: exl.maintenance_exp_invoice == True))

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].sudo().get(
            'sequence.maintenance.request')
        if 'issue_type' in vals:
            vals.update({'invoice_status':
                         self.env["maintenance.issue.type"].browse(vals['issue_type']).invoice_status})
        res = super(MaintenanceRequest, self).create(vals)
        res._send_notification_email()
        return res

    def _send_notification_email(self):
        # for rec in self.company_id.maintenance_request_to_notify_user_id:
            print("################# _send_notification_email")
            if self.requester_id.email:
                mail_content = " مرحيا " + self.requester_id.name + \
                               " <br/> " + "<br/> " + \
                               "طلب صيانة جديد تم انشاءه"+"  (" + self.name + ")" + \
                               " <br/> " + \
                               "  الفرع: " + self.operating_unit_id.name + \
                               " العقار: " + self.property_rent_id.property_name + \
                               " <br/> " + \
                               " الوحدة: " + self.property_id.name + \
                               " <br/> " + \
                               "الرجاء تحديد الوقت المناسب للصيانة"+ \
                               " <br/> " + \
                               "  شكرا لك,"
                print("################# mail_content",mail_content)
                self.env['mail.mail'].create({
                    'subject': _('Maintenance Request -  (Ref %s)') % (self.name),
                    'author_id': self.env.user.partner_id.id,
                    'body_html': mail_content,
                    'email_to': self.requester_id.email,
                }).send()

    def _compute_attachment_ids(self):
        for maintenance_request in self:
            attachment_ids = self.env['ir.attachment'].sudo().search([('res_id', '=', maintenance_request.id),
                                                                      ('res_model', '=', 'maintenance.request')]).ids
            message_attachment_ids = maintenance_request.mapped(
                'message_ids.attachment_ids').ids
            maintenance_request.attachment_ids = [
                (6, 0, list(set(attachment_ids) - set(message_attachment_ids)))]

    def action_activity_feedback(self):
        activities = self.env['mail.activity'].search([
            ('res_model', '=', 'maintenance.request'),
            ('res_id', '=', self.id)])
        activities.sudo().action_feedback()

    def get_res_users(self, group_ext_id):
        user_ids = self.env['res.users']
        if self.state == 'to_review':
            user_ids += self.env.company.maintenance_request_to_notify_user_id
        user_ids += self.env.ref(group_ext_id).users
        return user_ids

    def action_to_review(self):
        self.action_activity_feedback()
        self.state = 'to_review'
        user_ids = self.get_res_users('real_estate_maintenance.group_maintenance_review')
        self._send_notification(self.id, '', user_ids)

    def action_review(self):
        self.action_activity_feedback()
        self.state = 'review'
        user_ids = self.get_res_users('real_estate_maintenance.group_maintenance_property_manager')
        self._send_notification(self.id, '', user_ids)

    def prop_manager(self):
        self.action_activity_feedback()
        self.state = 'prop_manager'
        user_ids = self.get_res_users('real_estate_maintenance.group_maintenance_ceo')
        self._send_notification(self.id, '', user_ids)

    def action_ceo(self):
        self.action_activity_feedback()
        self.state = 'ceo'
        user_ids = self.get_res_users('real_estate_maintenance.group_maintenance_confirm')
        self._send_notification(self.id, '', user_ids)

    def action_confirm(self):
        ctx = self.env.context
        self.action_activity_feedback()
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
                raise UserError(
                    _("Please add consumed products in order to create purchase requisition"))

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
        # self.create_bills()
        self.end_date = date.today()
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

    def _send_notification(self, res_id, note, user_ids):
        for user in user_ids :
            notification = {
                'activity_type_id': self.env.ref('real_estate_maintenance.real_estate_maintenance_activity').id,
                'res_id': res_id,
                'res_model_id': self.env['ir.model'].search([('model', '=', 'maintenance.request')], limit=1).id,
                'icon': 'fa-pencil-square-o',
                'date_deadline': fields.Date.today(),
                'user_id': user.id,
                'note': note
            }
            try:
                self.env['mail.activity'].create(notification)
            except:
                pass

    def create_bills(self):
        bill_vals = self._prepare_bill()
        for partner in self.maintenance_request_expense_line_ids.mapped('partner_id'):
            bill_vals.update({"partner_id": partner.id})
            if self.pay_with_custody :
                bill_vals.update({"pay_with_custody": True})
                bill_vals.update({"custody_journal_id": self.journal_id.id})
            bill_lines = []
            for line in self.maintenance_request_expense_line_ids.filtered(lambda exl: exl.partner_id.id == partner.id):
                bill_lines.append([0, 0, line._prepare_invoice_line()])
            bill_vals.update({"invoice_line_ids": bill_lines})
            print("##################3 bill_vals",bill_vals)
            self.env["account.move"].create(bill_vals)

    def get_delivery_picking_type(self):
        self.ensure_one()
        delivery_operation = self.env['stock.picking.type'].search(
            [('code', '=', 'outgoing')], limit=1)

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
            'location_dest_id': picking_type.default_location_dest_id.id
            or self.env.ref("stock.stock_location_customers").id,
        }
        return picking_vals

    def action_create_picking_new(self):
        for rec in self:
            location_ids = rec.maintenance_request_product_line_ids.mapped(
                'location_id')
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
            'maintenance_exp_invoice': True,
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
        action = self.env["ir.actions.actions"]._for_xml_id(
            "account.action_move_out_invoice_type")
        form_view = [(self.env.ref('account.view_move_form').id, 'form')]
        action['views'] = form_view
        action['res_id'] = invoice_id.id
        return action

    def action_view_invoices(self):
        invoices = self.mapped('account_move_ids')
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        action['domain'] = [('id', 'in', invoices.ids),('maintenance_exp_invoice', '=', True)]
        return action
    
    def action_view_customer_invoices(self):
        invoices = self.mapped('account_move_ids')
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        action['domain'] = [('id', 'in', invoices.ids),('maintenance_cus_invoice', '=', True)]
        return action

    def _prepare_maintenance_invoice_line(self):
        self.ensure_one()
        if self.env.company.invoice_product_id:
            res = {
                'name': self.env.company.invoice_product_id.name,
                'product_id': self.env.company.invoice_product_id.id,
                'analytic_account_id': self.property_id.analytic_account.id or self.property_rent_id.analytic_account.id,
                'quantity': 1,
                'price_unit': self.inv_total + self.exp_total + self.add_total,
            }
            print("#@################### res res res",self)
            print("#@################### res res self.property_id",self.property_id)
            print("#@################### res res res",res)
            return res
        
        else:
            raise UserError(
                _("Please define maintenance invoicing product in settings!"))

    def _prepare_invoice(self):
        invoice_vals = {
            'ref': self.name or '',
            'move_type': 'out_invoice',
            'maintenance_cus_invoice': True,
            'maintenance_request_id': self.id,
            'narration': self.name,
            'invoice_origin': self.name,
            'partner_id': self.requester_id.id,
            'invoice_line_ids': [],
        }
        return invoice_vals
