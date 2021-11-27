# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta

class QRCodeInvoice(models.Model):
    @api.model
    def _get_default_invoice__date(self):
        current_date = datetime.now()

        return current_date


    _inherit = 'account.move'

    invoice_date = fields.Datetime(readonly = True, states = {'draft': [('readonly', False)]},index=True,
                                   help="Keep empty to use the current date",copy =False,
                                   default=_get_default_invoice__date)
    invoice_date_due = fields.Datetime(readonly = True, states = {'draft': [('readonly', False)]},index=True,help="Keep empty to use the current date",copy =False)

