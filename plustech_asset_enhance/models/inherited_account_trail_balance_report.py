# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models


class AccountChartOfAccountReportIn(models.AbstractModel):
    _inherit = "account.coa.report"

    filter_analytic = True
