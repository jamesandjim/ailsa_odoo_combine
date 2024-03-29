# -*- coding: utf-8 -*-

from odoo import api, models
from odoo.osv import expression

DEFAULT_INVOICED_TIMESHEET = 'all'


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _timesheet_compute_delivered_quantity_domain(self):
        domain = super(SaleOrderLine, self)._timesheet_compute_delivered_quantity_domain()
        # force to use only the validated timesheet
        param_invoiced_timesheet = self.env['ir.config_parameter'].sudo().get_param('sale.invoiced_timesheet', DEFAULT_INVOICED_TIMESHEET)
        if param_invoiced_timesheet == 'approved':
            domain = expression.AND([domain, [('validated', '=', True)]])
        return domain
