from odoo import models, fields


class StockLocation(models.Model):
    _inherit = "stock.location"

    def get_branch_id(self):
        print("................................................................................")
        branch_id = self.env["branch.branch"].sudo().search([("warehouse_id", "=", self.warehouse_id.id)], limit=1)
        return branch_id.id if branch_id else False
